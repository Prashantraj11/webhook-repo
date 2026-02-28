from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


class EventAction(Enum):
    PUSH = "PUSH"
    PULL = "PULL"
    MERGE = "MERGE"


@dataclass
class Event:
    request_id: str
    author: str
    action: EventAction
    from_branch: str
    to_branch: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "author": self.author,
            "action": self.action.value,
            "from_branch": self.from_branch,
            "to_branch": self.to_branch,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(
            request_id=data.get("request_id", ""),
            author=data.get("author", "unknown"),
            action=EventAction(data.get("action", "PUSH")),
            from_branch=data.get("from_branch", ""),
            to_branch=data.get("to_branch", ""),
            timestamp=data.get("timestamp", ""),
        )
