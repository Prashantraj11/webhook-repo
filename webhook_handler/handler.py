from datetime import datetime, timezone
from models.event import Event, EventAction


def parse_webhook(event_type: str, payload: dict) -> Event | None:

    if event_type == "push":
        return _parse_push(payload)
    if event_type == "pull_request":
        return _parse_pull_request(payload)
    return None

def _parse_push(payload: dict) -> Event:
    branch = payload.get("ref", "").split("/")[-1]
    head_commit = payload.get("head_commit", {})

    return Event(
        request_id=head_commit.get("id", ""),
        author=payload.get("pusher", {}).get("name", "unknown"),
        action=EventAction.PUSH,
        from_branch="",
        to_branch=branch,
        timestamp=head_commit.get(
            "timestamp", datetime.now(timezone.utc).isoformat()
        ),
    )


def _parse_pull_request(payload: dict) -> Event:
    pr = payload.get("pull_request", {})
    gh_action = payload.get("action", "")

    if gh_action == "closed" and pr.get("merged", False):
        action = EventAction.MERGE
    else:
        action = EventAction.PULL

    return Event(
        request_id=str(pr.get("id", "")),
        author=pr.get("user", {}).get("login", "unknown"),
        action=action,
        from_branch=pr.get("head", {}).get("ref", ""),
        to_branch=pr.get("base", {}).get("ref", ""),
        timestamp=pr.get(
            "updated_at", datetime.now(timezone.utc).isoformat()
        ),
    )
