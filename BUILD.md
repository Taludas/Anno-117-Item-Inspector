# Build and Installation

The Anno 117 Item Inspector can be built into a standalone `.exe` using PyInstaller, controlled via a Makefile.

## Prerequisites

- Python 3.10 or newer — [python.org](https://www.python.org/downloads/)
- GNU Make for Windows — install via winget:
  ```
  winget install GnuWin32.Make
  ```
  or via Chocolatey:
  ```
  choco install make
  ```

## Game Data (per game version)

The exe does not ship the full in-game files. `build_version_data.py` boils the game's `assets.xml` and `texts_*.xml`
files down to a small package per game version in `data/versions/<version>/` (item CSV, asset lookup index,
only the localization lines the app can ask for, and the item XML used by the right-click export), plus
`data/versions/versions.json` which feeds the "Game Version" dropdown.

Source files:
- the current game version: `data/base/config/export/assets.xml` and `data/base/config/gui/texts_*.xml`
  (the version label is taken from `_version.py`, e.g. `2.1.0.0` -> `2.1`)
- older versions: `game_versions/<version>/data/base/config/{export,gui}/...` (same layout)

```
py build_version_data.py --current                       # only the current version
py build_version_data.py --version 2.0 --src game_versions/2.0
py build_version_data.py --all                           # current + everything in game_versions/
```

Run this after every game update (and after adding hardcoded OasisIDs/GUIDs to the mapping in
`anno117_item_inspector.py`, so their localization lines are included), before building the exe.
If two project folders exist side by side, pass the other script via `--scan-extra "<path>/anno117_item_inspector.py"`
so IDs used by either script are kept.

## Build Steps

**1. Create the virtual environment** (run this outside of any existing venv):
```
make venv
```

**2. Activate the virtual environment:**
```
.tamm.venv\Scripts\activate
```

**3. Install dependencies and build the executable:**
```
make all
```

The finished executable will be placed in the `dist` subdirectory as `Anno 117 Item Inspector.exe`.

**4. Test the executable:**
```
dist\Anno 117 Item Inspector.exe
```

## Cleanup

To remove build artefacts while still inside the virtual environment:
```
make clean
```

Then deactivate and remove the virtual environment:
```
deactivate
make venv.clean
```

## Notes

- `data/ui` (icons), `data/fonts` and `data/versions` (the generated game data packages) are bundled into the executable via the `--add-data` flags in the Makefile. `data/base` (the raw game files) is only needed to build the packages and is not shipped. Do not move or rename these folders before building.
- If you see font or icon errors when launching the exe, run `make exe.clean` followed by `make exe` to force a clean rebuild.
- The `requirements.txt` file must be present in the project root before running `make all`. It should contain at minimum:
  ```
    pillow
    pyinstaller
  ```