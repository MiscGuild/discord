from enum import Enum

import toml

from src.utils.data_classes import IngameRank

config = toml.load("config.toml")

# Gexp requirements
ingame_ranks_dict = config["ingame_ranks"]
RANK_1 = IngameRank(
    name=ingame_ranks_dict["rank_1"]["name"],
    requirement=ingame_ranks_dict["rank_1"]["requirement"],
    is_staff=ingame_ranks_dict["rank_1"]["is_staff"],
    discord_role=None
)
RANK_2 = IngameRank(
    name=ingame_ranks_dict["rank_2"]["name"],
    requirement=ingame_ranks_dict["rank_2"]["requirement"],
    is_staff=ingame_ranks_dict["rank_2"]["is_staff"],
    discord_role=None
)
RANK_3 = IngameRank(
    name=ingame_ranks_dict["rank_3"]["name"],
    requirement=ingame_ranks_dict["rank_3"]["requirement"],
    is_staff=ingame_ranks_dict["rank_3"]["is_staff"],
    discord_role=None
)
MOD = IngameRank(
    name=ingame_ranks_dict["rank_4"]["name"],
    requirement=ingame_ranks_dict["rank_4"]["requirement"],
    is_staff=ingame_ranks_dict["rank_4"]["is_staff"],
    discord_role=None
)
ADMIN = IngameRank(
    name=ingame_ranks_dict["rank_5"]["name"],
    requirement=ingame_ranks_dict["rank_5"]["requirement"],
    is_staff=ingame_ranks_dict["rank_5"]["is_staff"],
    discord_role=None
)
INGAME_RANKS = [RANK_1, RANK_2, RANK_3, MOD, ADMIN]
NON_STAFF_RANKS = [rank for rank in INGAME_RANKS if not rank.is_staff]

DNKL_REQ = NON_STAFF_RANKS[0].requirement * 2


class ChatColor(Enum):
    RED = "&c"
    GOLD = "&6"
    GREEN = "&a"
    YELLOW = "&e"
    LIGHT_PURPLE = "&d"
    WHITE = "&f"
    BLUE = "&9"
    DARK_GREEN = "&2"
    DARK_RED = "&4"
    DARK_AQUA = "&3"
    DARK_PURPLE = "&5"
    DARK_GRAY = "&8"
    BLACK = "&0"
    DARK_BLUE = "&1"
