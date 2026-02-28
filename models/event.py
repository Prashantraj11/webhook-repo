"""
Event model and EventAction enum.
"""

from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


class EventAction(Enum):
    """Allowed webhook event types."""
    PUSH = "PUSH"
    PULL = "PULL"
    MERGE = "MERGE"


@dataclass
class Event:
    """Represents a single GitHub webhook event."""
    request_id: str
    author: str
    action: EventAction
    from_branch: str
    to_branch: str
    timestamp: str

    # -- serialisation helpers ------------------------------------------------

    def to_dict(self) -> dict:
        """Convert to a plain dict suitable for MongoDB insertion."""
        return {
            "request_id": self.request_id,
            "author": self.author,
            "action": self.action.value,          # store the string value
            "from_branch": self.from_branch,
            "to_branch": self.to_branch,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Reconstruct an Event from a MongoDB document."""
        return cls(
            request_id=data.get("request_id", ""),
            author=data.get("author", "unknown"),
            action=EventAction(data.get("action", "PUSH")),
            from_branch=data.get("from_branch", ""),
            to_branch=data.get("to_branch", ""),
            timestamp=data.get("timestamp", ""),
        )
