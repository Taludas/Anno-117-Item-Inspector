# ANNO 117 Item Inspector

A standalone desktop utility designed to browse, filter, and analyze item data for ANNO 117: Pax Romana. This tool provides a deep-dive interface for the game's item data, allowing players to find the perfect specialist or captain for their next Roman empire.

![Anno 117 Item Inspector](thumbnail_en.jpg)

# Features
![Anno 117 Item Inspector Features](features_en.jpg)
- Complete Database: Contains every item currently available in ANNO 117: Pax Romana.
- Full Multi-Language Support: Available in all official in-game languages. The data automatically adapt to your preferred language. Set your default startup language once or change it on the fly.

## Comprehensive Item Data
Every item entry is broken down into two distinct sections:

### General Information
- Visuals: Item Icon and Name.
- Context: Flavor Text and Niche.
- Metadata: Rarity, GUID, Game Version, and Allocation.

### Deep Dive Details
- Targets: Which buildings or units are affected - for multi-target items (using Asset Pools), hover over the light blue underlined Asset Pool name to see all individual targets. Click to pin the tooltip.
- Buffs & Values: All item effects covered, with value percentages in a nicely presented layout.
- Boost Logic: Specific Boost Conditions and the corresponding Boost Buffs for legendary items.
- Item Costs
- Acquisition: All Item Sources (Traders, Contracts, Reward Pools, Quest Rewards, or specific Research) with probabilities where applicable. Hover over the Item Source Header to get a legend for interpreting the icons in the list.

## Filtering System
- Multi-Category Search: Filter items by Rarity, Allocation, Niche, Target, Effects and Source.
- Smart Effect Merging: A unified filtering logic that merges similar attributes across different data types.
- Game Version history: Filter for items introduced in specific game versions (for future DLC releases)
- "Intelligent" Search Bar: You can manually search for (parts of the) item name, GUID, (parts of the) effect names, targets etc. Just type in what you are looking for and hit Enter or press the search button.
- Clear all Filters by pressing the "Clear All" Button.

# Getting Started
- Download the standalone exe file from the Releases.
- If you want to run the script locally:
  - Prerequisites:
    - Python 3.10 or higher
    - Tkinter (usually included with Python)
  - Installation:
    - Clone the repository
    - Run the extract_assets_resolve_pools_buffs_conditions_sources.py script to generate a fresh scv file - update the game assets.xml and language files in the data folder if necessary.
    - Run the application anno117_item_inspector.py

# Credits
- DuxVitae for the idea of extracting the item data to a csv
- Google Gemini for coding the majority of this project

# License
This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).