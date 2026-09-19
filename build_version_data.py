"""
Builds the compact per-version data packages that the item inspector loads at runtime, so the
full in-game files (assets.xml ~35-100 MB, 12 x texts_*.xml ~5 MB each) no longer need to ship.

For every game version this writes data/versions/<version>/:
    items.csv           - the extractor output (extract_assets_resolve_pools_buffs_conditions_sources.py)
    assets_index.json   - only the asset facts the app looks up (names, icons, inheritance, pools, regions ...)
    loca/<language>.json- only the localization lines the app can ask for
    export_assets.json  - raw XML of every item (+ its buff assets) for the right-click "export item XML"
and refreshes data/versions/versions.json, which feeds the "Game Version" dropdown.

Usage:
    py build_version_data.py --current                      # this project's data/base/... (label taken from _version.py)
    py build_version_data.py --version 2.0 --src game_versions/2.0
    py build_version_data.py --all                          # current + every folder in game_versions/

The "relevant" set is a closure: every number found in the items CSV and in the inspector script(s)
(hardcoded OasisIDs / GUIDs) plus everything reachable from those GUIDs (inheritance parents, asset
pool members). Anything the app can look up at runtime starts from one of those.
"""
import argparse
import csv
import glob
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import extract_assets_resolve_pools_buffs_conditions_sources as extractor

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSIONS_DIR = os.path.join(ROOT, "data", "versions")
HISTORY_DIR = os.path.join(ROOT, "game_versions")
ASSETS_REL = os.path.join("data", "base", "config", "export", "assets.xml")
GUI_REL = os.path.join("data", "base", "config", "gui")

NUMBER = re.compile(r'-?\d+')

# Same paths export_selected_item_xml() used to walk on the full asset tree.
EXPORT_RELATED_PATHS = [
    './Values/Item/Buff',
    './/Buffs/Item/GUID',
    './/BoostBuffs/Item/GUID',
    './Values/Item/EffectTargetGuid',
    './Values/Item/EffectTargets/Item/GUID',
]


def version_key(v):
    return tuple(int(p) for p in re.findall(r'\d+', v))


def current_version_label():
    with open(os.path.join(ROOT, "_version.py"), encoding="utf-8") as f:
        m = re.search(r"__VERSION__\s*=\s*'(\d+)\.(\d+)", f.read())
    return f"{m.group(1)}.{m.group(2)}"


def harvest_numbers(text, guids, oasis_ids):
    for tok in NUMBER.findall(text):
        digits = tok.lstrip('-')
        if len(digits) >= 15:
            oasis_ids.add(tok)
        elif not tok.startswith('-') and 1 <= len(digits) <= 9:
            guids.add(tok)


def index_assets(assets_path):
    root = ET.parse(assets_path).getroot()
    idx = {"loca": {}, "icon": {}, "base": {}, "region": {}, "first": {}, "members": {}}
    embankment_pairs = {}
    elements = {}

    for asset in root.iter('Asset'):
        guid_node = asset.find('./Values/Standard/GUID')
        if guid_node is None or not guid_node.text:
            continue
        guid = guid_node.text.strip()
        elements[guid] = asset

        oasis_node = asset.find('./Values/Text/OasisId')
        if oasis_node is not None and oasis_node.text:
            idx["loca"][guid] = oasis_node.text.strip()
        quest_name_node = asset.find('./Values/QuestEntry/QuestName')
        if quest_name_node is not None and quest_name_node.text:
            idx["loca"][guid] = quest_name_node.text.strip()

        base_node = asset.find('./BaseAssetGUID')
        if base_node is not None and base_node.text:
            idx["base"][guid] = base_node.text.strip()

        icon_node = asset.find('./Values/Standard/IconFilename')
        if icon_node is not None and icon_node.text:
            idx["icon"][guid] = icon_node.text.strip()

        region_node = asset.find('./Values/Building/AssociatedRegions')
        if region_node is not None and region_node.text:
            idx["region"][guid] = region_node.text.strip()

        embankment_node = asset.find('./Values/Building/EmbankmentReplacement')
        if embankment_node is not None and embankment_node.text:
            terrain2_node = asset.find('./Values/Building/TerrainType2')
            terrain2 = terrain2_node.text.strip() if terrain2_node is not None and terrain2_node.text else None
            embankment_pairs[guid] = (embankment_node.text.strip(), terrain2)

        template_node = asset.find('./Template')
        template = template_node.text.strip() if template_node is not None and template_node.text else ""
        if template == "AssetPoolNamed":
            child = asset.find('./Values/AssetPool/AssetList/Item/Asset')
            if child is not None and child.text:
                idx["first"][guid] = child.text.strip()
        if template in ("AssetPool", "AssetPoolNamed"):
            members = [a.text.strip() for a in asset.findall('./Values/AssetPool/AssetList/Item/Asset') if a.text]
            if members:
                idx["members"][guid] = members

    # Land/Floodplain pairs: "" = plain Aegyptus side, "Floodplain" = the riverside variant.
    farm = {}
    for guid, (partner, terrain2) in embankment_pairs.items():
        if terrain2 == "NormalLand":
            farm[guid] = ""
        elif terrain2 == "Embankment":
            farm[guid] = "Floodplain"
        else:
            partner_terrain2 = embankment_pairs.get(partner, (None, None))[1]
            if partner_terrain2 == "Embankment":
                farm[guid] = ""
            elif partner_terrain2 == "NormalLand":
                farm[guid] = "Floodplain"
    idx["farm"] = farm
    return idx, elements


def relevant_guids(seed_guids, idx):
    needed = set()
    stack = list(seed_guids)
    while stack:
        g = stack.pop()
        if g in needed:
            continue
        needed.add(g)
        parent = idx["base"].get(g)
        if parent:
            stack.append(parent)
        first = idx["first"].get(g)
        if first:
            stack.append(first)
        stack.extend(idx["members"].get(g, ()))
    return needed


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def read_loca_file(path):
    out = {}
    for text_container in ET.parse(path).getroot().findall('.//Text'):
        line_id = text_container.find('LineId')
        val = text_container.find('Text')
        if line_id is not None and val is not None and line_id.text:
            out[line_id.text.strip()] = val.text if val.text else ""
    return out


def build_export_assets(csv_rows, elements):
    assets, related = {}, {}
    for row in csv_rows:
        item_guid = row["GUID"].strip()
        item_asset = elements.get(item_guid)
        if item_asset is None:
            continue
        rel = []
        for path in EXPORT_RELATED_PATHS:
            for node in item_asset.findall(path):
                if node.text and node.text.strip().replace('-', '').isdigit():
                    rel.append(node.text.strip())
        rel = [g for g in dict.fromkeys(rel) if g in elements]
        related[item_guid] = rel
        for g in [item_guid] + rel:
            if g not in assets:
                el = elements[g]
                el.tail = None
                assets[g] = ET.tostring(el, encoding="unicode")
    return {"assets": assets, "related": related}


def update_manifest():
    versions = sorted(
        (d for d in os.listdir(VERSIONS_DIR) if os.path.isfile(os.path.join(VERSIONS_DIR, d, "items.csv"))),
        key=version_key,
    )
    write_json(os.path.join(VERSIONS_DIR, "versions.json"), {"versions": versions, "latest": versions[-1]})
    return versions


def build_version(version, src_root, scan_extra):
    assets_path = os.path.join(src_root, ASSETS_REL)
    gui_dir = os.path.join(src_root, GUI_REL)
    out_dir = os.path.join(VERSIONS_DIR, version)
    os.makedirs(out_dir, exist_ok=True)
    print(f"=== Building version {version} from {src_root}")

    csv_path = os.path.join(out_dir, "items.csv")
    extractor.extract_xml_to_csv(assets_path, csv_path)

    seed_guids, oasis_ids = set(), set()
    with open(csv_path, encoding="utf-8") as f:
        csv_text = f.read()
    harvest_numbers(csv_text, seed_guids, oasis_ids)
    scripts = glob.glob(os.path.join(ROOT, "anno117_item_inspector*.py")) + list(scan_extra)
    for script in scripts:
        with open(script, encoding="utf-8") as f:
            harvest_numbers(f.read(), seed_guids, oasis_ids)

    idx, elements = index_assets(assets_path)
    needed = relevant_guids(seed_guids, idx)

    slim = {}
    for key in ("loca", "icon", "base", "region", "first", "members", "farm"):
        slim[key] = {g: v for g, v in idx[key].items() if g in needed}
    for g, oid in slim["loca"].items():
        oasis_ids.add(oid)
    write_json(os.path.join(out_dir, "assets_index.json"), slim)

    for loca_path in sorted(glob.glob(os.path.join(gui_dir, "texts_*.xml"))):
        language = os.path.basename(loca_path)[len("texts_"):-len(".xml")]
        full = read_loca_file(loca_path)
        write_json(os.path.join(out_dir, "loca", f"{language}.json"), {i: full[i] for i in sorted(oasis_ids) if i in full})

    with open(csv_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    write_json(os.path.join(out_dir, "export_assets.json"), build_export_assets(rows, elements))

    size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(out_dir) for fn in fns)
    print(f"    {len(rows)} items, {len(slim['loca'])} named assets, {len(oasis_ids)} loca ids, package {size / 1024 / 1024:.1f} MB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--current", action="store_true", help="build this project's own data/base files")
    ap.add_argument("--all", action="store_true", help="build current + every game_versions/<version>")
    ap.add_argument("--version", help="version label for --src")
    ap.add_argument("--src", help="folder containing data/base/config/{export,gui}")
    ap.add_argument("--scan-extra", action="append", default=[], help="additional script(s) to harvest hardcoded IDs from")
    args = ap.parse_args()

    if args.all:
        cmds = [["--current"]]
        for d in sorted(os.listdir(HISTORY_DIR), key=version_key):
            cmds.append(["--version", d, "--src", os.path.join(HISTORY_DIR, d)])
        for c in cmds:
            extra = [a for e in args.scan_extra for a in ("--scan-extra", e)]
            subprocess.run([sys.executable, os.path.abspath(__file__)] + c + extra, check=True)
    elif args.current:
        build_version(current_version_label(), ROOT, args.scan_extra)
    elif args.version and args.src:
        build_version(args.version, os.path.abspath(args.src), args.scan_extra)
    else:
        ap.error("use --current, --all, or --version + --src")

    print("Versions available:", ", ".join(update_manifest()))


if __name__ == "__main__":
    main()
