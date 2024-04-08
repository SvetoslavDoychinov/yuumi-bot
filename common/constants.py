from enum import Enum


class LobbyTypes(Enum):
    """Enum containing all lobby types by id"""
    INTRO = 830
    BEGINNER = 840
    INTERMEDIATE = 850
    QUICK_PLAY = 490
    DRAFT_PICK = 400
    SOLO_DUO = 420
    FLEX = 440


class Positions(Enum):
    """Enum containing possible lane positions"""
    NONE = "UNSELECTED"
    BOTTOM = "BOTTOM"
    SUPPORT = "UTILITY"
    MIDDLE = "MIDDLE"
    JUNGLE = "JUNGLE"
    TOP = "TOP"


class ClientPhases(Enum):
    """Enum containing all client phases"""
    NONE = "None"
    LOBBY = "Lobby"
    QUEUE = "Matchmaking"
    READY_CHECK = "ReadyCheck"
    CHAMP_SELECT = "ChampSelect"
    IN_GAME = "InProgress"
    END_OF_GAME = "EndOfGame"
    RECONNECT = "Reconnect"


class ChampSelectPhases(Enum):
    """Enum containing all champion select phases"""
    BAN_PICK = "BAN_PICK"
    FINALIZATION = "FINALIZATION"


class ChampionIds(Enum):
    """Enum containing champion ids"""
    NONE = 0
    NUNU = 20
    DRAVEN = 119
    LUX = 99
    SETT = 875
    YUUMI = 350


class SummonerSpells(Enum):
    """Enum containing summoner spell ids"""
    CLEANSE = 1
    EXHAUST = 3
    FLASH = 4
    GHOST = 6
    HEAL = 7
    TELEPORT = 12
    IGNITE = 14
    BARRIER = 21


class MapLocationRatios(Enum):
    """Fraction of LoL window size used to calculate coordinates on the minimap"""
    ORDER = (0.97, 0.76)  # for ORDER nexus
    CHAOS = (0.82, 0.94)  # for CHAOS nexus
    CENTER = (0.5, 0.5)
    SHOP_ITEM_BUTTON = (0.3084, 0.5096)
    SHOP_PURCHASE_ITEM_BUTTON = (0.7019, 0.9450)


class Items(Enum):
    """Enum containing items with their prices"""
    World_Atlas = 400
    Dream_Maker = 400
    Moonstone_Renewer = 2200
    Ardent_Censer = 2300
    Staff_of_Flowing_Water = 2300
    Morellonomicon = 2200
