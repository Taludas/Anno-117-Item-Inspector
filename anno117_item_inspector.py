import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import csv
import xml.etree.ElementTree as ET
import os
import re
import webbrowser
import json
import sys
import platform
import ctypes
import _version

# Visual Styles
BG_MAIN = "#0b192c"
BG_SECTION = "#162a45"
FG_MAIN = "#ffffff"
FG_DIM = "#aaaaaa"

# Fonts
FONT_TITLE = ("Playfair Display SC", 16, "bold")
FONT_DESC = ("Marcellus", 11, "italic")
FONT_HEADER = ("Playfair Display SC", 13, "bold")
FONT_BODY = ("Marcellus", 13)
FONT_UI_BOLD = ("Marcellus", 14, "bold")
FONT_SMALL = ("Marcellus", 12)
FONT_HALF_SPACE = ("Marcellus", 5)

# Icon Rarity Colors and Loca
RARITY_COLORS = {
    "Common": "#32a852",
    "Rare": "#326ba8",
    "Epic": "#8032a8",
    "Legendary": "#d4af37",
    "Unique": "#eba117",
    "None": "#333333"
}

RARITY_LOCA_MAPPING = {
    "Common": "-6912278317458973655",
    "Uncommon": "-6906076503927319029",
    "Rare": "-6905062142041500517",
    "Epic": "-6907577562514031859",
    "Legendary": "-6909465036342822366",
    "Unique": "-6914484556772811597"
}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_path():
    """Returns a path to config.json in the user's AppData folder"""
    app_name = "Anno 117 Item Inspector"

    if platform.system() == "Windows":
        # Points to C:\Users\<User>\AppData\Roaming\Anno 117 Item Inspector
        base_dir = os.path.join(os.environ.get('APPDATA'), app_name)
    else:
        # For Mac/Linux, uses a hidden folder in the home directory
        base_dir = os.path.join(os.path.expanduser("~"), f".{app_name.lower()}")

    # Create the directory if it doesn't exist yet
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    return os.path.join(base_dir, "config.json")

CONFIG_FILE = get_config_path()

# Configuration
BASE_ICON_PATH = '.'
CSV_FILE = resource_path('items_export_with_effects.csv')
ASSETS_XML = resource_path('data/base/config/export/assets.xml')
LOCA_PATH_TEMPLATE = resource_path('data/base/config/gui/texts_{}.xml')

LANGUAGES = [
    'english', 'german', 'french', 'italian', 'spanish', 'russian', 'polish', 'japanese', 'korean', 'brazilian', 'simplified_chinese', 'traditional_chinese'
]

# Constants & IDs
ADDITIONAL_EFFECTS_ID = ["data/ui/fhd/base/icon_content/items_general/icon_2d_item_scope_radius.png", "-6916464905928465879"]
PRICE_LABEL_ID = ["data/ui/fhd/base/icon_content/generic/icon_2d_category_economy.png", "-6906740458081347201"]
BOOST_HEADER_ID = ["data/ui/fhd/base/icon_content/generic/icon_2d_enlarge.png", "-6902725718800634074"]

# Buff Effects
BUFF_EFFECT_MAPPING = {
    "AccuracyArcherModuleUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_accuracy.png", "-6911855274850644762"],
    "AccuracyBallistaModuleUpgrage": ["data/ui/fhd/base/icon_content/military/icon_2d_accuracy.png", "-6907865508483901738"],
    "AccuracyCatapultModuleUpgrage": ["data/ui/fhd/base/icon_content/military/icon_2d_accuracy.png", "-6903547229044160126"],
    "AccuracyUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_accuracy.png", "-6914510932562426253"],
    "ActiveTradePriceInPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_percentage.png", "-6904910338903030922"],
    "AddedFertility": ["data/ui/fhd/base/icon_content/generic/icon_2d_fertility.png", "-6909929033293673440", "-6907770522750495863"],
    "AdditionalLoadingSpeedInPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_ship_civilian.png", "-6913245221430448853"],
    "AdditionalMoneyIncome": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6907832455942731395"],
    "AdditionalOutput": ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_goods.png", "-6899820196143793484"],
    "AdditionalPercentage": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_reward_buff.png", "-6907497495990126878"],
    "AdditionalWorkforces": ["data/ui/fhd/base/icon_content/generic/icon_2d_meta_profile.png", "-6902792103058113405"],
    "AqueductConsumedWaterUpgrade": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_irrigation_water_capacity_1.png", "-6900173698993465429"],
    "AqueductWaterSupplyUpgrade": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_irrigation_water_capacity_1.png", "-6901410119100201615"],
    "ArmorUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_defense_armor.png", "-6916173326961563427"],
    "AttackCone_BallistaModule": ["data/ui/fhd/base/icon_content/generic/icon_2d_arrow_stylized_down.png", "-6908156295089722167", "-6906254771419500991"],
    "AttackCone_CatapultModule": ["data/ui/fhd/base/icon_content/generic/icon_2d_arrow_stylized_down.png", "-6908156295089722167", "-6904022497762596337"],
    "AttackSpeedArcherModulePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_speed.png", "-6907471390180921660"],
    "AttackSpeedBallistaModulePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_speed.png", "-6900615996648907081"],
    "AttackSpeedCatapultModulePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_speed.png", "-6914364061449956903"],
    "AttackSpeedRangedPercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_speed.png", "-6916798165698611871"],
    "AttackSpeedTorchPercentualUpgrade": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_minor_fire.png", "-6904582095030413595"],
    "AttributeModifierInPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_arrow_up.png", "-6905501351022478370"],
    "BaseHealthUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_plus.png", "-6908494598081338492"],
    "Belief": ["data/ui/fhd/base/icon_content/religion/icon_2d_religion.png", "-6917117282888968611"],
    "BuffBaseSpeedUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_rushing_to.png", "-6899782450596141269"],
    "BuffFavorableWindAngle": ["data/ui/fhd/base/icon_content/generic/icon_2d_wind_direction.png", "-6917509324150509842"],
    "BuffReduceCargoImpactUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_rushing_to.png", "-6917314961146315631"],
    "BuffReduceDamageImpactUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_rushing_to.png", "-6915299435512831228"],
    "BuffReduceNegativeWindImpactUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_wind_direction.png", "-6904284175891437012"],
    "BuffTransferSpeedUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_province_map.png", "-6914547372679383539"],
    "CanUseForest": ["data/ui/fhd/base/icon_content/infrastructure/icon_3d_resource_forest.png", "-6906268553696161885"],
    "CanUseMarsh": ["data/ui/fhd/base/icon_content/infrastructure/icon_3d_resource_marsh.png", "-6914826481896353728"],
    "CanUseMeadow": ["data/ui/fhd/base/icon_content/infrastructure/icon_3d_resource_meadow.png", "-6908731335818162955"],
    "ChangeNeedAttributesOf": ["data/ui/fhd/base/icon_content/generic/icon_2d_additional_need_attributes.png", "-6916727109582534166"],
    "ConstructionCostInPercent": ["data/ui/fhd/base/icon_content/construction_tools/icon_2d_construction_materials.png", "-6905220259948887554"],
    "ConstructionSpeedInPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_remaining_time.png", "-6916588842784089099"],
    "ConsumptionModifierInPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_repeatable.png", "-6902845924876156586"],
    "DefenseUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_defense_base.png", "-6916234667073216072"],
    "DiscoveryRadiusUpgrade": ["data/ui/fhd/base/icon_content/items_general/icon_2d_item_scope_radius.png", "-6912851074397281398"],
    "DistanceAttackRangeArcherModulePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_range.png", "-6913771487903800801"],
    "DistanceAttackRangeBallistaModulePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_range.png", "-6900440828800548713"],
    "DistanceAttackRangeCatapultModulePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_range.png", "-6908752606907018381"],
    "DistanceAttackRangePercentualUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_attack_range.png", "-6900632430001524951"],
    "EncampedUnitScalingFactorUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6916806603637230261"],
    "EncampedUnitSelfHealMultiplierUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_building_tier_max.png", "-6905174277262380495"],
    "FactoryRangePercentageUpgrade": ["data/ui/fhd/base/icon_content/transporter_cart/icon_2d_cart_empty.png", "-6905430209589419363"],
    "FireSafety": ["data/ui/fhd/base/icon_content/attributes/icon_2d_fire_safety.png", "-6913876283495722297"],
    "FuelDurationPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_frequency.png", "-6901428646395682482"],
    "Happiness": ["data/ui/fhd/base/icon_content/attributes/icon_2d_happiness.png", "-6915056271707822368"],
    "HealBuildingsPerMinuteUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_building_tier_max.png", "-6904744989082029193"],
    "HealPerMinuteUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_building_tier_max.png", "-6909031806713637632"],
    "HealRadiusUpgrade": ["data/ui/fhd/base/icon_content/items_general/icon_2d_item_scope_radius.png", "-6902642577827438950"],
    "Health": ["data/ui/fhd/base/icon_content/attributes/icon_2d_health.png", "-6912510107473053226"],
    "IncidentImmunity": ["data/ui/fhd/base/icon_content/generic/icon_2d_warning.png", "-6905739525374090419"],
    "InputAmountUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_goods.png", "-6900576451581047741"],
    "Knowledge": ["data/ui/fhd/base/icon_content/attributes/icon_2d_techtree_knowledge.png", "-6908049578864304337"],
    "LandTax": ["data/ui/fhd/base/icon_content/attributes/icon_2d_income.png", "-6905885150396558664"],
    "LoadingSpeedUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_ship_civilian.png", "-6911162818502702769"],
    "MaintenanceFactorUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6903385320568856769"],
    "MaximumMoraleUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_morale.png", "-6917319967366727198"],
    "MaximumRepairTargetsUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_repeatable.png", "-6904878606025953416"],
    "MeshGraphUpkeep": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6903385320568856769"],
    "MinDistanceBetweenTowersBuff": ["data/ui/fhd/base/icon_content/items_general/icon_2d_item_scope_radius.png", "-6917486192068866197"],
    "ModuleLimitPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_paste.png", "-6913343185575431361"],
    "Money": ["data/ui/fhd/base/icon_content/attributes/icon_2d_income.png", "-6910799479763478465"],
    "NeededAreaUpgrade": ["data/ui/fhd/base/icon_content/items_general/icon_2d_item_scope_radius.png", "-6915963651705874185"],
    "OffenseArcherModuleRangedUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_offense.png", "-6902617017467231785"],
    "OffenseBallistaModuleRangedUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_offense.png", "-6909984235779738348"],
    "OffenseCatapultModuleRangedUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_offense.png", "-6906754297935564907"],
    "OffenseChargeUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_offense.png", "-6907642198169893607"],
    "OffenseMeleeUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_offense.png", "-6914624354330523363"],
    "OffenseRangedUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_offense.png", "-6901124448895689147"],
    "PassiveRuinRepairSpeedUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_rebuild.png", "-6902214522674861072"],
    "PassiveTradeReward": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6909300745746637117"],
    "PipeCapacityUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_category_marsh_drainage.png", "-6908505536770437697"],
    "Population": ["data/ui/fhd/base/icon_content/attributes/icon_2d_population.png", "-6916310552575698080"],
    "Prestige": ["data/ui/fhd/base/icon_content/attributes/icon_2d_prestige.png", "-6911554866663245776"],
    "ProductivityUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_productivity.png", "-6901457306120429160"],
    "ProvidedNeedUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_consumption.png", "-6906821818431502107"],
    "RecruitmentCostInPercent": ["data/ui/fhd/base/icon_content/construction_tools/icon_2d_construction_materials.png", "-6900175465122901010"],
    "RecruitmentSpeedInPercent": ["data/ui/fhd/base/icon_content/generic/icon_2d_remaining_time.png", "-6912203919785395737"],
    "ReplaceInputs": ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_rotation.png", "-6909767605057018144"],
    "ReplaceWorkforce": ["data/ui/fhd/base/icon_content/construction_tools/icon_2d_tools.png", "-6900271494650358300"],
    "ResolverRangeUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_patrol_range.png", "-6899682999703418604"],
    "ResolverRepairDurationUpgrade": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_rebuild_time.png", "-6908683155652934058"],
    "ResolverResolveDurationUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_remaining_time.png", "-6901804608838418377"],
    "ResolverUnitCountUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_break_camp.png", "-6911863755390981443"],
    "RewardMoneyPerDestroyedBuildingUpgrade": ["data/ui/fhd/base/icon_content/attributes/icon_2d_income.png", "-6914993701769861740"],
    "RewardMoneyPerDestroyedShipUpgrade": ["data/ui/fhd/base/icon_content/attributes/icon_2d_income.png", "-6905414924283098115"],
    "SelfHealUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_building_tier_max.png", "-6906905232291239015"],
    "SellPriceFactorUpgrade": ["data/ui/fhd/base/icon_content/attributes/icon_2d_income.png", "-6912306538068974009"],
    "ShieldUpgrade": ["data/ui/fhd/base/icon_content/military/icon_2d_defense_shield.png", "-6915348409801369648"],
    "SlotCountUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_goods.png", "-6901072862113090986"],
    "SocketCountUpgrade": ["data/ui/fhd/base/icon_content/generic/icon_2d_category_civic.png", "-6908073095614905585"],
    "StorageCapacityModifier": ["data/ui/fhd/base/icon_content/generic/icon_2d_storage_capacity.png", "-6910269557488986844"],
    "WorkforceMaintenanceFactorUpgrade": ["data/ui/fhd/base/icon_content/attributes/icon_2d_population.png", ["-6912050764580404020", "-6910974881837699422"]],
    "WorkforceModifierInPercent": ["data/ui/fhd/base/icon_content/construction_tools/icon_2d_tools.png", "-6902123928322850502"]
}

# Niche
NICHE_LOCA_MAPPING = {
    "Finance": ["data/ui/fhd/base/icon_content/attributes/icon_2d_income.png", "-6914140938188892301"],
    "Religion": ["data/ui/fhd/base/icon_content/religion/icon_2d_religion.png", "-6914559624031392856"],
    "Research": ["data/ui/fhd/base/icon_content/attributes/icon_2d_techtree_knowledge.png", "-6915178130906922013"],
    "Culture": ["data/ui/fhd/base/icon_content/attributes/icon_2d_happiness.png", "-6900022411251645295"],
    "Economy": ["data/ui/fhd/base/icon_content/generic/icon_2d_productivity.png", "-6901647246967713753"],
    "Agriculture": ["data/ui/fhd/base/icon_content/attributes/icon_2d_health.png", "-6917159103013214000"],
    "Diplomacy": ["data/ui/fhd/base/icon_content/attributes/icon_2d_prestige.png", "-6910372341984870934"],
    "Military": ["data/ui/fhd/base/icon_content/attributes/icon_2d_fire_safety.png", "-6899994156946737926"],
    "Nautics": ["data/ui/fhd/base/icon_content/generic/icon_2d_nautical.png", "-6909918878210610862"]
}

# Incidents
INCIDENT_MAPPING = {
    "Disease": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_minor_illness.png", "-6900581410579948849"],
    "Plague": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_major_illness.png", "-6905547679383140251"],
    "Fire": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_minor_fire.png", "-6909498465775769599"],
    "Inferno": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_major_fire.png", "-6902978744771256478"],
    "Unrest": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_minor_riot.png", "-6913158135862449542"],
    "Rebellion": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_incident_major_riot.png", "-6908386764451142720"]
}

# Allocation
SLOT_LOCA_MAPPING = {
    "Villa": ["data/ui/fhd/base/icon_content/generic/icon_2d_villa.png", "-6906804867337495474"],
    "Ship": ["data/ui/fhd/base/icon_content/generic/icon_2d_ship.png", "-6910306070209971020"]
}

# Compare Ops Boost Hints
COMPARE_OPS = {
    "AtLeast": "≥", "AtMost": "≤", "Equals": "=", "LessThen": "<", "MoreThen": ">"
}

# Conditions Boost Hints
CONDITION_TYPES = {
    "ConditionNeedAttributeCounter": ["-6907409456541782824", "-6914796270700478523"],
    "ConditionObjectCount": "-6909050664680798634",
    "ConditionItemUsed": "-6914628682709519748",
    "ConditionActiveEmperor": ["-6909286393160361264", "-6910778800790301118"],
    "ConditionReligion": "-6914126446077893143",
    "ConditionMonumentEventActive": "-6912188219464097135",
    "ConditionEmperorRelation": ["-6900988673237471031", "-6909286393160361264"],
    "ConditionDiplomacyState": "-6901372654787949026",
    "ConditionWarState": "-6916305455916138439",
    "ConditionDominantPatron": "-6917281781830473807",
    "ConditionInStorage": ["-6904656400857447148", "-6916792298682888435"],
    "ConditionTradeRouteCount": "-6915569607474692589"
}

# No Religion Condition
RELIGION_ZERO_ID = "-6899884938127726030"

# Have Goods in island storage Condition
STORAGE_LOCA_ID = ["-6904656400857447148", "-6916792298682888435"]

# Condition Attributes
CONDITION_ATTRIBUTES = {
    "Belief": "-6917117282888968611",
    "FireSafety": "-6913876283495722297",
    "Happiness": "-6915056271707822368",
    "Health": "-6912510107473053226",
    "Knowledge": "-6908049578864304337",
    "Money": "-6910799479763478465",
    "Prestige": "-6911554866663245776",
    "Population": "-6916310552575698080",
    "NavalStrength": "-6903178156203890847",
    "ArmyStrength": "-6916030253858215742",
    "MoneyBalance": "-6910768626546451500",
    "ActiveEmperorReputation": ["-6900988673237471031", "-6909286393160361264"],
    "ContractsCompleted": "-6915965511056834686",
    "ShipsSoldToParticipant": "-6915345810045190210",
    "IslandsDiscovered": "-6917195644310704229",
    "ItemsInStock": ["-6914097598100160370", "-6916792298682888435"],
}

# Condition Scope
CONDITION_LOCATIONS = {
    "Area": "-6902656537549924720",
    "Session": ["-6914487889124229090", "-6907135442311038421"]
}

# Condition Emperor Relation
EMPEROR_RELATION_VALUES = {
    "HostileZone": "-6917403091401205128",
    "UnrulyZone": "-6915583492848202370",
    "CasualZone": "-6914671557303069450",
    "EffortZone": "-6917351903766265206",
    "ChallengeZone": "-6901978489714054004",
    "Rebellion": "-6912555987231726209",
    "ProConsul": "-6904131997685258147",
    "Consul": "-6916032052665441306"
}

# Condition Diplomacy Status
DIPLOMACY_STATE_VALUES = {
    "Undiscovered": "-6910984867916216313",
    "Alliance": "-6909792988828917153",
    "DefensivePact": "-6913251946263130178",
    "Peace": "-6913646454384213306",
    "War": "-6903421091051165993"
}

# Condition Ship Modules
MODULE_MAPPING = {
    "RequiredModuleCount": "-6903948808470486709",
    "RequiredMilitaryModuleCount": ["-6903948808470486709", "-6905451000995360298"],
    "ShipConfiguration": "-6910601933138024387"
}

# Manual GUID Mappings
MANUAL_GUID_MAP = {
    "52097": ["-6914984016984180941", "-6912105848696448949"],
    "113059": "-6907933155664049947"
}

# RewardPool GUID Mappings
REWARD_POOL_MAPPING = {
    "43017": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_caeso.png", "-6911896607082319713"],
    "43018": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/base/icon_content/portraits/portrait_trader_diana.png", "-6916713046177402308"],
    "43019": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/base/icon_content/portraits/portrait_trader_valeria.png", "-6914091878445862523"],
    "43020": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/base/icon_content/portraits/portrait_trader_manx.png", "-6910353931395472437"],
    "43021": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/base/icon_content/portraits/portrait_trader_corvinus.png", "-6913545710924920342"],
    "43022": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_voada.png", "-6917151211833228038"],
    "145045": ["data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png", "-6915651869812775825", "data/ui/fhd/dlc01/icon_content/portraits/icon_3d_trader_caecilia.png", "-6910597003872763071"],
    "64766": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_dorian.png", "-6907653836002759647", "-6914762194635081755"],
    "64767": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_dorian.png", "-6907653836002759647", "-6915564870584412590"],
    "64768": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_dorian.png", "-6907653836002759647", "-6916763202365380332"],
    "64769": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_tarragon.png", "-6907715955237745360", "-6914762194635081755"],
    "64770": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_tarragon.png", "-6907715955237745360", "-6915564870584412590"],
    "64771": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_tarragon.png", "-6907715955237745360", "-6916763202365380332"],
    "64772": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_licia.png", "-6913848851309955011", "-6914762194635081755"],
    "64773": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_licia.png", "-6913848851309955011", "-6915564870584412590"],
    "64774": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_licia.png", "-6913848851309955011", "-6916763202365380332"],
    "64775": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_athr.png", "-6910833454643017908", "-6914762194635081755"],
    "64776": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_athr.png", "-6910833454643017908", "-6915564870584412590"],
    "64777": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_athr.png", "-6910833454643017908", "-6916763202365380332"],
    "64778": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_zarai.png", "-6917026237016363604", "-6914762194635081755"],
    "64779": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_zarai.png", "-6917026237016363604", "-6915564870584412590"],
    "64780": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_zarai.png", "-6917026237016363604", "-6916763202365380332"],
    "64781": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_concordia.png", "-6907727125079325428", "-6914762194635081755"],
    "64782": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_concordia.png", "-6907727125079325428", "-6915564870584412590"],
    "64783": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_concordia.png", "-6907727125079325428", "-6916763202365380332"],
    "64784": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_neferneru.png", "-6915743260076865937", "-6914762194635081755"],
    "64785": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_neferneru.png", "-6915743260076865937", "-6915564870584412590"],
    "64786": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_rival_neferneru.png", "-6915743260076865937", "-6916763202365380332"],
    "64787": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_diana.png", "-6916713046177402308", "-6914762194635081755"],
    "64788": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_diana.png", "-6916713046177402308", "-6915564870584412590"],
    "64789": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_diana.png", "-6916713046177402308", "-6916763202365380332"],
    "64790": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_valeria.png", "-6914091878445862523", "-6914762194635081755"],
    "64791": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_valeria.png", "-6914091878445862523", "-6915564870584412590"],
    "64792": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_valeria.png", "-6914091878445862523", "-6916763202365380332"],
    "64793": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_caeso.png", "-6911896607082319713", "-6914762194635081755"],
    "64794": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_caeso.png", "-6911896607082319713", "-6915564870584412590"],
    "64795": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_caeso.png", "-6911896607082319713", "-6916763202365380332"],
    "64796": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_corvinus.png", "-6913545710924920342", "-6914762194635081755"],
    "64797": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_corvinus.png", "-6913545710924920342", "-6915564870584412590"],
    "64798": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_corvinus.png", "-6913545710924920342", "-6916763202365380332"],
    "64799": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_manx.png", "-6910353931395472437", "-6914762194635081755"],
    "64800": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_manx.png", "-6910353931395472437", "-6915564870584412590"],
    "64801": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_trader_manx.png", "-6910353931395472437", "-6916763202365380332"],
    "64802": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_voada.png", "-6917151211833228038", "-6914762194635081755"],
    "64803": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_voada.png", "-6917151211833228038", "-6915564870584412590"],
    "64804": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_voada.png", "-6917151211833228038", "-6916763202365380332"],
    "145046": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/dlc01/icon_content/portraits/icon_3d_trader_caecilia.png", "-6910597003872763071", "-6914762194635081755"],
    "145047": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/dlc01/icon_content/portraits/icon_3d_trader_caecilia.png", "-6910597003872763071", "-6915564870584412590"],
    "145048": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png", "-6914021190765224130", "data/ui/fhd/dlc01/icon_content/portraits/icon_3d_trader_caecilia.png", "-6910597003872763071", "-6916763202365380332"],
    "79669": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_research_economic.png", "-6906931485680097276", "-6906931485680097276"],
    "79670": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_research_civic.png", "-6915741635554061343", "-6915741635554061343"],
    "79671": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_research_military.png", "-6909604399726531068", "-6909604399726531068"],
    "95375": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_caeso.png", "-6911896607082319713"],
    "95439": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_dorian.png", "-6907653836002759647"],
    "95440": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_tarragon.png", "-6907715955237745360"],
    "95441": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_licia.png", "-6913848851309955011"],
    "95442": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_athr.png", "-6910833454643017908"],
    "95443": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_zarai.png", "-6917026237016363604"],
    "95444": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_concordia.png", "-6907727125079325428"],
    "95445": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_rival_neferneru.png", "-6915743260076865937"],
    "95446": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_trader_diana.png", "-6916713046177402308"],
    "95447": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_trader_valeria.png", "-6914091878445862523"],
    "95448": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_trader_corvinus.png", "-6913545710924920342"],
    "95449": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_trader_manx.png", "-6910353931395472437"],
    "95450": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_pirate_voada.png", "-6917151211833228038"],
    "95452": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_empress_julia.png", "-6917064935972779595"],
    "95453": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/base/icon_content/portraits/portrait_emperor_calidus.png", "-6903528267829072805"],
    "145049": ["data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png", "-6904030652562679494", "data/ui/fhd/dlc01/icon_content/portraits/icon_3d_trader_caecilia.png", "-6910597003872763071"],
    "122533": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6908176692369518815"],
    "122534": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6909503110265739293"],
    "122535": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6915877880140582624"],
    "122536": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6913083066444049357"],
    "122537": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6910662342821446253"],
    "122538": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6899731952442968805"],
    "122539": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6901395514162112757"],
    "122540": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6908928132728089827"],
    "122541": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6914923149854169904"],
    "122542": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6909867291834833909"],
    "122543": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6903703426580683222"],
    "122544": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6906276675127952394"],
    "122545": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6907991623289664677"],
    "122546": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6900196985132589583"],
    "122547": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6914573601432067141"],
    "145050": ["data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png", "-6908773579491322283", "-6913008330424928700"]
}

REWARD_POOL_CATEGORY_ORDER = {
    "icon_2d_festival":              0,  # Festivals
    "icon_2d_buy_sell":              1,  # Traders
    "icon_2d_questlog_writting":     2,  # Quests
    "icon_2d_loading_ramp_ship":     3,  # Ship / Rivals
    "icon_2d_research_economic":     4,  # Research
    "icon_2d_research_civic":        4,
    "icon_2d_research_military":     4
}

# Source Labels
SOURCE_LABELS = {
    "ItemGainedWhenDefeated": ["data/ui/fhd/base/icon_content/diplomacy/icon_2d_subjugation_consul.png", "-6914401298572542861"],
    "HallofFame": ["data/ui/fhd/base/icon_content/tech_tree/icon_2d_anno_account.png", "-6906945524005841361"],
    "Quest": ["data/ui/fhd/base/icon_content/quest_tracker/icon_2d_quest_tracker.png", "-6905698394117185352"]
}

# DLC Icons
DLC_ICONS = {
    "base": ["data/ui/fhd/base/icon_content/generic/icon_3d_game_logo.png", "-6917415429012198504"],
    "cdlc01": ["data/ui/fhd/base/icon_content/cdlc/icon_3d_cdlc_category_01_mosaic.png", "-6909335020213265304"],
    "dlc01": ["data/ui/fhd/base/icon_content/dlc/icon_3d_dlc_category_volcano.png", "-6917386513941705145"],
    "dlc02": ["data/ui/fhd/base/icon_content/dlc/icon_3d_dlc_category_circus_maximus.png", "-6915867658126559590"],
    "dlc03": ["data/ui/fhd/base/icon_content/dlc/icon_3d_dlc_category_egypt.png", "-6901020047715601345"]
}

class ItemBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anno 117 Item Inspector" + f' v{_version.__VERSION__}')
        self.root.iconbitmap(resource_path("data/ui/anno117_item_inspector.ico"))
        self.root.geometry("1440x900")
        self.root.configure(bg=BG_MAIN)

        # Initialize all your dictionaries and lists
        self.items_data = []
        self.localization_map = {}
        self.asset_guid_to_loca_id = {}
        self.asset_guid_to_icon = {}
        self.asset_pool_first_item = {}
        self.inheritance_lookup = {}
        self.target_display_to_guid = {}
        self.effect_display_to_raw = {}
        self.niche_display_to_raw = {}
        self.rarity_display_to_raw = {}
        self.alloc_display_to_raw = {}
        self.source_display_to_raw = {}
        self._search_after_id = None
        self.icon_cache = {}
        self.name_resolution_cache = {}
        self.photo_image_cache = {}

        self.filter_rarities = set()
        self.filter_allocations = set()
        self.filter_effects_raw = set()
        self.filter_niches_raw = set()
        self.filter_sources_raw = set()
        self.current_dlc_filter = "all"

        FONT_FILES = [
            "data/fonts/PlayfairDisplaySC-Regular.ttf",
            "data/fonts/Marcellus-Regular.ttf"
        ]
        def load_custom_font(font_path):
            """Registers a font file with the Windows system for the current process."""
            if not os.path.exists(font_path):
                print(f"Font not found: {font_path}")
                return False

            # GDI AddFontResourceExW constant
            FR_PRIVATE = 0x10

            # Load the font using Windows API
            res = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
            return res > 0

        for f in FONT_FILES:
            load_custom_font(resource_path(f))

        # --- STARTUP OVERLAY ---
        # Create a frame that covers the whole screen
        self.startup_overlay = tk.Frame(self.root, bg=BG_MAIN)
        self.startup_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.loading_label = tk.Label(
            self.startup_overlay,
            text="Initializing Item Database...\nParsing Game Assets & Localization",
            font=FONT_HEADER, fg=FG_MAIN, bg=BG_MAIN
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

        # Set cursor to busy and force the window to draw the overlay
        self.root.config(cursor="watch")
        self.root.update()

        # Delay the heavy loading by 100ms so the UI has time to "breathe" and show the loading screen before the CPU hangs.
        self.root.after(100, self.perform_initial_load)

    def perform_initial_load(self):
        try:
            # 1. Handle Language (will open popup if no config exists)
            self.current_language = self.get_or_set_language()

            # 2. Heavy Data Parsing
            self.loading_label.config(text="Loading Localization...")
            self.root.update()
            self.load_localization(self.current_language)

            self.loading_label.config(text="Parsing Assets.xml...")
            self.root.update()
            self.load_assets_map(ASSETS_XML)

            self.loading_label.config(text="Processing CSV Data...")
            self.root.update()
            self.load_csv_data()

            # 3. Build the UI
            self.loading_label.config(text="Building Interface...")
            self.root.update()
            self.setup_top_bar()
            self.current_sort_col = "GUID"
            self.current_sort_reverse = False
            self.setup_main_layout()
            self.refresh_table()

        finally:
            # 4. Remove the overlay and restore cursor
            if hasattr(self, 'startup_overlay'):
                self.startup_overlay.destroy()
            self.root.config(cursor="")

    # User defines default language on first start of the app
    def get_or_set_language(self):
        # 1. Check if config exists
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    lang = config.get("language")
                    if lang:
                        return lang
            except Exception:
                pass

        # 2. Setup the Popup Dimensions
        pop_w, pop_h = 300, 600
        selected_lang = [None]

        # 3. FORCE MAIN WINDOW TO RENDER
        self.root.update()

        lang_window = tk.Toplevel(self.root)
        lang_window.title("Select Language")
        lang_window.configure(bg=BG_MAIN)

        # 4. Centering Math
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()

        x = root_x + (root_w // 2) - (pop_w // 2)
        y = root_y + (root_h // 2) - (pop_h // 2)

        lang_window.geometry(f"{pop_w}x{pop_h}+{x}+{y}")

        # 5. Layering
        lang_window.transient(self.root)
        lang_window.attributes("-topmost", True)
        lang_window.grab_set()

        tk.Label(lang_window, text="Select Default Language", font=FONT_HEADER, bg=BG_MAIN, fg=FG_MAIN).pack(pady=20)

        def set_lang(lang):
            selected_lang[0] = lang
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"language": lang}, f)
            lang_window.grab_release()
            lang_window.destroy()

        for lang in LANGUAGES:
            btn = tk.Button(lang_window,
                            text=lang.replace('_', ' ').title(),
                            command=lambda l=lang: set_lang(l),
                            bg=BG_SECTION, fg=FG_MAIN, font=FONT_BODY,
                            activebackground=FG_MAIN, activeforeground=BG_MAIN)
            btn.pack(fill="x", padx=20, pady=2)

        # Pause until user clicks a button
        self.root.wait_window(lang_window)
        return selected_lang[0] or "english"

    # Custom centered prompt that triggers the existing language swap engine when the user wants to swap the default language
    def change_language_request(self):
        # 1. Create a Custom Centered Prompt (since messagebox doesn't center well)
        prompt = tk.Toplevel(self.root)
        prompt.overrideredirect(True)
        prompt.configure(bg=BG_MAIN, highlightbackground="#ffd700", highlightthickness=2)

        # Centering
        self.root.update_idletasks()
        p_w, p_h = 400, 160
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (p_w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (p_h // 2)
        prompt.geometry(f"{p_w}x{p_h}+{x}+{y}")
        prompt.grab_set()

        tk.Label(prompt, text="Reset Default Language?", font=FONT_HEADER, bg=BG_MAIN, fg="#ffd700").pack(pady=(20, 10))
        tk.Label(prompt, text="This will clear settings and restart the selection.", font=FONT_BODY, bg=BG_MAIN, fg=FG_MAIN).pack()

        btn_frame = tk.Frame(prompt, bg=BG_MAIN)
        btn_frame.pack(pady=20)

        def proceed():
            prompt.destroy()
            # 2. DELETE CONFIG
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)

            # 3. Trigger your existing overlay/swap engine
            self.on_language_change()

        tk.Button(btn_frame, text=" Yes, Reset ", command=proceed, bg=BG_SECTION, fg=FG_MAIN, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text=" Cancel ", command=prompt.destroy, bg=BG_SECTION, fg=FG_MAIN, width=12).pack(side=tk.LEFT, padx=10)

    # Parse Assets
    def load_assets_map(self, xml_path):
        if not os.path.exists(xml_path): return
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for asset in root.findall('.//Asset'):
                guid_node = asset.find('./Values/Standard/GUID')
                if guid_node is None: continue
                guid = guid_node.text.strip()

                oasis_node = asset.find('./Values/Text/OasisId')
                if oasis_node is not None:
                    self.asset_guid_to_loca_id[guid] = oasis_node.text.strip()

                quest_name_node = asset.find('./Values/QuestEntry/QuestName')
                if quest_name_node is not None:
                    self.asset_guid_to_loca_id[guid] = quest_name_node.text.strip()

                base_node = asset.find('./BaseAssetGUID')
                if base_node is not None and base_node.text:
                    self.inheritance_lookup[guid] = base_node.text.strip()

                icon_node = asset.find('./Values/Standard/IconFilename')
                if icon_node is not None and icon_node.text:
                    self.asset_guid_to_icon[guid] = icon_node.text.strip()

                template_node = asset.find('./Template')
                if template_node is not None and template_node.text and template_node.text.strip() == "AssetPoolNamed":
                    child_asset = asset.find('./Values/AssetPool/AssetList/Item/Asset')
                    if child_asset is not None and child_asset.text:
                        self.asset_pool_first_item[guid] = child_asset.text.strip()

        except Exception as e:
            print(f"Error indexing assets: {e}")

    # Parse CSV Item data
    def load_csv_data(self):
        if not os.path.exists(CSV_FILE): return
        try:
            target_add_eff_id = ADDITIONAL_EFFECTS_ID[1] if isinstance(ADDITIONAL_EFFECTS_ID, list) else ADDITIONAL_EFFECTS_ID

            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    source_raw = row.get('Source', '').strip()
                    if not source_raw or source_raw.lower() == "none" or source_raw == "":
                        continue

                    self.items_data.append(row)

                    parts = [p.strip() for p in source_raw.split('|') if p.strip()]
                    for part in parts:
                        if ":" in part:
                            self.filter_sources_raw.add(part.split(':', 1)[0].strip())
                        elif "[" in part and "]" in part:
                            guid = part.split('[')[0].strip()
                            pool_oids = REWARD_POOL_MAPPING.get(guid, [])
                            if pool_oids:
                                self.filter_sources_raw.add(f"POOL_{guid}")

                    if row['Rarity']: self.filter_rarities.add(row['Rarity'])
                    if row['Allocation']: self.filter_allocations.add(row['Allocation'])
                    if row['Niche'] and row['Niche'] != "None": self.filter_niches_raw.add(row['Niche'])

                    for col in ['Buff Effects', 'BoostBuff Effects']:
                        val = row.get(col, '')
                        if val and val != "None":
                            found = re.findall(r'(\w+|-?\d{15,20})', val)
                            for m in found:
                                if m in ["Disease", "Plague", "Fire", "Inferno", "Unrest", "Rebellion", "FertilityPercent"]:
                                    continue
                                if not m.replace('-','').isdigit() or m == target_add_eff_id:
                                    self.filter_effects_raw.add(m)
        except Exception as e: print(f"CSV Error: {e}")

    # Parse Language files
    def load_localization(self, language):
        path = LOCA_PATH_TEMPLATE.format(language)
        self.localization_map = {}
        if not os.path.exists(path): return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for text_container in root.findall('.//Text'):
                line_id_node = text_container.find('LineId')
                val_node = text_container.find('Text')
                if line_id_node is not None and val_node is not None:
                    tid = line_id_node.text.strip()
                    self.localization_map[tid] = val_node.text if val_node.text else ""
        except Exception as e: print(f"Loca Error: {e}")

    # Resolve GUID to OasisID
    def get_resolved_name(self, guid):
        if not guid: return ""
        guid = str(guid).strip()

        # 1. Check Resolution Cache First (Instant Speedup)
        if guid in self.name_resolution_cache:
            return self.name_resolution_cache[guid]

        # 2. Check for Manual/Static GUIDs
        if guid in MANUAL_GUID_MAP:
            loca_id = MANUAL_GUID_MAP[guid]
            res = " ".join([self.localization_map.get(str(i), str(i)) for i in (loca_id if isinstance(loca_id, list) else [loca_id])])
            self.name_resolution_cache[guid] = res
            return res

        # 3. Resolve via Inheritance
        current_guid = guid
        visited = set()
        is_inherited = False

        suffix_id = "-6903427160198155951"
        suffix_text = f" ({self.localization_map.get(suffix_id, 'Base')})"

        while current_guid:
            if current_guid in visited: break
            visited.add(current_guid)

            loca_id = self.asset_guid_to_loca_id.get(current_guid)
            if loca_id:
                name = self.localization_map.get(loca_id, current_guid)
                # Apply suffix if we found the name via inheritance
                res = f"{name}{suffix_text}" if is_inherited else name
                self.name_resolution_cache[guid] = res
                return res

            # Move up the inheritance tree and mark that we are now looking at a parent
            current_guid = self.inheritance_lookup.get(current_guid)
            is_inherited = True

        res = f"Unknown ({guid})"
        self.name_resolution_cache[guid] = res
        return res

    # Setup for multiple OasisIds for one GUID/mapping entry
    def resolve_oasis_list(self, oid_list):
        if isinstance(oid_list, list):
            return " ".join([self.localization_map.get(o, o).replace("{}", "").strip() for o in oid_list])
        return self.localization_map.get(oid_list, oid_list).replace("{}", "").strip()

    # Parse item icon
    def get_icon_image(self, rel_path, size=(128, 128)):
        # 1. Basic check
        if not rel_path:
            rel_path = ""

        # Define paths
        full_path = resource_path(os.path.join(BASE_ICON_PATH, rel_path.replace('\\', '/')))
        placeholder_rel = resource_path("data/ui/fhd/base/icon_content/items_specialist/unique/icon_3d_specialist_hooded_01.png")
        placeholder_full = os.path.join(BASE_ICON_PATH, placeholder_rel)

        # 2. Try to load the requested icon
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                img = Image.open(full_path).convert("RGBA")
                return img.resize(size, Image.Resampling.LANCZOS)
            except:
                pass # Fall through to placeholder if file is corrupted

        # 3. Fallback: Try to load the placeholder hooded specialist
        if os.path.exists(placeholder_full):
            try:
                img = Image.open(placeholder_full).convert("RGBA")
                return img.resize(size, Image.Resampling.LANCZOS)
            except:
                return None

        # 4. Ultimate Fallback: Return None if nothing exists
        return None

    # Create a unique key for the specific path and size
    def get_icon_photo(self, icon_path, size=(25, 25)):
        cache_key = (icon_path, size)
        if cache_key in self.photo_image_cache:
            return self.photo_image_cache[cache_key]

        # Standardize path
        full_path = resource_path(os.path.join(BASE_ICON_PATH, icon_path.replace("\\", "/").lstrip("/")))
        if not os.path.exists(full_path):
            return None

        try:
            img = Image.open(full_path).convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.photo_image_cache[cache_key] = photo
            return photo
        except Exception as e:
            print(f"Icon Error: {e}")
            return None

    # Map item's game version from mentioning dlcs in icon path
    def get_dlc_key_from_path(self, icon_path, origin=""):
        # Origin column takes priority if populated
        if origin:
            origin_lower = origin.lower()
            if "CDLC01" in origin_lower: return "cdlc01"
            if "DLC01"  in origin_lower: return "dlc01"
            if "DLC02"  in origin_lower: return "dlc02"
            if "DLC03"  in origin_lower: return "dlc03"

        # Fallback: infer from icon path as before
        if not icon_path: return "base"
        path_lower = icon_path.lower().replace('\\', '/')
        if "data/ui/fhd/cdlc01" in path_lower: return "cdlc01"
        if "data/ui/fhd/dlc01"  in path_lower: return "dlc01"
        if "data/ui/fhd/dlc02"  in path_lower: return "dlc02"
        if "data/ui/fhd/dlc03"  in path_lower: return "dlc03"

        return "base"

    # Resolve icon path to actual icon and OasisId to actual text
    def resolve_loca_and_icon(self, mapping_val, default_text):
        """
        Handles mapping_val as:
        1. A simple string (GUID)
        2. A list: [icon_path, GUID]
        3. A list of GUIDs: [GUID1, GUID2]
        """
        icon_path = None

        # 1. Handle None
        if not mapping_val:
            return None, self.localization_map.get(default_text, default_text)

        # 2. If it's a list, check if the first element is a file path (contains '/')
        if isinstance(mapping_val, list):
            if len(mapping_val) > 0 and isinstance(mapping_val[0], str) and ('/' in mapping_val[0] or '\\' in mapping_val[0]):
                icon_path = mapping_val[0]
                # The rest are GUIDs
                oids = mapping_val[1:]
            else:
                # It's just a list of GUIDs
                oids = mapping_val
        else:
            # It's a single GUID string
            oids = [mapping_val]

        # 3. Resolve the localized text from the remaining GUIDs
        # Ensure we don't try to hash a list if 'o' is somehow still a list
        loc_parts = []
        for o in oids:
            if isinstance(o, list): # Safety check for nested lists
                part = " ".join([self.localization_map.get(i, i) for i in o])
            else:
                part = self.localization_map.get(o, str(o))
            loc_parts.append(part.replace("{}", "").strip())

        loc_text = " ".join(loc_parts) if loc_parts else default_text

        return icon_path, loc_text

    def insert_text_with_icons(self, text_widget, text, tags):
        if isinstance(tags, str):
            tags = (tags,)

        # The regex captures [IMG...], [SIMG...], and now explicitly handles \t if needed but usually, we just need to make sure the loop handles the 'else' parts correctly.
        parts = re.split(r'(\[(?:IMG|SIMG)[:\s].*?\])', text)

        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                is_small = part.startswith('[SIMG')
                prefix_len = 5 if is_small else 4
                icon_path = part[prefix_len:-1].strip(': ').strip()

                # Determine size
                target_size = (25, 25) if is_small else (35, 35)

                # Use the cached photo getter we implemented
                photo = self.get_icon_photo(icon_path, size=target_size)

                if photo:
                    # Insert the image at the current end
                    # We use "end-1c" to ensure it's placed before the trailing newline if present
                    insert_idx = text_widget.index(tk.END + "-1c")
                    text_widget.image_create(insert_idx, image=photo, padx=2, align="center")

                    # CRITICAL: Apply the tags to the specific index of the image
                    for t in tags:
                        text_widget.tag_add(t, insert_idx)
            else:
                if part:
                    # Insert text (including \t) with the tags
                    # This ensures the tab uses the 'source_line_split' tab settings
                    text_widget.insert(tk.END, part, tags)

    # Resolve Item Source from csv
    def resolve_source(self, raw_source):
        if not raw_source or raw_source == "None": return []

        parts = [p.strip() for p in raw_source.split('|') if p.strip()]

        def source_sort_key(part):
            # Pool entries carry their GUID before the bracket
            if "[" in part and "]" in part:
                match = re.match(r'(\d+)\s*\[', part)
                if match:
                    guid = match.group(1)
                    mapping = REWARD_POOL_MAPPING.get(guid, [])
                    if mapping:
                        icon_path = mapping[0] if mapping[0].endswith('.png') else ""
                        for key, priority in REWARD_POOL_CATEGORY_ORDER.items():
                            if key in icon_path:
                                return priority
            # Keyed sources (Quest:, ItemGainedWhenDefeated:, HallofFame:) go last
            return 99

        parts.sort(key=source_sort_key)

        resolved_lines = []

        for part in parts:
            line_segments = []
            line = ""

            def process_mapping(mapping):
                pending_icon = None
                for i, item in enumerate(mapping):
                    if item.endswith('.png'):
                        pending_icon = item
                    else:
                        # Determine sizing: First icon/ID pair is small (SIMG)
                        is_first = (len(line_segments) == 0)
                        tag = "SIMG" if is_first else "IMG"

                        if is_first and pending_icon:
                            line_segments.append(f"[{tag}:{pending_icon}] -")
                            pending_icon = None
                            continue

                        loc_txt = self.localization_map.get(item, item).replace("{}", "").strip()
                        segment = f"[{tag}:{pending_icon}] {loc_txt}" if pending_icon else loc_txt
                        line_segments.append(segment)
                        pending_icon = None

            # CASE 1: Reward Pools & Percentage entries
            if "[" in part and "]" in part:
                match = re.match(r'(\d+)\s*\[(.*?)\]', part)
                if match:
                    guid, percent = match.groups()
                    mapping = REWARD_POOL_MAPPING.get(guid)
                    if mapping:
                        process_mapping(mapping)
                    else:
                        # INSTANT LOOKUP FROM CACHE
                        xml_icon = self.asset_guid_to_icon.get(guid)
                        res_name = self.get_resolved_name(guid)
                        line_segments.append(f"[SIMG:{xml_icon}] {res_name}" if xml_icon else res_name)

                    line = f"{' '.join(line_segments)} [{percent}]"

            # CASE 2: Keyed Sources (e.g., Quest:123)
            elif ":" in part:
                key, val = part.split(':', 1)
                mapping = SOURCE_LABELS.get(key.strip())
                if mapping:
                    process_mapping(mapping)
                    val_text = self.localization_map.get(val.strip(), val.strip()) if val.strip().startswith('-') else self.get_resolved_name(val.strip())
                    line = f"{' '.join(line_segments)} {val_text}".strip()
                else:
                    line = f"{key}: {self.get_resolved_name(val.strip())}"

            # CASE 3: Simple Strings (fixes HallOfFame when no colon is present)
            if not line:
                mapping = SOURCE_LABELS.get(part)
                if mapping:
                    process_mapping(mapping)
                    line = " ".join(line_segments).strip()
                else:
                    # Final Fallback to Cached Icons
                    xml_icon = self.asset_guid_to_icon.get(part)
                    res_name = self.get_resolved_name(part)
                    line = f"[SIMG:{xml_icon}] {res_name}" if xml_icon else res_name

            if line:
                resolved_lines.append(f"{line}")

        return resolved_lines

    # Shows a legend tooltip for Source icons.
    def show_source_legend(self, event):
        # 1. CLEANUP & INITIALIZE
        if hasattr(self, "target_tooltip") and self.target_tooltip:
            try: self.target_tooltip.destroy()
            except: pass

        self.target_tooltip = tk.Toplevel(self.root)
        self.target_tooltip.wm_overrideredirect(True)

        # Border logic from your target tooltip
        border_color = "#ffd700"
        self.target_tooltip.configure(bg="#1a2e47", highlightbackground=border_color, highlightthickness=2)

        # 2. PREPARE DATA (Deduplicated logic)
        unique_entries = []
        seen_icons = set()
        for mapping_dict in [REWARD_POOL_MAPPING, SOURCE_LABELS]:
            for key, mapping in mapping_dict.items():
                if not mapping or len(mapping) < 2: continue
                icon_path, text_id = mapping[0], mapping[1]
                if icon_path not in seen_icons:
                    raw_loc = self.localization_map.get(text_id, text_id)
                    clean_loc = re.sub(r'<[^>]+>', '', raw_loc).replace("{}", "").strip()
                    if clean_loc and clean_loc != text_id:
                        unique_entries.append(f"• [SIMG:{resource_path(icon_path)}] {clean_loc}")
                        seen_icons.add(icon_path)

        unique_entries.sort()
        header_text = "SOURCE LEGEND:"
        all_lines = [header_text] + unique_entries
        num_total = len(all_lines)

        # 3. CALCULATE WIDTHS
        def get_char_width(text_list):
            if not text_list: return 0
            # Account for the [SIMG] tag being replaced by spaces for measurement
            return max(len(re.sub(r"\[SIMG:.*?\]", "   ", l)) for l in text_list)

        max_w = get_char_width(all_lines)
        total_width = (max_w * 9) + 60

        # 4. CALCULATE HEIGHT
        line_height = 27
        margin_v = 15
        total_height = (num_total * line_height) + margin_v

        # 5. CREATE UI STRUCTURE
        container = tk.Frame(self.target_tooltip, bg="#1a2e47")
        container.pack(fill="both", expand=True)

        tip_content = tk.Text(container, wrap=tk.NONE, bg="#1a2e47", fg="#ffffff", font=FONT_BODY, padx=10, pady=5, borderwidth=0, highlightthickness=0, cursor="arrow")
        tip_content.pack(side=tk.LEFT, fill="both", expand=True)

        # 6. INSERT CONTENT
        # Applying the same spacing logic
        tip_content.tag_configure("legend_style", spacing1=1, spacing3=1)
        tip_content.tag_configure("header_style", font=(FONT_BODY[0], 10, "bold"), foreground="#ffd700")

        # Insert Header separately to give it the gold color
        self.insert_text_with_icons(tip_content, header_text + "\n", ("header_style", "legend_style"))
        # Insert the rest
        remaining_text = "\n".join(unique_entries)
        self.insert_text_with_icons(tip_content, remaining_text, ("legend_style"))

        tip_content.config(state=tk.DISABLED)

        # 7. POSITIONING
        # Ensure it doesn't fall off the screen
        screen_h = self.root.winfo_screenheight()
        x_pos = event.x_root + 10
        y_pos = event.y_root + 10

        if y_pos + total_height > screen_h - 50:
            y_pos = screen_h - total_height - 50

        self.target_tooltip.geometry(f"{int(total_width)}x{int(total_height)}")
        self.target_tooltip.wm_geometry(f"+{x_pos}+{y_pos}")

        # Bind the leave event to close it
        self.target_tooltip.bind("<Leave>", self.hide_target_tooltip)

    # Top Bar Setup
    def setup_top_bar(self):
        top_frame = tk.Frame(self.root, pady=10, padx=10, bg=BG_MAIN)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Create two separate rows
        row1 = tk.Frame(top_frame, bg=BG_MAIN)
        row1.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        row2 = tk.Frame(top_frame, bg=BG_MAIN)
        row2.pack(side=tk.TOP, fill=tk.X)

        # --- ROW 1 ---
        tk.Label(row1, text="Language:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.lang_var = tk.StringVar(value=self.current_language)
        ttk.Combobox(row1, textvariable=self.lang_var, values=LANGUAGES, state="readonly", width=17).pack(side=tk.LEFT, padx=(0, 8))
        self.lang_var.trace("w", lambda *args: self.on_language_change())

        tk.Label(row1, text="Slot:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.alloc_var = tk.StringVar(value="All")
        self.alloc_combo = ttk.Combobox(row1, textvariable=self.alloc_var, state="readonly", width=5)
        self.alloc_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.update_slot_dropdown()
        self.alloc_var.trace("w", lambda *args: self.refresh_table())

        tk.Label(row1, text="Rarity:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.rarity_var = tk.StringVar(value="All")
        self.rarity_combo = ttk.Combobox(row1, textvariable=self.rarity_var, state="readonly", width=10)
        self.rarity_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.update_rarity_dropdown()
        self.rarity_var.trace("w", lambda *args: self.refresh_table())

        tk.Label(row1, text="Niche:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.niche_var = tk.StringVar(value="All")
        self.niche_combo = ttk.Combobox(row1, textvariable=self.niche_var, state="readonly", width=10)
        self.niche_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.update_niche_dropdown()
        self.niche_var.trace("w", lambda *args: self.refresh_table())

        tk.Label(row1, text="Target:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.target_var = tk.StringVar(value="All")
        self.target_combo = ttk.Combobox(row1, textvariable=self.target_var, state="readonly", width=30)
        self.target_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.update_target_list()
        self.target_var.trace("w", lambda *args: self.refresh_table())

        tk.Label(row1, text="Effect:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.effect_var = tk.StringVar(value="All")
        self.effect_combo = ttk.Combobox(row1, textvariable=self.effect_var, state="readonly", width=37)
        self.effect_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.update_effect_dropdown()
        self.effect_var.trace("w", lambda *args: self.refresh_table())

        tk.Label(row1, text="Source:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.source_var = tk.StringVar(value="All")
        self.source_combo = ttk.Combobox(row1, textvariable=self.source_var, state="readonly", width=40)
        self.source_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.update_source_dropdown()
        self.source_var.trace("w", lambda *args: self.refresh_table())

        # --- ROW 2 ---
        tk.Label(row2, text="Search:", bg=BG_MAIN, fg=FG_MAIN, font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 2))
        self.search_var = tk.StringVar()

        # 1. Assign the Entry to self.search_entry
        self.search_entry = tk.Entry(row2, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT)

        # 2. Bind the ENTER key to the ENTRY widget, not the StringVar
        self.search_entry.bind("<Return>", lambda e: self.refresh_table())

        # Dynamic search: fires after 300ms idle, only when ≥3 chars or empty
        self._search_after_id = None
        def on_search_change(*args):
            if self._search_after_id:
                self.root.after_cancel(self._search_after_id)
            query = self.search_var.get()
            if len(query) >= 3 or len(query) == 0:
                self._search_after_id = self.root.after(300, self.refresh_table)

        self.search_var.trace("w", on_search_change)

        # 3. The search button
        search_btn = tk.Button(row2, text="🔍", command=self.refresh_table, bg=BG_SECTION, fg=FG_MAIN, cursor="hand2")
        search_btn.pack(side=tk.LEFT, padx=5)

        # The Clear Button
        clear_btn = tk.Button(row2, text="Clear All", command=self.clear_filters, bg=BG_SECTION, fg=FG_MAIN, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=5)

        # The Default Language Change Button
        lang_btn = tk.Button(row2, text="Default Language", command=self.change_language_request, bg=BG_SECTION, fg="#ffd700", cursor="hand2")
        lang_btn.pack(side=tk.LEFT, padx=5)

        # The Version Filter Button
        self.setup_dlc_filter_button(row2)

        # Ko-fi Button (Right Aligned)
        def open_kofi():
            webbrowser.open("https://ko-fi.com/W7W8L558T")

        kofi_btn = tk.Button(
            row2,
            text="☕ Support me on Ko-fi!",
            command=open_kofi,
            bg="#5F032E",
            fg="white",
            font=("Marcellus", 10),
            relief="flat",
            padx=15,
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        kofi_btn.pack(side=tk.RIGHT, padx=(10, 7), ipady=0)

    # All the dropdown filters
    def update_niche_dropdown(self):
        display_names = []
        self.niche_display_to_raw = {}
        for raw in self.filter_niches_raw:
            loca_val = NICHE_LOCA_MAPPING.get(raw)
            _, name = self.resolve_loca_and_icon(loca_val, raw)
            display_names.append(name)
            self.niche_display_to_raw[name] = raw
        self.niche_combo['values'] = ["All"] + sorted(display_names)

    def update_effect_dropdown(self):
        display_names = []
        self.effect_display_to_raw = {}

        # Extract the target ID: "-6916464905928465879"
        target_add_eff_id = str(ADDITIONAL_EFFECTS_ID[1]).strip() if isinstance(ADDITIONAL_EFFECTS_ID, list) else str(ADDITIONAL_EFFECTS_ID).strip()

        for raw in self.filter_effects_raw:
            raw_str = str(raw).strip()
            if not raw_str: continue

            # 1. SPECIAL CASE: ChangeNeedAttributesOf
            if "ChangeNeedAttributesOf" in raw_str:
                base_key = "ChangeNeedAttributesOf"
                mapping_entry = BUFF_EFFECT_MAPPING.get(base_key)
                if mapping_entry:
                    oid_to_use = str(mapping_entry[1]).strip() if isinstance(mapping_entry, list) else str(mapping_entry).strip()
                    _, name = self.resolve_loca_and_icon(oid_to_use, base_key)
                    clean_name = name.replace("{}", "").replace(":", "").strip()
                    if clean_name not in display_names:
                        display_names.append(clean_name)
                        self.effect_display_to_raw[clean_name] = base_key
                continue # Move to next raw effect

            # Case 2: Additional Effects (OasisID)
            if raw_str == target_add_eff_id:
                _, name = self.resolve_loca_and_icon(ADDITIONAL_EFFECTS_ID, "Additional Effects")
                clean_name = name.replace("{}", "").replace(":", "").strip()
                if clean_name not in display_names:
                    display_names.append(clean_name)
                    self.effect_display_to_raw[clean_name] = target_add_eff_id
                continue

            # 3. Standard Effects
            oid = BUFF_EFFECT_MAPPING.get(raw_str)
            if oid:
                _, name = self.resolve_loca_and_icon(oid, raw_str)
            else:
                name = self.localization_map.get(raw_str, raw_str)

            clean_name = name.replace("{}", "").replace(":", "").strip()
            if clean_name not in display_names:
                display_names.append(clean_name)
                self.effect_display_to_raw[clean_name] = raw_str

        self.effect_combo['values'] = ["All"] + sorted(display_names)

    def update_target_list(self):
        unique_names = set()
        self.target_display_to_guid = {}
        EX_POOLS = ["38995", "26600", "140478", "29318"]
        for item in self.items_data:
            raw_t = item['Targets']
            active_ex = [p for p in EX_POOLS if f"{p}:" in raw_t or raw_t == p]
            raw_f = raw_t.replace('|', ';').replace(':', ';')
            guids = [g.strip() for g in raw_f.split(';') if g.strip()]
            for g in guids:
                if any(g != p for p in active_ex) and g not in EX_POOLS: continue
                name = self.get_resolved_name(g)
                if not name.startswith("Unknown"):
                    unique_names.add(name)
                    self.target_display_to_guid[name] = g
        self.target_combo['values'] = ["All"] + sorted(list(unique_names))

    def update_rarity_dropdown(self):
        display_names = []
        self.rarity_display_to_raw = {}
        for raw in self.filter_rarities:
            loca_id = RARITY_LOCA_MAPPING.get(raw)
            _, name = self.resolve_loca_and_icon(loca_id, raw) if loca_id else raw
            display_names.append(name)
            self.rarity_display_to_raw[name] = raw
        self.rarity_combo['values'] = ["All"] + sorted(display_names)

    def update_slot_dropdown(self):
        display_names = []
        self.alloc_display_to_raw = {}
        for raw in self.filter_allocations:
            loca_id = SLOT_LOCA_MAPPING.get(raw)
            _, name = self.resolve_loca_and_icon(loca_id, raw) if loca_id else raw
            display_names.append(name)
            self.alloc_display_to_raw[name] = raw
        self.alloc_combo['values'] = ["All"] + sorted(display_names)

    def update_source_dropdown(self):
        display_names = []
        # Change this to store LISTS of raw IDs: { "Contracts": ["POOL_123", "POOL_456"], ... }
        self.source_display_to_raw = {}
        clean_pattern = re.compile(r'<[^>]*>|\[S?IMG:[^\]]*\]')

        for raw in self.filter_sources_raw:
            raw_str = str(raw).strip()
            name = ""

            if raw_str.startswith("POOL_"):
                guid = raw_str.replace("POOL_", "")
                mapping = REWARD_POOL_MAPPING.get(guid)
                if mapping and len(mapping) > 1:
                    # Resolve name using the OasisId (mapping[1])
                    name = self.localization_map.get(str(mapping[1]), guid)
            else:
                mapping = SOURCE_LABELS.get(raw_str)
                if mapping and isinstance(mapping, list) and len(mapping) > 1:
                    name = self.localization_map.get(str(mapping[1]), raw_str)
                else:
                    _, name = self.resolve_loca_and_icon(raw_str, raw_str)

            # Final Cleaning
            name = clean_pattern.sub('', str(name))
            name = name.replace(" • ", "").replace(" - ", " ").strip(" -").strip()

            if name:
                if name not in display_names:
                    display_names.append(name)

                # IMPORTANT: Append to a list so "Contracts" holds ALL matching POOL IDs
                if name not in self.source_display_to_raw:
                    self.source_display_to_raw[name] = []

                # Avoid duplicates in the list
                if raw not in self.source_display_to_raw[name]:
                    self.source_display_to_raw[name].append(raw)

        self.source_combo['values'] = ["All"] + sorted(display_names)

    # Sort treeview content when a column header is clicked.
    def sort_column(self, col, reverse):
        # Update state
        self.current_sort_col = col
        self.current_sort_reverse = reverse

        # Get all items currently in the tree
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        # Attempt to sort numerically if it looks like a number (GUID), otherwise string
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(key=lambda t: t[0].lower(), reverse=reverse)

        # Rearrange items in sorted order
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Update headings to show which one is active
        # Reset other headings first
        self.tree.heading("Name", text="Item Name")
        self.tree.heading("GUID", text="GUID")

        # Add arrow to active heading
        arrow = " 🔽" if reverse else " 🔼"
        new_text = ("Item Name" if col == "Name" else "GUID") + arrow
        self.tree.heading(col, text=new_text, command=lambda: self.sort_column(col, not reverse))

    # Filter treeview content by game version
    def setup_dlc_filter_button(self, parent):
        self.dlc_menu = tk.Menu(self.root, tearoff=0, font=FONT_SMALL)

        # We need a cache for menu icons so they don't get garbage collected
        self.menu_icons = {}

        # 1. Add "All Game Versions" (Optional: add a generic icon or keep text only)
        self.dlc_menu.add_command(
            label=" All Game Versions",
            command=lambda: self.set_dlc_filter("all")
        )
        self.dlc_menu.add_separator()

        # 2. Add DLCs with icons
        for key, data in DLC_ICONS.items():
            icon_path = data[0]
            loca_id = data[1]
            display_name = self.localization_map.get(loca_id, key)

            # Load the icon (small size for menu)
            pil_img = self.get_icon_image(icon_path, size=(20, 20))
            if pil_img:
                tk_img = ImageTk.PhotoImage(pil_img)
                self.menu_icons[key] = tk_img # Store reference

                self.dlc_menu.add_command(
                    label=f" {display_name}",
                    image=tk_img,
                    compound=tk.LEFT, # Places image to the left of text
                    command=lambda k=key: self.set_dlc_filter(k)
                )
            else:
                # Fallback if icon fails to load
                self.dlc_menu.add_command(
                    label=f" {display_name}",
                    command=lambda k=key: self.set_dlc_filter(k)
                )

        # The Button that triggers the menu
        self.dlc_btn = tk.Button(parent, text="Version: All ▽", command=self.show_dlc_menu, bg=BG_SECTION, fg=FG_DIM, relief=tk.FLAT, padx=10, cursor="hand2")
        self.dlc_btn.pack(side=tk.LEFT, padx=5)

    def setup_dlc_filter(self, parent_frame):
        # Create the Popup Menu
        self.dlc_menu = tk.Menu(self.root, tearoff=0, font=FONT_SMALL, bg=BG_MAIN, fg=FG_DIM)

        # Add "Show All" option
        self.dlc_menu.add_command(label="Show All Versions", command=lambda: self.set_dlc_filter("all"))
        self.dlc_menu.add_separator()

        # Dynamically add DLCs from your mapping
        for key, data in DLC_ICONS.items():
            loca_id = data[1]
            # Resolve the name using your existing localization map
            display_name = self.localization_map.get(loca_id, key)

            # Use a closure to capture the key correctly in the loop
            self.dlc_menu.add_command(
                label=display_name,
                command=lambda k=key: self.set_dlc_filter(k)
            )

        # Create the Button
        self.dlc_btn = tk.Button(
            parent_frame, text="Game Version ▽",
            command=self.show_dlc_menu,
            bg=BG_MAIN, fg=FG_DIM, relief=tk.FLAT
        )
        self.dlc_btn.pack(side=tk.LEFT, padx=5)

    def show_dlc_menu(self):
        x = self.dlc_btn.winfo_rootx()
        y = self.dlc_btn.winfo_rooty() + self.dlc_btn.winfo_height()
        self.dlc_menu.post(x, y)

    def set_dlc_filter(self, key):
        self.current_dlc_filter = key

        self.refresh_table()

    def get_dlc_counts(self, current_filtered_items):
        # Initialize counts for all keys in your mapping + "all"
        counts = {k: 0 for k in DLC_ICONS.keys()}
        counts["all"] = len(current_filtered_items)

        # Get keys to check against (everything except base)
        dlc_keys = [k for k in DLC_ICONS.keys() if k != "base"]

        for item in current_filtered_items:
            path = str(item.get('Icon', '')).lower().replace('\\', '/')
            found_dlc = False

            for dlc in dlc_keys:
                if f"/{dlc}/" in path:
                    counts[dlc] += 1
                    found_dlc = True
                    break

            if not found_dlc:
                counts["base"] += 1

        return counts

    def update_dlc_menu_labels(self, counts):
        try:
            # Update "All Game Versions"
            self.dlc_menu.entryconfigure(0, label=f"All Game Versions ({counts['all']})")

            idx = 2
            for key in DLC_ICONS.keys():
                loca_id = DLC_ICONS[key][1]
                display_name = self.localization_map.get(loca_id, key)
                val = counts.get(key, 0)

                # Update text with count
                self.dlc_menu.entryconfigure(idx, label=f" {display_name} ({val})")

                # Disable the menu item if count is 0
                if val == 0:
                    self.dlc_menu.entryconfigure(idx, state="disabled")
                else:
                    self.dlc_menu.entryconfigure(idx, state="normal")

                idx += 1
        except Exception as e:
            pass # Keep UI stable if index drifts

    # Reset dropdowns to "All"
    def clear_filters(self):
        self.rarity_var.set("All")
        self.alloc_var.set("All")
        self.target_var.set("All")
        self.niche_var.set("All")
        self.effect_var.set("All")
        self.source_var.set("All")

        # Clear search bar
        self.search_var.set("")

        # Reset Version/DLC Filter
        self.current_dlc_filter = "all"

        # Refresh the table with the reset values
        self.root.after_idle(self.refresh_table)

    #Draws the offset gradient background with 128x128 icon considerations, and the new text fields.
    def draw_header_gradient(self, hex_color, rarity_raw, name, desc):
        self.header_canvas.delete("all")
        self.header_canvas.update_idletasks()
        width = self.header_canvas.winfo_width()
        height = 160
        if width <= 1: width = 800

        offset = 150 # Start gradient right after the 128x128 icon padding

        try:
            r1, g1, b1 = self.root.winfo_rgb(hex_color)
            r2, g2, b2 = self.root.winfo_rgb(BG_MAIN)

            # Solid dark blue under the icon
            self.header_canvas.create_rectangle(0, 0, offset, height, fill=BG_MAIN, outline="")

            # Blend from rarity color to dark blue
            if width > offset:
                r_ratio = (r2 - r1) / (width - offset)
                g_ratio = (g2 - g1) / (width - offset)
                b_ratio = (b2 - b1) / (width - offset)

                for i in range(offset, width):
                    nr = int(r1 + (r_ratio * (i - offset)))
                    ng = int(g1 + (g_ratio * (i - offset)))
                    nb = int(b1 + (b_ratio * (i - offset)))
                    color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"
                    self.header_canvas.create_line(i, 0, i, height, fill=color)
        except Exception:
            self.header_canvas.create_rectangle(0, 0, width, height, fill=hex_color)

        # Header Details: Rarity, Name, Description
        self.header_canvas.create_text(160, 20, anchor="nw", text=name, font=FONT_TITLE, fill=FG_MAIN, width=width-180)
        self.header_canvas.create_text(160, 75, anchor="nw", text=desc, font=FONT_DESC, fill=FG_MAIN, width=width-200)
        self.header_canvas.create_text(160, 130, anchor="nw", text=rarity_raw.upper(), font=FONT_UI_BOLD, fill=FG_MAIN)

    # Setup main layout
    def _disable_separator_drag(self, event):
        """Prevents users from dragging Treeview column separators."""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"

    def _disable_sash_drag(self, event):
        # Identify what part of the PanedWindow was clicked
        # "sash" refers to the divider between panes
        if "sash" in self.main_paned.identify(event.x, event.y):
            return "break"

    def setup_main_layout(self):
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BG_MAIN, sashwidth=0, sashpad=0, borderwidth=0, handlepad=0, handlesize=0)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        self.main_paned.bind("<Button-1>", self._disable_sash_drag)
        self.main_paned.bind("<B1-Motion>", self._disable_sash_drag)

        # LEFT SIDE: Treeview and Filters
        left_side = tk.Frame(self.main_paned, bg=BG_MAIN)
        # Reducing default width slightly to ensure right side has space on smaller screens
        self.main_paned.add(left_side, width=600, minsize=600, stretch="always")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=BG_MAIN, foreground=FG_MAIN, fieldbackground=BG_MAIN, font=FONT_SMALL, rowheight=40, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_SECTION, foreground=FG_MAIN, font=FONT_UI_BOLD, borderwidth=1)
        style.map("Treeview", background=[('selected', BG_SECTION)])

        scroll = tk.Scrollbar(left_side, bg=BG_MAIN, activebackground=BG_SECTION, troughcolor=BG_MAIN)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(left_side, columns=("Name", "GUID"), yscrollcommand=scroll.set, style="Treeview")
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=55, anchor='center', stretch=tk.NO)

        # Define headings with initial icons
        guid_text = "GUID" + (" 🔽" if self.current_sort_reverse else " 🔼")
        name_text = "Item Name" # No arrow yet
        self.tree.heading("Name", text=name_text, command=lambda: self.sort_column("Name", False), anchor='w')
        self.tree.column("Name", width=365, anchor='w', stretch=tk.YES)
        self.tree.heading("GUID", text=guid_text, command=lambda: self.sort_column("GUID", False))
        self.tree.column("GUID", width=90, anchor='center', stretch=tk.NO)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # --- DISABLE COLUMN RESIZING ---
        self.tree.bind('<Button-1>', self._disable_separator_drag, add='+')
        self.tree.bind('<Motion>', self._disable_separator_drag, add='+')

        # Create a context menu for the Treeview
        self.tree_menu = tk.Menu(self.tree, tearoff=0, bg=BG_SECTION, fg=FG_MAIN)
        self.tree_menu.add_command(label="Copy Name", command=self.copy_tree_name)
        self.tree_menu.add_command(label="Copy GUID", command=self.copy_tree_guid)

        # Bind right-click
        self.tree.bind("<Button-3>", lambda e: self.tree_menu.post(e.x_root, e.y_root))

        # RIGHT SIDE: Detail Panel
        self.detail_container = tk.Frame(self.main_paned, bg=BG_MAIN)
        self.main_paned.add(self.detail_container, width=850 , stretch="never")

        # Header Canvas stays at top
        self.header_canvas = tk.Canvas(self.detail_container, bg=BG_MAIN, height=160, highlightthickness=0)
        self.header_canvas.pack(fill=tk.X, padx=0, pady=0)

        # PACK SCROLLBAR BEFORE TEXT
        v_scroll = tk.Scrollbar(self.detail_container, orient=tk.VERTICAL,
                                bg=BG_MAIN, activebackground=BG_SECTION,
                                troughcolor=BG_MAIN, bd=0, highlightthickness=0)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_text = tk.Text(
            self.detail_container, bg=BG_MAIN, fg=FG_MAIN,
            font=FONT_BODY, wrap=tk.NONE, padx=15, pady=10, borderwidth=0,
            insertbackground=FG_MAIN,
            yscrollcommand=v_scroll.set,
            insertofftime=0,
            state=tk.DISABLED
        )
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scroll.config(command=self.details_text.yview)

        # Tags Configuration
        # Using 780 as the right-anchor to match your target width
        self.details_text.tag_configure("effect_line", font=FONT_BODY, foreground="#e0eaff", tabs=("780", "right"))
        self.details_text.tag_configure("effect_line_indented", font=FONT_BODY, foreground="#e0eaff", tabs=("40", "left", "780", "right"))

        # Source tag updated for the split column logic
        self.details_text.tag_configure("source_line_split", font=FONT_BODY, foreground="#ffffff", tabs=("400", "left"))
        self.details_text.tag_configure("source_header", font=FONT_HEADER, foreground="#ffffff")

        self.details_text.tag_configure("single_targets", font=FONT_UI_BOLD)
        self.details_text.tag_configure("section_bg", background=BG_SECTION)
        self.details_text.tag_configure("half_space", font=FONT_HALF_SPACE)
        self.details_text.tag_configure("multiple_targets", font=FONT_UI_BOLD, foreground="#6ab1ff", underline=True)

    # Right click copy GUID/Name in the right panel
    def copy_tree_name(self):
        selected = self.tree.selection()
        if selected:
            name = self.tree.item(selected[0])['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(name)

    def copy_tree_guid(self):
        selected = self.tree.selection()
        if selected:
            guid = self.tree.item(selected[0])['values'][1]
            self.root.clipboard_clear()
            self.root.clipboard_append(guid)

    # LOGIC for Language change
    def on_language_change(self, event=None):
        # Prevent overlapping calls
        if getattr(self, '_language_swap_in_progress', False):
            return
        self._language_swap_in_progress = True

        # 1. Capture current state immediately
        selected = self.tree.selection()
        current_guid = selected[0] if selected else None

        # 1.1 Determine if we are doing a Hard Reset BEFORE we start changing things
        is_hard_reset = not os.path.exists(CONFIG_FILE)
        if is_hard_reset:
            new_lang = self.get_or_set_language()
            # If the user closed the window without picking, get_or_set_language
            self.current_language = new_lang.lower()
            if hasattr(self, 'lang_var'):
                # We update the internal variable without triggering logic
                self.lang_var.set(new_lang.title())

        # 2. CREATE LOADING OVERLAY
        # This frame covers everything, including the area where the dropdown was
        self.root.config(cursor="watch")
        self.overlay = tk.Frame(self.root, bg=BG_MAIN)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        msg = "Setting Language..." if is_hard_reset else "Changing Language..."
        tk.Label(self.overlay, text=f"{msg}\nPlease wait!", font=FONT_HEADER, fg=FG_MAIN, bg=BG_MAIN).place(relx=0.5, rely=0.5, anchor="center")

        # 3. Schedule the heavy work for 100ms from now
        # This gives the OS/Tkinter time to hide the dropdown and draw the overlay
        self.root.update()
        self.root.after(100, lambda: self._execute_language_swap(current_guid))

    def _execute_language_swap(self, current_guid):
        """Internal method to handle the heavy processing"""
        try:
            # 1. Capture current filter state before reloading
            current_rarity_raw = self.rarity_display_to_raw.get(self.rarity_var.get())
            current_alloc_raw = self.alloc_display_to_raw.get(self.alloc_var.get())
            current_target_guid = self.target_display_to_guid.get(self.target_var.get())
            current_niche_raw = self.niche_display_to_raw.get(self.niche_var.get())
            current_eff_raw = self.effect_display_to_raw.get(self.effect_var.get())
            current_source_raw = self.source_display_to_raw.get(self.source_var.get())

            # 2. Sync the language variable (in case it wasn't set in on_language_change)
            self.current_language = self.lang_var.get().lower()

            # Clear Cache
            self.name_resolution_cache = {}

            # 3. Perform the actual data reload
            self.load_localization(self.current_language)

            # Rebuild dropdown lists
            self.update_target_list()
            self.update_effect_dropdown()
            self.update_source_dropdown()
            self.update_niche_dropdown()
            if hasattr(self, 'update_rarity_dropdown'): self.update_rarity_dropdown()
            if hasattr(self, 'update_slot_dropdown'): self.update_slot_dropdown()

            # 4. RESTORE STATE
            def restore_selection(var, mapping, raw_val):
                if raw_val:
                    # Find the localized name that matches the original raw ID
                    new_name = next((name for name, raw in mapping.items() if raw == raw_val), "All")
                    var.set(new_name)
                else:
                    var.set("All")

            restore_selection(self.rarity_var, self.rarity_display_to_raw, current_rarity_raw)
            restore_selection(self.alloc_var, self.alloc_display_to_raw, current_alloc_raw)
            restore_selection(self.target_var, self.target_display_to_guid, current_target_guid)
            restore_selection(self.niche_var, self.niche_display_to_raw, current_niche_raw)
            restore_selection(self.effect_var, self.effect_display_to_raw, current_eff_raw)
            restore_selection(self.source_var, self.source_display_to_raw, current_source_raw)

            # Refresh
            self.refresh_table()

            # Restore selection in Treeview
            if current_guid and self.tree.exists(current_guid):
                self.tree.selection_set(current_guid)
                self.tree.see(current_guid)
                self.on_item_select(None)

        except Exception as e:
            import traceback
            traceback.print_exc()
        finally:
            # A more robust cleanup
            if hasattr(self, 'overlay') and self.overlay:
                for child in self.overlay.winfo_children():
                    child.destroy()
                self.overlay.destroy()

            self.overlay = None
            self.root.config(cursor="")
            self.root.update()

            # Release the lock so future swaps can happen
            self._language_swap_in_progress = False

    # LOGIC for what happens on a table refresh - when filtering, changing language, selecting another item
    def refresh_table(self):
        # 1. CAPTURE CURRENT SELECTION
        selected = self.tree.selection()
        prev_selected_guid = selected[0] if selected else None

        # Clear current view
        for item in self.tree.get_children(): self.tree.delete(item)

        pre_dlc_list = []      # Items that pass search/rarity/etc. (Used for counts)
        filtered_items = []    # Final items to show in the table

        # 2. Get all current filter values
        rarity_disp = self.rarity_var.get()
        rarity_raw_filter = self.rarity_display_to_raw.get(rarity_disp)
        alloc_disp = self.alloc_var.get()
        alloc_raw_filter = self.alloc_display_to_raw.get(alloc_disp)
        target_name = self.target_var.get()
        target_guid_filter = self.target_display_to_guid.get(target_name)
        niche_disp = self.niche_var.get()
        niche_raw_filter = self.niche_display_to_raw.get(niche_disp)
        eff_disp = self.effect_var.get()
        eff_raw_filter = self.effect_display_to_raw.get(eff_disp)
        source_name = self.source_var.get()
        s_query = self.search_var.get().strip().lower()

        # 3. Filter Logic
        for item in self.items_data:

            is_dlc_match = True

            # Dropdown filters
            if rarity_disp != "All" and item['Rarity'] != rarity_raw_filter: continue
            if alloc_disp != "All" and item['Allocation'] != alloc_raw_filter: continue
            if niche_disp != "All" and item['Niche'] != niche_raw_filter: continue

            if target_name != "All":
                t_guids = item['Targets'].replace('|', ';').replace(':', ';').split(';')
                if target_guid_filter not in [t.strip() for t in t_guids]: continue

            if eff_disp != "All" and eff_raw_filter is not None:
                # 1. Gather all raw strings from the effect columns
                raw_eff_str = (item.get('Buff Effects', '') + "|" +
                            item.get('BoostBuff Effects', '') + "|" +
                            item.get('Effects', '')).strip()

                target_add_eff_id = ADDITIONAL_EFFECTS_ID[1] if isinstance(ADDITIONAL_EFFECTS_ID, list) else ADDITIONAL_EFFECTS_ID
                parts = [p.strip() for p in raw_eff_str.split('|') if p.strip()]

                item_search_terms = []
                for p in parts:
                    # Extract the base key (ID or main string)
                    # Handles "Key: Value" or "ID Value"
                    base_key = re.split(r'[:\s]', p)[0].strip()
                    item_search_terms.append(base_key.lower())

                    # --- Case A: ChangeNeedAttributesOf (Already working) ---
                    if "ChangeNeedAttributesOf" in p:
                        try:
                            attr_id = p.split(":")[-1].strip().split()[0]
                            item_search_terms.append(attr_id.lower())
                        except: pass

                    # --- Case B: Additional Effects (The "Merge" Logic) ---
                    # Matches: "-6916464905928465879 FireSafety: +1"
                    elif base_key == target_add_eff_id:
                        try:
                            sub_parts = p.split()
                            if len(sub_parts) > 1:
                                # 1. Get the attribute name (e.g., "FireSafety")
                                # rstrip(':') removes the colon if it exists
                                attr_key = sub_parts[1].rstrip(':').strip()

                                # 2. Look it up in BUFF_EFFECT_MAPPING to get its GUID
                                # This is what allows it to merge with the "Standard" filter
                                mapping_val = BUFF_EFFECT_MAPPING.get(attr_key)

                                if mapping_val:
                                    # Resolve GUID from [icon, GUID] or raw GUID
                                    resolved_guid = str(mapping_val[1] if isinstance(mapping_val, list) else mapping_val).strip()
                                    item_search_terms.append(resolved_guid.lower())
                                    # Also add the raw name as a fallback
                                    item_search_terms.append(attr_key.lower())
                                else:
                                    # If not in mapping, just add the word "FireSafety"
                                    item_search_terms.append(attr_key.lower())
                        except: pass

                # 3. Final Comparison
                # eff_raw_filter is the GUID/Key from the dropdown
                filter_val = str(eff_raw_filter).lower()
                if filter_val not in item_search_terms:
                    continue

            if source_name != "All":
                # Use the string 'source_name' as the key to get the list of IDs
                allowed_ids = self.source_display_to_raw.get(source_name, [])

                # Safety check: ensure it's a list
                if not isinstance(allowed_ids, list):
                    allowed_ids = [allowed_ids]

                item_source_raw = item.get('Source', '')
                source_parts = [p.strip() for p in item_source_raw.split('|') if p.strip()]

                found_source = False
                for p in source_parts:
                    if "[" in p and "]" in p:
                        item_raw_id = f"POOL_{p.split('[')[0].strip()}"
                    else:
                        item_raw_id = p.split(':', 1)[0].strip()

                    # Check if this item's source ID is in our list of allowed IDs
                    if item_raw_id in allowed_ids:
                        found_source = True
                        break

                if not found_source:
                    continue

            # Resolve name for search and display
            raw_name = self.get_resolved_name(item['GUID'])
            if raw_name.startswith("Unknown"): continue

            # Search query logic
            if s_query:
                found_match = False

                # 1. NUMBER SEARCH: Strictly filter by GUID prefix
                if s_query.isdigit():
                    if item['GUID'].startswith(s_query):
                        found_match = True
                else:
                    # 2. NAME MATCH
                    if s_query in raw_name.lower():
                        found_match = True

                    # 3. CATEGORY MATCH (Compare against Localized UI text)
                    if not found_match:
                        raw_niche = item.get('Niche', '')
                        niche_val = NICHE_LOCA_MAPPING.get(raw_niche)
                        _, loc_niche = self.resolve_loca_and_icon(niche_val, raw_niche)

                        raw_rarity = item.get('Rarity', '')
                        rar_id = RARITY_LOCA_MAPPING.get(raw_rarity)
                        loc_rarity = self.localization_map.get(rar_id, raw_rarity) if rar_id else raw_rarity

                        raw_alloc = item.get('Allocation', '')
                        alloc_val = SLOT_LOCA_MAPPING.get(raw_alloc)
                        _, loc_alloc = self.resolve_loca_and_icon(alloc_val, raw_alloc)

                        # Using 'in' allows partial matching (e.g., "civic" finds "Civic Buildings")
                        if (s_query in loc_niche.lower() or
                            s_query in loc_rarity.lower() or
                            s_query in loc_alloc.lower()):
                            found_match = True

                    # 4. CONTENT MATCH (Targets, Sources, Effects)
                    if not found_match:
                        # 4a. Targets (Translate GUIDs to readable names)
                        target_raw = item.get('Targets', '')
                        if target_raw and target_raw != "None":
                            t_guids = target_raw.replace('|', ';').replace(':', ';').split(';')
                            resolved_targets = " ".join([self.get_resolved_name(g.strip()).lower() for g in t_guids if g.strip()])
                            if s_query in resolved_targets:
                                found_match = True

                    if not found_match:
                        # 4b. Sources (Translate source formatting to readable text)
                        source_raw = item.get('Source', '')
                        if source_raw and source_raw != "None":
                            res_sources = " ".join(self.resolve_source(source_raw)).lower()
                            if s_query in res_sources:
                                found_match = True

                    if not found_match:
                        # 4c. Effects (Check raw text AND localized dropdown names)
                        eff_raw = (item.get('Buff Effects', '') + "|" + item.get('BoostBuff Effects', '')).strip()
                        if eff_raw and eff_raw != "None":
                            if s_query in eff_raw.lower():
                                found_match = True
                            else:
                                # Check if the search term matches the localized name of the effect
                                for disp_name, raw_id in getattr(self, 'effect_display_to_raw', {}).items():
                                    if s_query in disp_name.lower() and raw_id in eff_raw:
                                        found_match = True
                                        break

                # If after all checks we found nothing, skip this item
                if not found_match:
                    continue

            # If it reached here, it passed all text/dropdown filters!
            pre_dlc_list.append(item)

            # DLC / VERSION FILTER
            if self.current_dlc_filter != "all":
                raw_path = str(item.get('Icon', '')).lower().replace('\\', '/')

                if self.current_dlc_filter == "base":
                    # Dynamic check against your DLC_ICONS mapping
                    other_dlcs = [k for k in DLC_ICONS.keys() if k != "base"]
                    if any(f"/{tag}/" in raw_path for tag in other_dlcs):
                        is_dlc_match = False
                else:
                    # Specific DLC check
                    if f"/{self.current_dlc_filter}/" not in raw_path and not raw_path.startswith(f"{self.current_dlc_filter}/"):
                        is_dlc_match = False

            # Now this is safe because is_dlc_match is guaranteed to exist
            if is_dlc_match:
                filtered_items.append(item)

        # UPDATE MENU LABELS (Do this ONCE after the loop finishes)
        counts = self.get_dlc_counts(pre_dlc_list)
        # Update the main button text with the current selection and its count
        current_count = counts.get(self.current_dlc_filter, 0)
        display_name = "All" if self.current_dlc_filter == "all" else self.current_dlc_filter.upper()
        # Update the button text dynamically
        if self.current_dlc_filter != "all" and self.current_dlc_filter in self.menu_icons:
             self.dlc_btn.config(text=f" {display_name} ({current_count}) ▽", image=self.menu_icons[self.current_dlc_filter], compound=tk.LEFT)
        else:
             self.dlc_btn.config(text=f"Version: {display_name} ({current_count}) ▽", image="")
        self.update_dlc_menu_labels(counts)

        # 4. PERSISTENT SORTING LOGIC
        if self.current_sort_col == "GUID":
            filtered_items.sort(
                key=lambda x: int(x['GUID']) if x['GUID'].isdigit() else 0,
                reverse=self.current_sort_reverse
            )
        else: # Sort by Name
            filtered_items.sort(
                key=lambda x: self.get_resolved_name(x['GUID']).lower(),
                reverse=self.current_sort_reverse
            )

        # 5. RENDER LOGIC
        for item in filtered_items:
            current_guid = item['GUID']
            photo = self.icon_cache.get(current_guid + "_small")
            if not photo:
                icon_pil = self.get_icon_image(item['Icon'], size=(36, 36))
                if icon_pil:
                    photo = ImageTk.PhotoImage(icon_pil)
                    self.icon_cache[current_guid + "_small"] = photo

            res_name = self.get_resolved_name(current_guid)

            # Insert the item
            self.tree.insert("", tk.END, iid=current_guid, text="", image=photo, values=(res_name, current_guid))

        # 6. RESTORE SELECTION
        if prev_selected_guid and self.tree.exists(prev_selected_guid):
            self.tree.selection_set(prev_selected_guid)
            self.tree.see(prev_selected_guid)

    # Resolve Boost Condition to OasisIds
    def resolve_boost_condition(self, raw_condition):
        if not raw_condition or raw_condition == "None": return ""

        def resolve_all_guids(text):
            def r_g(m):
                g = m.group(0)
                if len(g.replace('-', '')) < 4: return g
                if g in MANUAL_GUID_MAP:
                    oid = MANUAL_GUID_MAP[g]
                    if isinstance(oid, list):
                        return " ".join([self.localization_map.get(o, o).replace("{}", "").strip() for o in oid])
                    return self.localization_map.get(oid, oid).replace("{}", "").strip()
                res = self.get_resolved_name(g)
                return res if not res.startswith("Unknown") else g
            return re.sub(r'(?<![+\d\-.])\b-?\d{4,20}\b(?![%])', r_g, str(text))

        parts = [p.strip() for p in raw_condition.split('|') if p.strip()]
        resolved_parts = []

        is_complex_condition = any(
            m in raw_condition for m in list(MODULE_MAPPING.keys()) +
            ["ConditionEmperorRelation", "ConditionDiplomacyState"] +
            list(CONDITION_LOCATIONS.keys())
        )

        for part in parts:
            if ":" in part:
                left, right = part.split(':', 1)
                left, right = left.strip(), right.strip()

                loc_label = ""
                if left == "ConditionPlayerCounter": loc_label = ""
                elif left in CONDITION_TYPES: loc_label = self.resolve_oasis_list(CONDITION_TYPES[left])
                elif left in MODULE_MAPPING: loc_label = self.resolve_oasis_list(MODULE_MAPPING[left])
                else: loc_label = resolve_all_guids(left)

                if loc_label: loc_label = loc_label.replace("{}", "").rstrip(':').strip()

                for comp, symbol in COMPARE_OPS.items(): right = right.replace(comp, symbol)

                if "ConditionEmperorRelation" in left:
                    for k, v in EMPEROR_RELATION_VALUES.items():
                        if k in right: right = right.replace(k, self.resolve_oasis_list(v))
                elif "ConditionDiplomacyState" in left:
                    for k, v in DIPLOMACY_STATE_VALUES.items():
                        if k in right: right = right.replace(k, self.resolve_oasis_list(v))

                if left == "ConditionReligion" and right.strip() == "0":
                    right = self.resolve_oasis_list(RELIGION_ZERO_ID)

                if "PopulationByGroup" in right:
                    right = right.replace("PopulationByGroup", "").strip()

                if "GoodsInStock" in right:
                    loc_storage = self.resolve_oasis_list(STORAGE_LOCA_ID).replace("{}", "").strip()
                    right = right.replace("GoodsInStock", loc_storage).strip()

                for attr_key, attr_oid in CONDITION_ATTRIBUTES.items():
                    if attr_key in right:
                        loc_attr = self.resolve_oasis_list(attr_oid)
                        if attr_key == "IslandsDiscovered":
                            loc_attr = re.sub(r'\{.*?\}|/', '', loc_attr).strip()
                        right = re.sub(r'\b' + re.escape(attr_key) + r'\b', loc_attr, right)

                right = resolve_all_guids(right)
                if loc_label: resolved_parts.append(f"{loc_label}: {right}")
                else: resolved_parts.append(right)
            else:
                sub_parts = [sp.strip() for sp in part.split(',')]
                res_sub = []
                for sp in sub_parts:
                    if sp in CONDITION_LOCATIONS: res_sub.append(self.resolve_oasis_list(CONDITION_LOCATIONS[sp]))
                    elif sp in MODULE_MAPPING: res_sub.append(self.resolve_oasis_list(MODULE_MAPPING[sp]).replace("{}", "").strip())
                    else: res_sub.append(resolve_all_guids(sp))
                resolved_parts.append(" ".join(res_sub))

        joiner = " | " if is_complex_condition else " "
        return joiner.join([p for p in resolved_parts if p])

    # Target hover tooltip for multi-target items. Pins it on click. Supports scrolling and 2 columns.
    def show_target_tooltip(self, event, sub_targets, pinned=False):
        if not sub_targets: return

        # If we just moved from one target to another, stop the 'actually_hide' task from the previous target immediately.
        if hasattr(self, "_hide_timer") and self._hide_timer:
            self.root.after_cancel(self._hide_timer)
            self._hide_timer = None

        # If already pinned, don't let a hover event overwrite it
        if getattr(self, "tooltip_pinned", False) and not pinned:
            return

        # Setup state
        self.tooltip_pinned = pinned

        # Cleanup existing window
        if hasattr(self, "target_tooltip") and self.target_tooltip:
            try: self.target_tooltip.destroy()
            except: pass

        self.target_tooltip = tk.Toplevel(self.root)
        self.target_tooltip.wm_overrideredirect(True)

        # Color coding: Gold for pinned, standard blue/grey for hover
        border_color = "#ffd700" if pinned else "#4a90e2"
        self.target_tooltip.configure(bg="#1a2e47", highlightbackground=border_color, highlightthickness=2)

        # 1. PREPARE DATA
        clean_text = sub_targets.strip()
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        num_total = len(lines)
        max_visible_rows = 20

        if num_total > max_visible_rows:
            is_split = True
            num_actual_rows = (num_total + 1) // 2
            left_col = lines[:num_actual_rows]
            right_col = lines[num_actual_rows:]
            display_rows = max_visible_rows
        else:
            is_split = False
            num_actual_rows = num_total
            display_rows = num_total

        # 2. CALCULATE WIDTHS
        def get_width(text_list):
            if not text_list: return 0
            return max(len(re.sub(r"\[SIMG:.*?\]", "   ", l)) for l in text_list)

        if is_split:
            max_l = get_width(left_col)
            max_r = get_width(right_col)
            col_width_px = (max_l * 9) + 50
            total_width = col_width_px + (max_r * 9) + 70
        else:
            max_w = get_width(lines)
            total_width = (max_w * 9) + 60
            col_width_px = 0

        # 3. CREATE UI
        line_height = 25
        header_height = 30 if pinned else 0
        margin_v = 15
        total_height = (min(display_rows, num_actual_rows) * line_height) + margin_v + header_height

        container = tk.Frame(self.target_tooltip, bg="#1a2e47")
        container.pack(fill="both", expand=True)

        if pinned:
            bar = tk.Frame(container, bg="#0d1b2a")
            bar.pack(side=tk.TOP, fill=tk.X)
            tk.Label(bar, text=" Pinned Asset Pool", bg="#0d1b2a", fg="#ffd700", font=(FONT_BODY[0], 9, "bold")).pack(side=tk.LEFT)
            close_btn = tk.Label(bar, text="× ", bg="#0d1b2a", fg="#ffd700", font=("Arial", 14, "bold"), cursor="hand2")
            close_btn.pack(side=tk.RIGHT)
            close_btn.bind("<Button-1>", lambda e: self.close_pinned_tooltip())

        tip_content = tk.Text(
            container, wrap=tk.NONE, bg="#1a2e47", fg="#ffffff", font=FONT_BODY,
            padx=10, pady=5, borderwidth=0, highlightthickness=0, cursor="arrow"
        )

        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=tip_content.yview)
        tip_content.configure(yscrollcommand=scrollbar.set)

        if num_actual_rows > max_visible_rows:
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tip_content.pack(side=tk.LEFT, fill="both", expand=True)

        # 4. INSERT TEXT
        if is_split:
            tip_content.tag_configure("multi_col", tabs=(col_width_px,), spacing1=0, spacing3=0)
            combined_text = ""
            for i in range(num_actual_rows):
                l_item = left_col[i]
                r_item = right_col[i] if i < len(right_col) else ""
                combined_text += f"{l_item}\t{r_item}\n"
            self.insert_text_with_icons(tip_content, combined_text.strip(), ("multi_col"))
        else:
            tip_content.tag_configure("single_col", spacing1=0, spacing3=0)
            self.insert_text_with_icons(tip_content, clean_text, ("single_col"))

        tip_content.config(state=tk.DISABLED)

        # 5. POSITIONING & EVENTS
        self.target_tooltip.geometry(f"{int(total_width)}x{int(total_height)}")
        self.target_tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        if pinned:
            self.target_tooltip.focus_set()
            self.target_tooltip.bind("<FocusOut>", lambda e: self.close_pinned_tooltip())
        else:
            # Hover bridge logic
            self.target_tooltip.bind("<Enter>", self._on_tooltip_enter)
            self.target_tooltip.bind("<Leave>", self.hide_target_tooltip)

    def close_pinned_tooltip(self):
        self.tooltip_pinned = False
        if hasattr(self, "target_tooltip") and self.target_tooltip:
            self.target_tooltip.destroy()
            self.target_tooltip = None

    def hide_target_tooltip(self, event=None):
        if getattr(self, "tooltip_pinned", False):
            return
        if hasattr(self, "_hide_timer") and self._hide_timer:
            try:
                self.root.after_cancel(self._hide_timer)
            except:
                pass
        self._hide_timer = self.root.after(100, self._actually_hide)

    def _on_tooltip_enter(self, event):
        if hasattr(self, "_hide_timer") and self._hide_timer:
            self.root.after_cancel(self._hide_timer)
            self._hide_timer = None

    def _actually_hide(self):
        if hasattr(self, "target_tooltip") and self.target_tooltip:
            x, y = self.root.winfo_pointerxy()
            widget_under_mouse = self.root.winfo_containing(x, y)

            if widget_under_mouse and str(widget_under_mouse).startswith(str(self.target_tooltip)):
                self._hide_timer = None
                return

            self.target_tooltip.destroy()
            self.target_tooltip = None

        self._hide_timer = None

    # Helper to split Target GUIDs and resolve names with variant preservation.
    def get_target_info(self, group):
        SFX = ["-6903427160198155951", "154567"]

        def get_variant_name(name, count):
            if count == 0: return name
            sid = SFX[count-1] if (count-1) < len(SFX) else None
            return f"{name} ({self.localization_map.get(sid, sid).strip()})" if sid else f"{name} ({count+1})"

        if ":" in group:
            p_guid, m_str = group.split(":", 1)
            p_name = self.get_resolved_name(p_guid)

            sub_guids = [m.strip() for m in m_str.split(";") if m.strip()]
            resolved_sub_targets = []
            counts = {}

            for m_guid in sub_guids:
                m_name = self.get_resolved_name(m_guid)
                if m_name.startswith("Unknown"): continue

                c = counts.get(m_name, 0)
                v_name = get_variant_name(m_name, c)
                counts[m_name] = c + 1

                icon_path = self.get_target_icon(m_guid)
                # Ensure each line is its own discrete unit
                icon_tag = f"[SIMG:{icon_path}] " if icon_path else "• "
                resolved_sub_targets.append(f"{icon_tag}{v_name}")

            # .strip() prevents the parser from seeing an extra line at the end
            return p_name, "\n".join(sorted(resolved_sub_targets)).strip()

        p_name = self.get_resolved_name(group)
        return (p_name if not p_name.startswith("Unknown") else group), ""

    # Get and render icon for the target before the target text
    def get_target_icon(self, guid, is_ship=False):
        # 1. Ship override: Use fixed icon for GUID 500465
        if is_ship:
            return self.asset_guid_to_icon.get("500465", "")

        # 2. Multi-target AssetPool check: If it contains a ':', return "" for main view
        if ":" in str(guid):
            return ""

        # 3. Standard inheritance lookup for single GUIDs
        guid_str = str(guid).strip()
        current_guid = guid_str
        visited = set()

        while current_guid:
            if current_guid in visited: break
            visited.add(current_guid)

            icon = self.asset_guid_to_icon.get(current_guid, "")
            if icon: return icon

            # Check for AssetPool fallback if no direct icon
            first_child_guid = self.asset_pool_first_item.get(current_guid)
            if first_child_guid:
                child_current = first_child_guid
                child_visited = set()
                while child_current:
                    if child_current in child_visited: break
                    child_visited.add(child_current)
                    child_icon = self.asset_guid_to_icon.get(child_current, "")
                    if child_icon: return child_icon
                    child_current = self.inheritance_lookup.get(child_current)

            current_guid = self.inheritance_lookup.get(current_guid)
        return ""

    # Main Logic of what happens when you click on an item in the left panel
    def on_item_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        guid = sel[0]
        data = next((item for item in self.items_data if item['GUID'] == guid), None)
        if not data: return

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        # Details Setup
        rarity_raw = data.get('Rarity', 'None')
        rarity_guid = RARITY_LOCA_MAPPING.get(rarity_raw)
        if rarity_guid:
            rarity_display = self.localization_map.get(rarity_guid, rarity_raw).upper()
        else:
            rarity_display = rarity_raw.upper()

        # Get the Color
        rarity_color = RARITY_COLORS.get(rarity_raw, "#333333")
        item_name = self.get_resolved_name(guid)

        desc_id = data.get('InfoDescription', '').strip()
        description = self.localization_map.get(desc_id, f"ID: {desc_id}") if desc_id else "No description available."

        self.draw_header_gradient(rarity_color, rarity_display, item_name, description)

        width = self.header_canvas.winfo_width()
        if width <= 1: width = 800

        # Construct customized 128x128 icon
        size = (128, 128)
        alloc_raw = data.get('Allocation', '').strip()
        is_ship = alloc_raw.lower() in ["ships", "ship"]
        prefix = "ship" if is_ship else "villa"
        rarity_key = "legendary" if rarity_raw == "Unique" else rarity_raw.lower()

        bg_img = self.get_icon_image(f"data/ui/4k/base/features/goods_items/item_{prefix}_{rarity_key}_color.png", size)
        stroke_img = self.get_icon_image(f"data/ui/4k/base/features/goods_items/item_{prefix}_stroke_outer.png", size)
        item_img = self.get_icon_image(data['Icon'], size)

        base = Image.new("RGBA", size, (0,0,0,0))
        if bg_img: base.alpha_composite(bg_img)
        if stroke_img: base.alpha_composite(stroke_img)
        if item_img: base.alpha_composite(item_img)

        # DLC Version Icon Logic
        icon_path = data.get('Icon', '')
        origin_raw = data.get('Origin', '').strip()
        dlc_key = self.get_dlc_key_from_path(icon_path, origin_raw)

        # Only show obsidian price if it's dlc01 AND sold by the obsidian trader (GUID 145045)
        source_raw_price = data.get('Source', '')
        is_obsidian_item = (dlc_key == "dlc01") and ("145045" in source_raw_price)

        # Get the first icon path from your DLC_ICONS mapping
        dlc_icon_rel_path = DLC_ICONS.get(dlc_key, DLC_ICONS["base"])[0]

        # Load the icon (reusing your get_icon_image helper)
        dlc_icon_pil = self.get_icon_image(dlc_icon_rel_path, size=(32, 32))

        if dlc_icon_pil:
            dlc_photo = ImageTk.PhotoImage(dlc_icon_pil)
            # We must keep a reference so it doesn't get garbage collected
            self.header_dlc_icon = dlc_photo

            # Draw the icon on the canvas
            # Positioned at 152 vertical (matching your text) but shifted left
            # We use width - 110 to stay clear of the "GUID: 12345" text
            self.header_canvas.create_image(width - 40, 158, anchor="se", image=dlc_photo)

        # GUID in upper right corner
        self.header_canvas.create_text(width - 80, 152, anchor="se", text=f"{guid}", font=FONT_SMALL, fill=FG_DIM)

        photo = ImageTk.PhotoImage(base)
        self.icon_cache[guid + "_header"] = photo

        # 128x128 icon drawn at left edge
        self.header_canvas.create_image(15, 15, anchor="nw", image=self.icon_cache[guid + "_header"])

        big_sep = f"{'═' * 47}\n"

        # --- Niche & Allocation ---
        niche_raw = data.get('Niche', 'None')
        niche_val = NICHE_LOCA_MAPPING.get(niche_raw)
        n_icon, n_text = self.resolve_loca_and_icon(niche_val, niche_raw)

        alloc_raw = data.get('Allocation', '').strip()
        alloc_val = SLOT_LOCA_MAPPING.get(alloc_raw)
        a_icon, a_text = self.resolve_loca_and_icon(alloc_val, alloc_raw)

        self.details_text.insert(tk.END, big_sep)

        # 1. Create a transparent frame that spans the width of the text area
        # We use a slightly smaller width to account for margins
        f = tk.Frame(self.details_text, bg=BG_MAIN, width=790, height=25)
        f.pack_propagate(False) # Prevent the frame from shrinking to icon size

        # 2. Add Niche to the LEFT of this frame
        n_frame = tk.Frame(f, bg=BG_MAIN)
        n_frame.pack(side=tk.LEFT)
        if n_icon:
            img_n = self.get_icon_image(n_icon, (25, 25))
            if img_n:
                ph_n = ImageTk.PhotoImage(img_n)
                self.icon_cache[f"niche_{n_icon}"] = ph_n
                tk.Label(n_frame, image=ph_n, bg=BG_MAIN).pack(side=tk.LEFT)
        tk.Label(n_frame, text=n_text.upper(), font=FONT_UI_BOLD, fg=FG_MAIN, bg=BG_MAIN).pack(side=tk.LEFT, padx=10)

        # 3. Add Allocation to the RIGHT of this frame
        a_frame = tk.Frame(f, bg=BG_MAIN)
        a_frame.pack(side=tk.RIGHT)
        tk.Label(a_frame, text=a_text.upper(), font=FONT_UI_BOLD, fg=FG_MAIN, bg=BG_MAIN).pack(side=tk.RIGHT, padx=10)
        if a_icon:
            img_a = self.get_icon_image(a_icon, (25, 25))
            if img_a:
                ph_a = ImageTk.PhotoImage(img_a)
                self.icon_cache[f"alloc_{a_icon}"] = ph_a
                tk.Label(a_frame, image=ph_a, bg=BG_MAIN).pack(side=tk.RIGHT)

        # 4. Embed this entire horizontal "row" into the text widget
        self.details_text.window_create(tk.END, window=f)
        self.details_text.insert(tk.END, "\n")
        self.details_text.insert(tk.END, big_sep)

        # --- START MERGED CONTAINER TARGET AND REGULAR BUFFS ---
        # Record the start index here and only close it after all effects are done.
        merged_start = self.details_text.index(tk.INSERT)

        # 1. Target Rendering (Bold, Hover restricted to Villas)
        target_raw = data.get('Targets', '').strip()
        if target_raw and target_raw != "None":
            target_oid = "-6899655277052108454" if alloc_raw == "Villa" else "-6915573523070985148"
            target_label = self.localization_map.get(target_oid, "Influences").replace(":", "").strip()
            raw_groups = [g.strip() for g in target_raw.split('|') if g.strip()]

            if alloc_raw == "Villa":
                # VILLA: [Icons/Names] [Label]
                for i, group in enumerate(raw_groups):
                    p_name, sub_text = self.get_target_info(group)
                    t_icon = self.get_target_icon(group)
                    icon_tag = f"[SIMG:{t_icon}] " if t_icon else ""

                    tag = f"tg_hv_{i}"
                    active_style = "multiple_targets" if sub_text else "single_targets"

                    self.insert_text_with_icons(self.details_text, icon_tag, (active_style, "section_bg"))
                    self.details_text.insert(tk.END, p_name, (tag, active_style, "section_bg"))

                    # Only bind tooltip if there is actual sub_text
                    if sub_text:
                        self.details_text.tag_bind(tag, "<Enter>", lambda e, s=sub_text: self.show_target_tooltip(e, s, pinned=False))
                        # Hover to hide (only if not pinned)
                        self.details_text.tag_bind(tag, "<Leave>", self.hide_target_tooltip)
                        # Click to pin
                        self.details_text.tag_bind(tag, "<Button-1>", lambda e, s=sub_text: self.show_target_tooltip(e, s, pinned=True))
                        self.details_text.tag_bind(tag, "<Enter>", lambda e: self.details_text.config(cursor="hand2"), add="+")
                        self.details_text.tag_bind(tag, "<Leave>", lambda e: self.details_text.config(cursor="arrow"), add="+")
                    else:
                        # Explicitly bind to hide tooltip to ensure no old tooltip persists
                        self.details_text.tag_bind(tag, "<Enter>", lambda e: self.hide_target_tooltip(e))

                    if i < len(raw_groups) - 1:
                        self.details_text.insert(tk.END, ", ", ("single_targets", "section_bg"))

                # "Residences in range:"
                self.details_text.insert(tk.END, f" {target_label}:\n", ("single_targets", "section_bg"))

            else:
                # SHIP: [Label] [Icons/Names]
                self.details_text.insert(tk.END, f"{target_label} ", ("single_targets", "section_bg"))
                for i, group in enumerate(raw_groups):
                    p_name, _ = self.get_target_info(group)

                    t_icon = self.get_target_icon(group, is_ship=True)
                    icon_tag = f"[SIMG:{t_icon}] " if t_icon else ""

                    tag = f"sh_hv_{i}"
                    # Clear potential old ship hover tags
                    self.details_text.tag_unbind(tag, "<Enter>")

                    self.insert_text_with_icons(self.details_text, icon_tag, ("single_targets", "section_bg"))
                    self.details_text.insert(tk.END, p_name, ("single_targets", "section_bg"))

                    if i < len(raw_groups) - 1:
                        self.details_text.insert(tk.END, ", ", ("single_targets", "section_bg"))

                self.details_text.insert(tk.END, ":\n", ("single_targets", "section_bg"))

            self.details_text.insert(tk.END, "\n", ("half_space", "section_bg"))

        # Complex String Formatting
        add_eff_text = _, add_eff_text = self.resolve_loca_and_icon(ADDITIONAL_EFFECTS_ID, "Additional Effects")

        def res_emb(text):
            if not text or text == "None": return "None"

            def localize_generic(t):
                def replace_tech(m):
                    tk_match = m.group(0)
                    oid = BUFF_EFFECT_MAPPING.get(tk_match)
                    if oid:
                        icon_path, loc_text = self.resolve_loca_and_icon(oid, tk_match)
                        loc_text = loc_text.replace(":", "").strip()
                        if icon_path:
                            return f"[SIMG:{icon_path}] {loc_text}"
                        return loc_text
                    return tk_match
                t = re.sub(r'\b[a-zA-Z]+\b', replace_tech, t)

                def replace_guid(m):
                    g = m.group(0)
                    if len(g.replace('-', '')) < 4: return g
                    res = self.get_resolved_name(g)

                    if not res.startswith("Unknown"):
                        # --- FIX: Prepend the XML icon if it exists ---
                        icon_path = self.asset_guid_to_icon.get(g)
                        if icon_path:
                            return f"[SIMG:{icon_path}] {res}"
                        return res

                    return g
                return re.sub(r'(?<![+\d\-.])\b-?\d{4,20}\b(?![%])', replace_guid, t)

            add_eff_guid = ADDITIONAL_EFFECTS_ID[1] if isinstance(ADDITIONAL_EFFECTS_ID, list) else ADDITIONAL_EFFECTS_ID

            # 1. SPECIAL CASE: ChangeNeedAttributesOf
            if "ChangeNeedAttributesOf" in text:
                # Find all occurrences: (Action) (GUID) (Attribute +Value)
                matches = re.findall(r'(ChangeNeedAttributesOf)\s+(-?\d+):\s*([^|]+)', text)

                if matches:
                    # --- STEP 1: Action Mapping (Always use the first match to define the block type) ---
                    action_key = matches[0][0]
                    a_oid = BUFF_EFFECT_MAPPING.get(action_key)
                    a_icon, a_loc = self.resolve_loca_and_icon(a_oid, action_key)

                    # Safety check for the path-based mapping we saw in debug
                    if not a_icon and isinstance(a_oid, str) and a_oid.endswith('.png'):
                        a_icon, a_loc = a_oid, self.localization_map.get(action_key, "Need Attributes")

                    action_prefix = f"[SIMG:{a_icon}] {a_loc.strip()}"

                    # --- STEP 2 & 3: Grouping Attributes by Target GUID ---
                    # Format: { "2144": [formatted_attr_line1, formatted_attr_line2], ... }
                    grouped_data = {}

                    for _, target_guid, attr_raw in matches:
                        t_id = target_guid.strip()

                        # Process the Attribute (Step 3)
                        subp = attr_raw.strip().rsplit(' ', 1)
                        if len(subp) == 2:
                            name_raw, val_raw = subp
                            at_oid = BUFF_EFFECT_MAPPING.get(name_raw.strip())
                            at_icon, at_loc = self.resolve_loca_and_icon(at_oid, name_raw.strip())

                            attr_line = f"\t- [SIMG:{at_icon}] {at_loc}\t{val_raw.strip()}"
                        else:
                            attr_line = f"\t- {attr_raw.strip()}"

                        # Grouping
                        if t_id not in grouped_data:
                            grouped_data[t_id] = []
                        grouped_data[t_id].append(attr_line)

                    # --- STEP 4: Final UI Block Construction ---
                    result_blocks = []
                    for guid, lines in grouped_data.items():
                        # Resolve Target Name & Icon from Asset Data (Step 2)
                        t_name = self.get_resolved_name(guid)
                        t_icon = self.asset_guid_to_icon.get(str(guid), "")
                        target_str = f"[SIMG:{t_icon}] {t_name}"

                        # Build the header line + all indented attributes
                        # Using \t for the header ensures insert_effect_block handles icons correctly
                        block = f"{action_prefix}\t{target_str}:\n" + "\n".join(lines)
                        result_blocks.append(block)

                    return "\n\n".join(result_blocks)

            # 2. SPECIAL CASE: IncidentImmunity
            if "IncidentImmunity" in text:
                raw_content = text.replace("IncidentImmunity", "").replace(":", "").strip()
                raw_incidents = [i.strip() for i in raw_content.split(";") if i.strip()]
                processed_incidents = []
                for term in raw_incidents:
                    mapping_val = INCIDENT_MAPPING.get(term)
                    icon_path, loc_text = self.resolve_loca_and_icon(mapping_val, term)
                    if icon_path:
                        processed_incidents.append(f"[SIMG:{icon_path}] {loc_text}")
                    else:
                        processed_incidents.append(loc_text)

                header_guid = "-6905739525374090419"
                header_mapping = BUFF_EFFECT_MAPPING.get("IncidentImmunity", header_guid)
                h_icon, h_text = self.resolve_loca_and_icon(header_mapping, "Incident Immunity")
                header_with_icon = f"[SIMG:{h_icon}] {h_text.replace('{}', '').strip()}" if h_icon else h_text
                return f"{header_with_icon}: {', '.join(processed_incidents)}"

            # 3. SPECIAL CASE: Additional Effects (Radius/Scope)
            if add_eff_guid in text:
                add_eff_icon, add_eff_label = self.resolve_loca_and_icon(ADDITIONAL_EFFECTS_ID, "Additional Effects")
                header = add_eff_label.replace(':', '').strip()
                header_with_icon = f"[SIMG:{add_eff_icon}] {header}" if add_eff_icon else header

                parts = text.split(' ', 1)
                if len(parts) > 1:
                    resolved_attrs = localize_generic(parts[1])
                    attr_lines = []
                    for a in resolved_attrs.split(','):
                        a = re.sub(r':\s*', ' ', a).strip()
                        subp = a.rsplit(' ', 1)
                        if len(subp) == 2:
                            attr_lines.append(f"\t- {subp[0]}\t{subp[1]}")
                        else:
                            attr_lines.append(f"\t- {a}")
                    return header_with_icon + ":\n" + "\n".join(attr_lines)
                return header_with_icon

            # 4. SPECIAL CASE: AdditionalOutput
            elif "AdditionalOutput" in text:
                # 1. Resolve Header using BUFF_EFFECT_MAPPING entry
                # Entry: ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_goods.png", "-6899820196143793484"]
                mapping_val = BUFF_EFFECT_MAPPING.get("AdditionalOutput")
                header_icon, header_text = self.resolve_loca_and_icon(mapping_val, "Additional Output")

                header_with_icon = f"[SIMG:{header_icon}] {header_text}"

                # 2. Parse the CSV Data (e.g., "AdditionalOutput: 31697 1/10")
                raw_data = text.replace("AdditionalOutput:", "").strip()
                parts = raw_data.split()

                if len(parts) >= 2:
                    # GUID and Amount provided
                    product_guid = parts[0]
                    amount = parts[1]
                    # Resolve product using single GUID string logic
                    prod_icon = self.asset_guid_to_icon.get(product_guid)
                    prod_text = self.get_resolved_name(product_guid)

                else:
                    # No product GUID provided -> use your supplied fallback tuple
                    fallback_val = ["data/ui/fhd/base/icon_content/generic/icon_2d_generic_item.png", "-6913919693270396287"]
                    amount = parts[0] if parts else "1"
                    prod_icon, prod_text = self.resolve_loca_and_icon(fallback_val, "Storage")

                # 3. Clean the product name
                clean_product_name = re.sub(r'<[^>]+>', '', prod_text).replace("{}", "").strip()

                # 4. Construct the output string (Matches "Additional Effects" layout)
                # \t- for indentation, second \t for right-aligned amount
                sub_line = f"\t- [SIMG:{prod_icon}] {clean_product_name}\t{amount}"

                return f"{header_with_icon}\n{sub_line}"

            # 5. FINAL FALLBACK: Standard Effects (e.g., AttackPower: 10%)
            # Split into Key and Value
            parts = text.split(':', 1)
            tech_key = parts[0].strip()
            raw_val = parts[1].strip() if len(parts) > 1 else ""

            # Resolve the Label and Icon for the Key
            oid = BUFF_EFFECT_MAPPING.get(tech_key)
            icon_path, loc_title = self.resolve_loca_and_icon(oid, tech_key)

            # Fetch Icon and Name if the key is a GUID
            if not icon_path and tech_key.replace('-', '').isdigit():
                icon_path = self.asset_guid_to_icon.get(tech_key)
                loc_name = self.get_resolved_name(tech_key)
                if not loc_name.startswith("Unknown"):
                    loc_title = loc_name

            title = loc_title.replace("{}", "").replace(":", "").strip()
            header_with_icon = f"[SIMG:{icon_path}] {title}" if icon_path else title

            # Localize the Value (important for OasisIDs in generic values)
            localized_val = localize_generic(raw_val)

            if localized_val:
                # Use \t for the Right-Alignment logic
                return f"{header_with_icon}\t{localized_val}"

            return header_with_icon

        # Insert Effects logic with bg tags, half spacing, and right-alignment
        def insert_effect_block(raw_str):
            if not raw_str or raw_str == "None" or not raw_str.strip():
                return

            start_idx = self.details_text.index(tk.INSERT)

            # 1. Flexible Splitting
            separator = '|' if '|' in raw_str else ','
            raw_list = [e.strip() for e in raw_str.split(separator) if e.strip()]

            # --- NEW with DLC01: Extract paired AddedFertility + FertilityPercent before main loop ---
            fertility_guid = None
            fertility_pct = None
            filtered_raw_list = []
            for e in raw_list:
                if e.startswith("AddedFertility:"):
                    fertility_guid = e.split(":", 1)[1].strip()
                elif e.startswith("FertilityPercent:"):
                    fertility_pct = e.split(":", 1)[1].strip()
                else:
                    filtered_raw_list.append(e)
            raw_list = filtered_raw_list

            # 2. Gather all resolved lines first
            all_lines = []
            for e in raw_list:
                resolved = res_emb(e)
                if not resolved or resolved == "None": continue
                all_lines.extend(resolved.split('\n'))

            # --- NEW with DLC01: Formating for Fertility Items: Append merged fertility line (icon + loca name left, percent right) ---
            if fertility_guid is not None:
                f_icon = "data/ui/fhd/base/icon_content/generic/icon_2d_fertility.png"
                f_name = self.get_resolved_name(fertility_guid)
                left = f"[SIMG:{f_icon}] {f_name}" if f_icon else f_name
                pct = fertility_pct if fertility_pct is not None else "+100%"
                all_lines.append(f"{left}\t{pct}")

            # 3. Filter duplicate headers
            processed_lines = []
            last_header = None

            for line in all_lines:
                if not line.strip(): continue

                is_indented = line.startswith('\t-')

                if not is_indented:
                    # If this is a header (ends with colon) and matches the previous one, skip it!
                    if line.strip().endswith(':') and line == last_header:
                        continue
                    # Update our tracker to the new header
                    last_header = line

                processed_lines.append(line)

            # 4. Insert lines with dynamic spacing
            for i, line in enumerate(processed_lines):
                target_tag = "effect_line_indented" if line.startswith('\t-') else "effect_line"

                if '\t' in line:
                    self.insert_text_with_icons(self.details_text, f"{line}\n", (target_tag))
                else:
                    parts = line.rsplit(' ', 1)
                    if len(parts) == 2 and any(char.isdigit() for char in parts[1]):
                        self.insert_text_with_icons(self.details_text, f"{parts[0]}\t{parts[1]}\n", (target_tag))
                    else:
                        self.insert_text_with_icons(self.details_text, f"{line}\n", (target_tag))

                # Dynamic Spacing
                # We only add a half-space if the NEXT line is NOT an indented bullet.
                # This naturally glues bullets to their header while keeping standard effects separated.
                if i < len(processed_lines) - 1:
                    next_line = processed_lines[i + 1]
                    if not next_line.startswith('\t-'):
                        self.details_text.insert(tk.END, "\n", ("half_space", "section_bg"))
                else:
                    # Always append a half-space at the very end of the block
                    self.details_text.insert(tk.END, "\n", ("half_space", "section_bg"))

            # Apply the background color to the whole block
            end_idx = self.details_text.index(tk.INSERT)
            self.details_text.tag_add("section_bg", start_idx, end_idx)

        insert_effect_block(data.get('Buff Effects', ''))

        # 2. Effect Rendering (Second part of the merged box)
        eff_raw = data.get('Effects', '').strip()
        insert_effect_block(eff_raw)

        # --- CLOSE MERGED CONTAINER ---
        merged_end = self.details_text.index(tk.INSERT)
        self.details_text.tag_add("section_bg", merged_start, merged_end)
        self.details_text.insert(tk.END, "\n") # Outer gap after the merged box

        # --- BOOST CONDITION Section ---
        boost_cond_raw = data.get('Boost Condition', '').strip()
        if boost_cond_raw and boost_cond_raw != "None":
            boost_hint_raw = data.get('Boost Hint', '').strip()
            localized_hint = self.localization_map.get(boost_hint_raw, boost_hint_raw)
            formatted_condition = self.resolve_boost_condition(boost_cond_raw)

            # 1. Resolve icon and localized label
            boost_icon, boost_label = self.resolve_loca_and_icon(BOOST_HEADER_ID, "Boost Requirements")

            # 2. Create a Frame for the Header to allow for the custom icon scale
            header_frame = tk.Frame(self.details_text, bg=BG_MAIN)

            if boost_icon:
                img_b = self.get_icon_image(boost_icon, (25, 25))  # Scaled up to 25x25
                if img_b:
                    ph_b = ImageTk.PhotoImage(img_b)
                    # Unique key for cache
                    self.icon_cache[f"boost_hdr_{len(self.icon_cache)}"] = ph_b
                    tk.Label(header_frame, image=ph_b, bg=BG_MAIN).pack(side=tk.LEFT)

            # Add the Header Text
            tk.Label(header_frame, text=f" {boost_label.upper()}", font=FONT_UI_BOLD, fg=FG_MAIN, bg=BG_MAIN).pack(side=tk.LEFT)

            # 3. Insert the Frame and then the standard text
            self.details_text.window_create(tk.END, window=header_frame)
            self.details_text.insert(tk.END, "\n")

            # Apply the boost_header tag style to the hint text
            self.details_text.insert(tk.END, f"{localized_hint} ({formatted_condition})\n\n")

            # 4. Process the effects
            s_b = data.get('BoostBuff Effects', '').strip()
            insert_effect_block(s_b)

        # --- PRICE Section ---
        is_meta = data.get('IsMetaItem') == '1'
        meta_text = self.localization_map.get("-6901699015838422825", "Meta Item").strip()

        # Resolve localized "Price" label (icon ignored here, currency_icon used instead)
        _, price_label = self.resolve_loca_and_icon(PRICE_LABEL_ID, "Price")

        if is_meta:
            pr_val = meta_text
            currency_icon = SOURCE_LABELS["HallofFame"][0]
            left_label = price_label
            left_icon = self.asset_guid_to_icon.get("107517", "")
        elif rarity_raw == "Unique":
            pr_val = self.localization_map.get(RARITY_LOCA_MAPPING.get("Unique", ""), "Unique")
            currency_icon = self.asset_guid_to_icon.get("29293", "")
            left_label = price_label
            left_icon = self.asset_guid_to_icon.get("107517", "")
        elif is_obsidian_item:
            pr_val = data.get('ObsidianPrice', '0')
            currency_icon = self.asset_guid_to_icon.get("145102", "")
            left_label = self.localization_map.get("-6900979948556600852", "Obsidian Item").strip()
            left_icon = self.asset_guid_to_icon.get("107517", "")
        else:
            pr_val = data.get('Price', '0')
            currency_icon = self.asset_guid_to_icon.get("1010017", PRICE_LABEL_ID[0])
            left_label = price_label
            left_icon = self.asset_guid_to_icon.get("107517", "")

        self.details_text.insert(tk.END, big_sep)

        # Container frame
        price_row = tk.Frame(self.details_text, bg=BG_MAIN, width=790, height=25)
        price_row.pack_propagate(False)

        # LEFT SIDE: optional icon + label
        left_group = tk.Frame(price_row, bg=BG_MAIN)
        left_group.pack(side=tk.LEFT)

        if left_icon:
            img_l = self.get_icon_image(left_icon, (25, 25))
            if img_l:
                ph_l = ImageTk.PhotoImage(img_l)
                self.icon_cache[f"price_left_icon_{len(self.icon_cache)}"] = ph_l
                tk.Label(left_group, image=ph_l, bg=BG_MAIN).pack(side=tk.LEFT)

        tk.Label(left_group, text=f" {left_label.upper()}:", font=FONT_UI_BOLD, fg=FG_MAIN, bg=BG_MAIN).pack(side=tk.LEFT)

        # RIGHT SIDE: currency icon + value
        right_group = tk.Frame(price_row, bg=BG_MAIN)
        right_group.pack(side=tk.RIGHT)

        tk.Label(right_group, text=pr_val, font=FONT_UI_BOLD, fg=FG_MAIN, bg=BG_MAIN).pack(side=tk.RIGHT, padx=10)

        if currency_icon:
            img_p = self.get_icon_image(currency_icon, (25, 25))
            if img_p:
                ph_p = ImageTk.PhotoImage(img_p)
                self.icon_cache[f"price_icon_{len(self.icon_cache)}"] = ph_p
                tk.Label(right_group, image=ph_p, bg=BG_MAIN).pack(side=tk.LEFT)

        self.details_text.window_create(tk.END, window=price_row)
        self.details_text.insert(tk.END, "\n")
        self.details_text.insert(tk.END, big_sep)

        # --- ITEM SOURCE Rendering (Multi-Column using tabs) ---
        self.details_text.tag_configure("source_header", font=FONT_UI_BOLD)
        self.details_text.tag_configure("source_line_split", font=FONT_SMALL, tabs=("400", "left"))
        self.details_text.tag_configure("source_gold", foreground="#ffd700")
        self.details_text.tag_configure("source_research", foreground="#eba117")

        source_raw = data.get('Source', '').strip()
        if source_raw and source_raw != "None":
            source_start = self.details_text.index(tk.INSERT)

            # 1. Localize and Iconize the Source Header
            source_header_guid = "-6907963067247957273"
            source_icon_path = resource_path("data/ui/fhd/base/icon_content/generic/icon_2d_generic_reward.png")

            # Localize
            localized_source_title = self.localization_map.get(source_header_guid, "SOURCES").upper()

            # Combine with Icon Tag
            header_with_icon = f"[SIMG:{source_icon_path}] {localized_source_title}: \n"

            # --- TAG BINDING LOGIC ---
            # Record where we start inserting
            tag_start = self.details_text.index(tk.INSERT)

            # Insert using a new tag 'source_legend_trigger'
            self.insert_text_with_icons(self.details_text, header_with_icon, ("source_header", "section_bg", "source_legend_trigger"))
            self.details_text.insert(tk.END, "\n", ("half_space", "section_bg"))

            tag_end = self.details_text.index(f"{tag_start} lineend")

            # Bind the hover events to the header text
            self.details_text.tag_bind("source_legend_trigger", "<Enter>", lambda e: [self.details_text.config(cursor="question_arrow"), self.show_source_legend(e)])
            self.details_text.tag_bind("source_legend_trigger", "<Leave>", lambda e: [self.details_text.config(cursor="xterm"), self.hide_target_tooltip(e)])

            # 2. Resolve and Columnize the Source List
            resolved_list = self.resolve_source(source_raw)

            # --- COLOR RANKING LOGIC ---
            ICON_TO_CAT = {
                "data/ui/fhd/base/icon_content/generic/icon_2d_buy_sell.png": "-6915651869812775825",
                "data/ui/fhd/base/icon_content/quest_tracker/icon_2d_questlog_writting.png": "-6914021190765224130",
                "data/ui/fhd/base/icon_content/generic/icon_2d_loading_ramp_ship.png": "-6904030652562679494",
                "data/ui/fhd/base/icon_content/city_incident/icon_2d_festival.png": "-6908773579491322283"
            }
            RESEARCH_ICONS = {
                "data/ui/fhd/base/icon_content/tech_tree/icon_2d_research_military.png",
                "data/ui/fhd/base/icon_content/tech_tree/icon_2d_research_civic.png",
                "data/ui/fhd/base/icon_content/tech_tree/icon_2d_research_economic.png"
            }

            item_stats = []
            for item_str in resolved_list:
                pct_match = re.search(r'(\d+(?:\.\d+)?)%', item_str)
                pct = float(pct_match.group(1)) if pct_match else 0.0

                category = "none"
                # Check for Research first
                if any(res_icon in item_str for res_icon in RESEARCH_ICONS):
                    category = "research"
                else:
                    # Check for Big Categories based on the icon path
                    for icon_path, cat_id in ICON_TO_CAT.items():
                        if icon_path in item_str:
                            category = cat_id
                            break

                item_stats.append({'text': item_str, 'pct': pct, 'cat': category})

            # Identify ALL Top 1s for each Big Category
            gold_texts = set()
            for cat_id in ICON_TO_CAT.values():
                cat_items = [i for i in item_stats if i['cat'] == cat_id]
                if cat_items:
                    max_val = max(i['pct'] for i in cat_items)
                    if max_val > 0:
                        for i in cat_items:
                            if i['pct'] == max_val:
                                gold_texts.add(i['text'])

            research_texts = {i['text'] for i in item_stats if i['cat'] == "research"}

            # Split into two halves for the columns
            mid = (len(resolved_list) + 1) // 2
            left_col = resolved_list[:mid]
            right_col = resolved_list[mid:]

            # Print the columns
            # Function to pick the right tags for an item
            def get_style(txt):
                if not txt: return ("source_line_split", "section_bg")
                if txt in gold_texts: return ("source_gold", "source_line_split", "section_bg")
                if txt in research_texts: return ("source_research", "source_line_split", "section_bg")
                return ("source_line_split", "section_bg")

            for i in range(len(left_col)):
                l_item = left_col[i]
                r_item = right_col[i] if i < len(right_col) else ""

                self.insert_text_with_icons(self.details_text, l_item, get_style(l_item))
                if r_item:
                    self.details_text.insert(tk.END, "\t", ("source_line_split", "section_bg"))
                    self.insert_text_with_icons(self.details_text, r_item, get_style(r_item))
                self.details_text.insert(tk.END, "\n", ("section_bg"))

        self.details_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ItemBrowserApp(root)
    root.mainloop()