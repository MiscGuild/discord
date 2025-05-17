from dataclasses import dataclass, asdict, field
from typing import List

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
