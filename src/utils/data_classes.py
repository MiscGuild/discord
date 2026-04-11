from dataclasses import dataclass, asdict, field
from typing import List, Optional

import discord


@dataclass
class WeeklyStats:
    total: int = 0
    valid: int = 0
    all_uuids: List[str] = field(default_factory=list)
    valid_uuids: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "total": self.total,
            "valid": self.valid,
            "all_uuids": self.all_uuids,
            "valid_uuids": self.valid_uuids,
        }


@dataclass
class InvitationStats:
    uuid: str
    weekly: WeeklyStats = field(default_factory=WeeklyStats)
    total: int = 0
    valid: int = 0

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "weekly": asdict(self.weekly),
            "total": self.total,
            "valid": self.valid,
        }


@dataclass
class IngameRank:
    name: str
    requirement: int
    is_staff: bool
    discord_role: Optional[discord.Role] = None

    def to_dict(self):
        return {
            "name": self.name,
            "requirement": self.requirement,
            "is_staff": self.is_staff,
        }


@dataclass
class RegisteredDiscordMember:
    ign: Optional[str] = None
    uuid: Optional[str] = None
    discord_id: Optional[int] = None

    @classmethod
    async def from_uuid(
            cls,
            uuid: str,
            include_discord_id: bool = False,
    ) -> "RegisteredDiscordMember":
        if uuid == "0":
            return cls()

        from src.utils.db_utils import get_username_from_uuid, get_discord_id_from_uuid
        from src.utils.request_utils import get_mojang_profile_from_uuid

        ign, resolved_uuid = await get_username_from_uuid(uuid)
        if not resolved_uuid:
            ign, resolved_uuid = await get_mojang_profile_from_uuid(uuid)
        discord_id = None

        if include_discord_id and resolved_uuid:
            discord_id = await get_discord_id_from_uuid(resolved_uuid)

        return cls(ign=ign, uuid=resolved_uuid, discord_id=discord_id)

    @classmethod
    async def from_username(
            cls,
            username: str,
            include_discord_id: bool = False,
    ) -> "RegisteredDiscordMember":
        from src.utils.db_utils import get_discord_id_from_uuid, get_uuid_from_username
        from src.utils.request_utils import get_uuid_by_name

        ign, resolved_uuid = await get_uuid_from_username(username)
        if not resolved_uuid:
            ign, resolved_uuid = await get_uuid_by_name(username)

        discord_id = None

        if include_discord_id and resolved_uuid:
            discord_id = await get_discord_id_from_uuid(resolved_uuid)

        return cls(ign=ign, uuid=resolved_uuid, discord_id=discord_id)

    @classmethod
    async def from_discord_id(cls, discord_id: int) -> "RegisteredDiscordMember":
        from src.utils.db_utils import get_username_from_uuid, get_uuid_from_discord_id
        from src.utils.request_utils import get_mojang_profile_from_uuid

        resolved_uuid = await get_uuid_from_discord_id(discord_id=discord_id)
        ign, _ = await get_username_from_uuid(uuid=resolved_uuid)
        if not ign:
            ign, resolved_uuid = await get_mojang_profile_from_uuid(resolved_uuid)

        return cls(ign=ign, uuid=resolved_uuid, discord_id=discord_id)
