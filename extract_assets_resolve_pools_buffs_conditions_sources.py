import xml.etree.ElementTree as ET
import csv
import os

# --- Configuration for Buff Parsing ---
UPGRADE_PARENTS = [
    "ResidenceUpgrade", "FactoryUpgrade", "ModuleOwnerUpgrade",
    "MaintenanceUpgrade", "CityInstitutionUpgrade", "IncidentInfectableUpgrade",
    "RecruitmentUpgrade", "AqueductUpgrade", "WarehouseUpgrade",
    "IrrigationUpgrade", "HealthUpgrade", "VehicleUpgrade",
    "TradeShipUpgrade", "MovementUpgrade", "UnitUpgrade",
    "ItemContainerUpgrade", "SellableUpgrade", "BuildingUpgrade", "MetaUnitBuff", "RepairCraneUpgrade", "MetaEconomyBuff", "AreaPassiveTradeUpgrade", "AreaMaintenanceUpgrade", "AreaFestivalAttributeUpgrade"
]

ATTRIBUTES_OF_INTEREST = [
    "Population", "Money", "Happiness", "Health",
    "FireSafety", "Belief", "Knowledge", "Prestige"
]

PERCENT_OVERRIDE_TAGS = [
    "BuffBaseSpeedUpgrade", "BuffReduceNegativeWindImpactUpgrade",
    "BuffTransferSpeedUpgrade", "BuffReduceDamageImpactUpgrade",
    "BuffReduceCargoImpactUpgrade", "AccuracyCatapultModuleUpgrage",
    "AccuracyArcherModuleUpgrade", "AccuracyBallistaModuleUpgrage",
    "AccuracyUpgrade", "ProductivityUpgrade"
]

# NEW: Blacklist for Source Logic
BLACKLIST_ROOTS = {"43037", "82598", "83484"}

def get_text_safe(element, tag, default="0"):
    """Helper to extract text from a child tag safely."""
    if element is None:
        return default
    child = element.find(tag)
    return child.text if child is not None else default

# --- NEW: Source Extraction Logic ---

def build_extended_source_maps(assets_map):
    """
    Builds indices for RewardPools, Rivals, and Quests.
    Uses a broad text-based reverse lookup to find quest parents.
    """
    child_to_parents = {}
    reward_pool_guids = set()
    public_refs = set()
    rival_rewards = {}
    quest_item_map = {}

    # Identify all Quest-related templates that might need climbing
    QUEST_TEMPLATES = {'Sequence', 'Decision', 'StateChecker', 'SequenceCharNotif', 'GoToObjectiveComponent', 'DecisionRoot', 'Function', 'Objective'}
    quest_related_guids = set()

    for guid, asset in assets_map.items():
        tpl_node = asset.find('Template')
        tpl = tpl_node.text if tpl_node is not None else ""
        if tpl == "RewardPool":
            reward_pool_guids.add(guid)
        if tpl in QUEST_TEMPLATES:
            quest_related_guids.add(guid)

    # REVERSE MAP: child_guid -> list of parent_guids
    # Now scans ALL text nodes in an asset to find references to quest-related GUIDs
    guid_to_any_container_parents = {}

    for guid, asset in assets_map.items():
        # Optimization: Get all text once
        all_text_values = {t.strip() for t in asset.itertext() if t and t.strip()}

        for val in all_text_values:
            # If this asset contains a Quest-related GUID, mark this asset as a parent
            if val in quest_related_guids and val != guid:
                if val not in guid_to_any_container_parents:
                    guid_to_any_container_parents[val] = []
                guid_to_any_container_parents[val].append(guid)

    # Pass 2: Source Logic
    for guid, asset in assets_map.items():
        tpl_node = asset.find('Template')
        tpl = tpl_node.text if tpl_node is not None else ""
        is_pool = (tpl == "RewardPool")

        # 1. RewardPool Orphan Filter
        for text_node in asset.itertext():
            val = text_node.strip()
            if val in reward_pool_guids and not is_pool:
                public_refs.add(val)

        # 2. Defeated Rivals
        defeated_item = asset.find('.//Participant/ItemGainedWhenDefeated')
        if defeated_item is not None and defeated_item.text:
            item_id = defeated_item.text.strip()
            if item_id not in rival_rewards: rival_rewards[item_id] = []
            rival_rewards[item_id].append(guid)

        # 3. Quests with Broad Climbing
        if tpl in ['Decision', 'Sequence', 'Objective', 'SequenceCharNotif', 'GoToObjectiveComponent']:
            for text_node in asset.itertext():
                val = text_node.strip()
                if val in assets_map:
                    item_asset = assets_map[val]
                    item_tpl = item_asset.find('Template')
                    if item_tpl is not None and item_tpl.text in ['Item', 'ItemWithBoost']:

                        quest_info = None
                        if tpl == 'Decision':
                            # Prefer Headline for Decisions if available
                            headline = asset.find('.//Decision/DecisionScreenConfig/Headline')
                            if headline is not None and headline.text:
                                quest_info = f"Quest: {headline.text.strip()}"

                        # If not a Decision with a headline, or if it's Sequence/Objective, climb the tree
                        if not quest_info:
                            linked_content = find_linked_quest_content(guid, assets_map, guid_to_any_container_parents)
                            if linked_content:
                                quest_info = f"Quest: {linked_content}"

                        if quest_info:
                            if val not in quest_item_map: quest_item_map[val] = set()
                            quest_item_map[val].add(quest_info)

        # 4. RewardPool Hierarchy
        if is_pool:
            items_pool = asset.find('.//ItemsPool')
            if items_pool is not None:
                items = items_pool.findall('Item')
                total_weight = sum(int(get_text_safe(i, 'Weight', "1")) for i in items)
                if total_weight > 0:
                    for item in items:
                        child_guid = get_text_safe(item, 'ItemLink', None)
                        if child_guid:
                            weight = int(get_text_safe(item, 'Weight', "1"))
                            if weight > 0:
                                prob = weight / total_weight
                                if child_guid not in child_to_parents: child_to_parents[child_guid] = []
                                child_to_parents[child_guid].append((guid, prob))

    return child_to_parents, public_refs, rival_rewards, quest_item_map

def find_linked_quest_content(current_guid, assets_map, guid_to_any_container_parents, visited=None):
    """
    Climbs the tree based on broad text references.
    Stops at any asset containing <LinkedQuestEntry>.
    """
    if visited is None: visited = set()
    if current_guid in visited or current_guid not in assets_map:
        return None
    visited.add(current_guid)

    asset = assets_map[current_guid]

    # Search for the container
    linked_entry = asset.find('.//LinkedQuestEntry')
    if linked_entry is not None and linked_entry.text:
        return linked_entry.text.strip()

    # Broad search for parents (assets that mention this GUID in any tag)
    parents = guid_to_any_container_parents.get(current_guid, [])
    for p_guid in parents:
        result = find_linked_quest_content(p_guid, assets_map, guid_to_any_container_parents, visited)
        if result:
            return result

    return None

def find_root_sources(current_guid, current_prob, child_to_parents, public_refs, roots_found, visited):
    """
    Recursive climb.
    If a node is in 'public_refs', it is recorded as a source.
    We also continue climbing because a pool can be both a root AND a child.
    """
    if current_guid in visited or current_prob <= 0:
        return
    visited.add(current_guid)

    # 1. Capture the pool if it's a functional entry point (Quest, Trader, etc.)
    if current_guid in public_refs:
        if current_guid not in BLACKLIST_ROOTS:
            roots_found[current_guid] = roots_found.get(current_guid, 0.0) + current_prob
        # NOTE: We do NOT 'return' here. We keep climbing to find higher parents.

    # 2. Continue climbing the tree
    parents = child_to_parents.get(current_guid, [])
    for parent_guid, link_prob in parents:
        find_root_sources(parent_guid, current_prob * link_prob, child_to_parents, public_refs, roots_found, visited.copy())


def get_combined_source_value(item_guid, asset, child_to_parents, public_refs, rival_rewards, quest_item_map):
    """Aggregates all source data (Pools, Rivals, Hall of Fame, Quests) into the cell string."""
    sources = []

    # 1. Reward Pools (Recursive climb)
    roots_found = {}
    find_root_sources(item_guid, 1.0, child_to_parents, public_refs, roots_found, set())
    for guid, prob in roots_found.items():
        if prob > 0:
            sources.append(f"{guid} [{prob:.3%}]")

    # 2. Defeated Rivals
    if item_guid in rival_rewards:
        for rival_guid in rival_rewards[item_guid]:
            sources.append(f"ItemGainedWhenDefeated: {rival_guid}")

    # 3. Hall of Fame (IsMetaItem check)
    item_vals = asset.find('Values/Item')
    # Updated to print the specific ID string requested
    if item_vals is not None and get_text_safe(item_vals, 'IsMetaItem') == '1':
        sources.append("HallofFame: -6906945524005841361")

    # 4. Quests
    if item_guid in quest_item_map:
        sources.extend(list(quest_item_map[item_guid]))

    return " | ".join(sorted(sources))

# --- End New Source Logic ---

def parse_value_node(node):
    """Parses a node for values, handling percentages, signs, and specific offsets."""
    if node is None: return None
    tag_name = node.tag

    # Handle Item lists
    item_child = node.find("Item")
    if item_child is not None:
        for sub_node in item_child:
            if sub_node.text:
                return sub_node.text.strip()
        return None

    target_node = node.find("AmountOrPercent") if node.find("AmountOrPercent") is not None else node
    val_child = target_node.find("Value")

    raw_val = None
    if val_child is not None:
        raw_val = val_child.text
    elif len(node) == 0 and node.text is not None:
        raw_val = node.text.strip()

    if raw_val is not None:
        try:
            val_num = float(raw_val)

            # 1. ActiveTradePriceInPercent: value in assets is already the direct percent, no offset needed

            # 2. Reduction Tags (Force '-' for positive values)
            REDUCTION_TAGS = [
                "BuffReduceCargoImpactUpgrade",
                "BuffReduceDamageImpactUpgrade",
                "BuffReduceNegativeWindImpactUpgrade"
            ]

            # 3. CLEAN FORMATTING: Remove .0 from integers
            val_fmt = str(int(val_num)) if val_num.is_integer() else str(val_num)

            # Tags whose value is a GUID reference — never prepend a sign
            GUID_VALUE_TAGS = ["AddedFertility"]

            if tag_name in REDUCTION_TAGS and val_num > 0:
                final_val = f"-{val_fmt}"
            elif tag_name in GUID_VALUE_TAGS:
                final_val = val_fmt  # raw number, no sign
            else:
                # 4. Workforce & others get '+' prefix
                final_val = f"+{val_fmt}" if val_num > 0 else val_fmt

        except (ValueError, TypeError):
            final_val = raw_val

        # 5. Percentage Detection
        PERCENT_LOOKUP = [
            "WorkforceModifierInPercent", "FuelDurationPercent",
            "ActiveTradePriceInPercent", "ConstructionCostInPercent",
            "ConstructionSpeedInPercent", "RecruitmentSpeedInPercent",
            "RecruitmentCostInPercent"
        ]

        is_percent = get_text_safe(target_node, "Percental", "0") == "1"
        if any(x in tag_name for x in ["percent", "Percent"]) or tag_name in PERCENT_OVERRIDE_TAGS or tag_name in PERCENT_LOOKUP:
            is_percent = True

        return f"{final_val}%" if is_percent else str(final_val)

    return None

def resolve_matcher_guid(matcher_guid, assets_map):
    """Resolves a Matcher GUID into its specific criteria strings using pipe syntax."""
    if matcher_guid not in assets_map:
        return f"Matcher | {matcher_guid}"

    asset = assets_map[matcher_guid]
    criteria_root = asset.find(".//Matcher/Criterion")
    if criteria_root is None:
        return ""

    results = []
    values_node = criteria_root.find("Values")
    if values_node is None:
        return ""

    for criterion_data in values_node:
        tag = criterion_data.tag
        if tag == "MatcherCriterion":
            continue

        for detail in criterion_data:
            d_tag = detail.tag
            d_val = detail.text.strip() if detail.text else ""

            # Check for inner GUIDs (e.g., ShipConfiguration)
            guid_check = detail.find("GUID")
            if guid_check is not None:
                # Use Pipe instead of Colon as requested
                results.append(f"{tag} | {guid_check.text.strip()}")
            elif d_val and d_val != "0":
                results.append(f"{d_tag} | {d_val}")

    return " | ".join(results)

def parse_condition_node(cond_node, assets_map):
    """Parses a specific <Condition> XML node with updated syntax and Matcher resolution."""
    if cond_node is None: return ""

    template = get_text_safe(cond_node, "Template", "Unknown")
    values_node = cond_node.find("Values")
    if values_node is None: return template

    data_node = values_node.find(template)
    if data_node is None and template == "ConditionMonumentEventActive":
        data_node = values_node.find("ConditionMonumentEventsActive")
    if data_node is None:
        data_node = values_node

    # 1. Operator Logic
    op = get_text_safe(data_node, "ComparisonOp", "0")
    if op == "0": op = get_text_safe(data_node, "ComparisonOpType", "0")

    AT_LEAST_TEMPLATES = ["ConditionObjectCount", "ConditionNeedAttributeCounter", "ConditionItemUsed", "ConditionPlayerCounter", "ConditionInStorage", "ConditionTradeRouteCount"]
    if (op == "0" or not op) and template in AT_LEAST_TEMPLATES:
        op = "AtLeast"
    elif op == "0":
        op = ""

    # 2. Value Extraction Logic
    val_str = ""

    if template == "ConditionNeedAttributeCounter":
        amt = get_text_safe(data_node, "NeedAttributeAmount")
        kind = get_text_safe(data_node, "NeedAttributeType", "Population")
        val_str = f"{kind} {op} {amt}".strip()
        op = ""

    elif template == "ConditionPlayerCounter":
        amt = get_text_safe(data_node, "CounterAmount")
        ctr = get_text_safe(data_node, "PlayerCounter", "")
        if ctr == "0": ctr = ""
        ctx = get_text_safe(data_node, "Context", "0")
        val_str = f"{ctr} {op} {amt}".strip()
        if ctx != "0": val_str += f" | {ctx}"
        op = ""

    elif template == "ConditionObjectCount":
        val_str = get_text_safe(data_node, "Amount")

    elif template == "ConditionItemUsed":
        amt = get_text_safe(data_node, 'ItemAmount')
        target = get_text_safe(data_node, 'TargetItem')
        # Use Pipe before GUID as requested
        val_str = f"{amt} | {target}"

    elif template == "ConditionInStorage":
        items = [f"{get_text_safe(i, 'Amount')} | {get_text_safe(i, 'Product')}" for i in data_node.findall(".//Item")]
        val_str = ", ".join(items)

    elif "ConditionMonumentEvent" in template:
        mon_node = data_node.find("MonumentEventsActive")
        if mon_node is None: mon_node = data_node
        val_str = ", ".join([get_text_safe(i, "MonumentEventGUID") for i in mon_node.findall("Item")])

    elif template == "ConditionTradeRouteCount":
        val_str = get_text_safe(data_node, "TradeRouteCount")

    elif template == "ConditionActiveEmperor":
        val_str = get_text_safe(data_node, "EmperorParticipant")

    elif template == "ConditionReligion":
        val_str = get_text_safe(data_node, "ReligionAsset")

    elif template == "ConditionEmperorRelation":
        val_str = get_text_safe(data_node, "AllowedZones", "0")
        if val_str == "0": val_str = get_text_safe(data_node, "AllowedSpecialStates")

    elif template == "ConditionWarState":
        val_str = get_text_safe(data_node, "WarStates")

    elif template == "ConditionDominantPatron":
        val_str = get_text_safe(data_node, "PatronGUID")

    elif template == "ConditionDiplomacyState":
        state = get_text_safe(data_node, "DesiredState", "War")
        if state == "0": state = "War"
        val_str = f"{state} | {get_text_safe(data_node, 'Profile2')}"

    op_str = f"{op} " if op else ""
    scope = get_text_safe(data_node, "CounterScope", "0")
    scope_str = f" | {scope}" if scope != "0" else ""

    # 4. Object Filter & Matcher (using resolved pipe syntax)
    filter_parts = []
    obj_filter = values_node.find("ObjectFilter")
    if obj_filter is not None:
        f_guid = get_text_safe(obj_filter, "ObjectGUID", "0")
        f_matcher = get_text_safe(obj_filter, "Matcher", "0")
        if f_guid != "0": filter_parts.append(f"{f_guid}")
        if f_matcher != "0":
            filter_parts.append(resolve_matcher_guid(f_matcher, assets_map))

    filter_str = (" | " + " | ".join(filter_parts)) if filter_parts else ""

    return f"{template}: {op_str}{val_str}{scope_str}{filter_str}".strip()

def resolve_boost_condition(guid, assets_map):
    """Parses BoostCondition assets from the map by GUID."""
    if guid not in assets_map:
        return f"Unknown Condition {guid}"

    asset = assets_map[guid]
    # Standard path for separate assets: Values/BoostCondition/PreConditionList/Condition
    cond_node = asset.find(".//Values/BoostCondition/PreConditionList/Condition")
    return parse_condition_node(cond_node, assets_map)

def resolve_single_buff_asset(asset_node, assets_map, visited_guids, prefix=""):
    """Extracts effects from an asset, including ReplaceWorkforce logic."""
    extracted_effects = []
    values_node = asset_node.find("Values")
    if values_node is None: return extracted_effects

    guid_node = values_node.find("./Standard/GUID")
    current_guid = guid_node.text.strip() if guid_node is not None else None
    if current_guid:
        if current_guid in visited_guids: return []
        visited_guids.add(current_guid)

    for parent_tag in UPGRADE_PARENTS:
        parent_node = values_node.find(parent_tag)
        if parent_node is None: continue

        if parent_tag == "MaintenanceUpgrade":
            replace_node = parent_node.find("ReplaceWorkforce")
            if replace_node is not None:
                new_workforce = get_text_safe(replace_node, "NewWorkforce", None)
                if new_workforce:
                    extracted_effects.append(f"{prefix}ReplaceWorkforce: {new_workforce}")

        # Build tag set ONCE before the loop
        effect_tags_present = {node.tag for node in parent_node}

        for effect_node in parent_node:
            effect_name = effect_node.tag

            if effect_name == "ReplaceWorkforce":
                continue

            if effect_name == "AdditionalFunctionalEffect":
                intermediate_guid = effect_node.text.strip() if effect_node.text else ""
                if intermediate_guid in assets_map:
                    intermediate_asset = assets_map[intermediate_guid]
                    buffs_list_node = intermediate_asset.find(".//Effect/Buffs")
                    if buffs_list_node is not None:
                        for item in buffs_list_node.findall("Item"):
                            actual_buff_guid = get_text_safe(item, "GUID", None)
                            if actual_buff_guid and actual_buff_guid in assets_map:
                                sub_effects = resolve_single_buff_asset(
                                    assets_map[actual_buff_guid],
                                    assets_map,
                                    set(visited_guids),
                                    prefix="-6916464905928465879 "
                                )
                                extracted_effects.extend(sub_effects)
                continue

            if effect_name == "AdditionalOutput":
                for item in effect_node.findall("Item"):
                    force = get_text_safe(item, "ForceProductSameAsFactoryOutput", "0")
                    cycle = get_text_safe(item, "AdditionalOutputCycle", "1")
                    amount = get_text_safe(item, "Amount", "1")
                    if force == "1":
                        extracted_effects.append(f"{prefix}AdditionalOutput: {amount}/{cycle}")
                    else:
                        product = get_text_safe(item, "Product", "0")
                        extracted_effects.append(f"{prefix}AdditionalOutput: {product} {amount}/{cycle}")
                continue

            if effect_name == "NeedProvidedNeedAttributes":
                target_node = effect_node.find("ChangeNeedAttributesOf")
                target_guids = []
                if target_node is not None:
                    items = target_node.findall("Item")
                    if items:
                        for item in items:
                            prod = get_text_safe(item, "ProvidedProduct", None)
                            if prod: target_guids.append(prod)
                    else:
                        val = parse_value_node(target_node)
                        if val: target_guids.append(val)

                attrib_node = effect_node.find("AdditionalNeedAttributes")
                if target_guids and attrib_node is not None:
                    for target_guid in target_guids:
                        for attr in ATTRIBUTES_OF_INTEREST:
                            attr_val_node = attrib_node.find(attr)
                            if attr_val_node is not None:
                                val_str = parse_value_node(attr_val_node)
                                if val_str:
                                    extracted_effects.append(f"{prefix}ChangeNeedAttributesOf {target_guid}: {attr} {val_str}")

            elif effect_name == "AdditionalAttributes":
                for attr in ATTRIBUTES_OF_INTEREST:
                    attr_node = effect_node.find(attr)
                    if attr_node is not None:
                        val_str = parse_value_node(attr_node)
                        if val_str: extracted_effects.append(f"{prefix}{attr}: {val_str}")
            else:
                val_str = parse_value_node(effect_node)
                if val_str: extracted_effects.append(f"{prefix}{effect_name}: {val_str}")

        # if AddedFertility exists but FertilityPercent is absent, default it
        if "AddedFertility" in effect_tags_present and "FertilityPercent" not in effect_tags_present:
            extracted_effects.append(f"{prefix}FertilityPercent: +100%")

    return extracted_effects

def get_full_buff_description(guid, assets_map):
    """Helper to fetch and join effects for a GUID."""
    if guid not in assets_map:
        return f"Unknown GUID ({guid})"
    effects = resolve_single_buff_asset(assets_map[guid], assets_map, set())
    return " | ".join(effects) if effects else ""

# --- Main Extraction Script ---
def extract_xml_to_csv(xml_file_path, csv_file_path):
    if not os.path.exists(xml_file_path):
        print(f"Error: {xml_file_path} not found.")
        return

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    assets_map = {}
    asset_pools = {}
    inheritance_map = {}
    assets = root.findall('.//Asset')

    for asset in assets:
        guid_node = asset.find('./Values/Standard/GUID')
        if guid_node is None: continue
        guid = guid_node.text.strip()
        assets_map[guid] = asset

        template = asset.find('Template')
        if template is not None and template.text in ['AssetPoolNamed', 'AssetPool']:
            asset_list = asset.find('./Values/AssetPool/AssetList')
            if asset_list is not None:
                asset_pools[guid] = [item.find('Asset').text.strip() for item in asset_list.findall('Item') if item.find('Asset') is not None]

        base_asset = asset.find('./BaseAssetGUID')
        if base_asset is not None and base_asset.text:
            inheritance_map[guid] = base_asset.text.strip()

    # --- NEW: Build the Parent Reward Map ---
    # This must be done AFTER assets_map is fully populated
    child_to_parents, public_refs, rival_rewards, quest_item_map = build_extended_source_maps(assets_map)
    # ----------------------------------------

    def resolve_with_structure(target_list):
        results = []
        for guid in target_list:
            if guid in asset_pools:
                members = resolve_with_structure(asset_pools[guid])
                flat = []
                for m in members:
                    flat.extend(m.split(":")[1].split(";")) if ":" in m else flat.append(m)
                results.append(f"{guid}:" + ";".join(flat))
            else:
                results.append(guid)
        return results

    headers = [
        'GUID', 'Icon', 'Name', 'InfoDescription', 'Buff', 'Buff Effects', 'BoostBuff', 'BoostBuff Effects', 'Boost Hint', 'Boost Condition', 'Targets', 'Source', 'Allocation', 'Rarity', 'Niche', 'Price', 'IsMetaItem', 'Origin', 'ObsidianPrice'
    ]
    extracted_data = []
    EXCLUDED_ICON = "data/ui/fhd/base/icon_content/items_specialist/unique/icon_3d_specialist_hooded_01.png"

    for asset in assets:
        template_node = asset.find('Template')
        if template_node is None or template_node.text not in ['Item', 'ItemWithBoost']:
            continue

        values_node = asset.find('Values')
        item_node = values_node.find('Item')
        guid = asset.find('./Values/Standard/GUID').text.strip()

        icon_node = asset.find('.//IconFilename')
        icon_val = icon_node.text if (icon_node is not None and icon_node.text) else ""
        if icon_val == EXCLUDED_ICON or get_text_safe(item_node, 'Rarity') == "Quest" or get_text_safe(item_node, 'Niche') == "None":
            continue

        raw_rarity = get_text_safe(item_node, 'Rarity', 'Common')
        is_meta_val = get_text_safe(item_node, 'IsMetaItem', '0')
        final_rarity = "Unique" if is_meta_val == '1' else raw_rarity

        row = {
            'GUID': guid, 'Icon': icon_val, 'Rarity': final_rarity,
            'Niche': get_text_safe(item_node, 'Niche', 'Finance'),
            'IsMetaItem': '1' if get_text_safe(item_node, 'IsMetaItem', '0') == '1' else '',
            'Allocation': get_text_safe(item_node, 'Allocation', 'Villa')
        }

        row['Price'] = get_text_safe(item_node, 'TradePrice', '')
        row['Origin'] = get_text_safe(item_node, 'Origin', '')
        try:
            row['ObsidianPrice'] = str(round(int(row['Price']) / 4 / 42)) if row['Price'] else ''
        except (ValueError, ZeroDivisionError):
            row['ObsidianPrice'] = ''

        oasis = asset.find('.//Text/OasisId')
        row['Name'] = oasis.text.strip() if oasis is not None else f"INHERIT:{inheritance_map.get(guid, '')}"
        row['InfoDescription'] = get_text_safe(asset, './/InfoDescription', "")

        row['Source'] = get_combined_source_value(guid, asset, child_to_parents, public_refs, rival_rewards, quest_item_map)

        buffs_node = asset.find('.//Effect/Buffs')
        buff_guids = [i.find('GUID').text.strip() for i in buffs_node.findall('Item') if i.find('GUID') is not None] if buffs_node is not None else []
        row['Buff'] = "; ".join(buff_guids)
        row['Buff Effects'] = " + ".join(filter(None, [get_full_buff_description(bg, assets_map) for bg in buff_guids]))

        # --- Boost Logic Updates ---
        boost_item = values_node.find('./ItemWithBoost')
        if boost_item is not None:
            # 1. Boost Buffs
            boost_buff_node = boost_item.find('BoostBuffs/Item/GUID')
            if boost_buff_node is not None:
                row['BoostBuff'] = boost_buff_node.text.strip()
                row['BoostBuff Effects'] = get_full_buff_description(row['BoostBuff'], assets_map)
            else:
                row['BoostBuff'] = ""; row['BoostBuff Effects'] = ""

            # 2. Boost Hint
            row['Boost Hint'] = get_text_safe(boost_item, 'BoostHint', "")

            # 3. Boost Conditions
            cond_list = []

            # CHECK 1: Inline Condition
            inline_cond_node = boost_item.find('BoostCondition/Values/PreConditionList/Condition')
            if inline_cond_node is not None:
                cond_list.append(parse_condition_node(inline_cond_node, assets_map))

            # CHECK 2: Referenced Conditions
            conditions_node = boost_item.find('BoostConditions')
            if conditions_node is not None:
                for item in conditions_node.findall('Item'):
                    cond_guid = get_text_safe(item, 'GUID', None)
                    if cond_guid:
                        cond_list.append(resolve_boost_condition(cond_guid, assets_map))

            row['Boost Condition'] = " & ".join(cond_list)

        else:
            row['BoostBuff'] = ""; row['BoostBuff Effects'] = ""
            row['Boost Hint'] = ""; row['Boost Condition'] = ""
        # ---------------------------

        targets_node = asset.find('.//Effect/Targets')
        raw_targets = [i.find('GUID').text.strip() for i in targets_node.findall('Item') if i.find('GUID') is not None] if targets_node is not None else []
        row['Targets'] = "|".join(resolve_with_structure(raw_targets))

        extracted_data.append(row)

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)
    print(f"Done. Exported {len(extracted_data)} items to {csv_file_path}")

if __name__ == "__main__":
    extract_xml_to_csv('data/base/config/export/assets.xml', 'items_export_with_effects.csv')