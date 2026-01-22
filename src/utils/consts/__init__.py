from .bot_consts import (CONFIG, PREFIX, API_KEYS, ERROR_REPLY_EXCEPTIONS, GUILD_HANDLE, ALLIES, NEG_COLOR, POS_COLOR,
                         NEUTRAL_COLOR, \
                         ERROR_COLOR)
from .discord_consts import (GVG_REQUIREMENTS, ERROR_CHANNEL_ID, DNKL_CHANNEL_ID, TICKET_CHANNEL_ID, LOG_CHANNEL_ID,
                             REGISTRATION_CHANNEL_ID, STAFF_BRIDGE_CHANNEL_ID, STAFF_ANNOUNCEMENTS_CHANNEL_ID,
                             PARTNER_CHANNEL_ID,
                             QOTD_THREAD_ID,
                             GEOGUESSR_THREAD_ID, MILESTONES_CHANNEL_ID, WEEKLY_LB_CHANNEL_ID, DAILY_LB_CHANNEL_ID,
                             RANK_UPGRADE_CHANNEL_ID,
                             TICKET_CATEGORIES, MILESTONE_CATEGORIES, MILESTONE_EMOJIS, GUEST_TICKET_REASONS,
                             MEMBER_TICKET_REASONS,
                             GENERAL_TICKET_REASONS, ELITE_MEMBER_CATEGORIES, REGISTRATION_EMBED, TICKET_DELETED_EMBED, \
                             STAFF_IMPERSONATION_EMBED, ACCEPTED_STAFF_APPLICATION_EMBED, REQUIREMENTS_EMBED,
                             DNKL_ENTRIES_NOT_FOUND,
                             INFORMATION_MESSAGE, RESIDENT_EMBED, INFORMATION_REQUIREMENTS_EMBED, TICKETS_MESSAGES,
                             GVG_INFO_EMBED,
                             POSITIVE_RESPONSES,
                             UNKNOWN_IGN_MSG, INVALID_DATE_MSG, MISSING_ROLES_EMBED, MISSING_PERMS_MSG,
                             INVALID_COMMAND_EMBED,
                             NOT_OWNER_EMBED,
                             MISSING_PERMS_EMBED, MEMBER_NOT_FOUND_EMBED, ERR_404_EMBED, BOT_MISSING_PERMS_EMBED,
                             GUILDLESS_EMBED, INVALID_GUILD_EMBED, UNKNOWN_IGN_EMBED, DISCORD_NOT_LINKED_EMBED,
                             REQUIREMENTS_TEXT,
                             JOIN_REQUEST_EMBED,
                             DNKL_CREATION_EMBED, RULES_MESSAGES, RANK_UPGRADE_WINNER_MESSAGE,
                             STAFF_APPLICATION_QUESTIONS, SPOILERS_AHEAD)
from .ingame_consts import (INGAME_RANKS, NON_STAFF_RANKS, DNKL_REQ, ChatColor)

__all__ = [
    name for name, value in globals().items()
    if name.isupper()
]
