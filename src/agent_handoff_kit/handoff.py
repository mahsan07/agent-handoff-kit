"""Provider-neutral handoff records and lifecycle validation."""

from __future__ import annotations

import copy
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUSES = ("draft", "ready", "accepted", "completed", "returned")
TRANSITIONS = {
    "draft": {"ready"},
    "ready": {"accepted", "returned"},
    "accepted": {"completed", "returned"},
    "returned": {"ready"},
    "completed": set(),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_handoff(
    title: str,
    objective: str,
    owner: str,
    next_owner: str,
    reviewer: str,
    *,
    handoff_id: str | None = None,
    scope: list[str] | None = None,
) -> dict[str, Any]:
    timestamp = now()
    return {
        "schema_version": "1.0",
        "id": handoff_id or uuid.uuid4().hex[:12],
        "title": title,
        "objective": objective,
        "status": "draft",
        "owner": owner,
        "next_owner": next_owner,
        "reviewer": reviewer,
        "scope": scope or [],
        "artifacts": [],
        "decisions": [],
        "assumptions": [],
        "risks": [],
        "next_actions": [],
        "verification": [],
        "return_reason": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "events": [{"at": timestamp, "event": "created", "actor": owner}],
    }


def validate_handoff(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_strings = ("schema_version", "id", "title", "objective", "status", "owner", "next_owner", "reviewer", "created_at", "updated_at")
    required_lists = ("scope", "artifacts", "decisions", "assumptions", "risks", "next_actions", "verification", "events")
    for field in required_strings:
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"{field} must be a non-empty string")
    for field in required_lists:
        if not isinstance(record.get(field), list):
            errors.append(f"{field} must be a list")
    if record.get("status") not in STATUSES:
        errors.append(f"status must be one of: {', '.join(STATUSES)}")
    for index, artifact in enumerate(record.get("artifacts", [])):
        if not isinstance(artifact, dict) or not isinstance(artifact.get("uri"), str) or not artifact.get("uri"):
            errors.append(f"artifacts[{index}].uri must be a non-empty string")
        if isinstance(artifact, dict) and artifact.get("kind") not in {"file", "url", "commit", "note"}:
            errors.append(f"artifacts[{index}].kind must be file, url, commit, or note")
    if record.get("status") == "ready" and not record.get("next_actions"):
        errors.append("ready handoffs must include at least one next action")
    if record.get("status") == "completed" and not record.get("verification"):
        errors.append("completed handoffs must include verification evidence")
    if record.get("status") == "returned" and not record.get("return_reason"):
        errors.append("returned handoffs must include a return reason")
    return errors


def transition(record: dict[str, Any], target: str, actor: str, *, reason: str | None = None) -> dict[str, Any]:
    current = record.get("status")
    if target not in TRANSITIONS.get(current, set()):
        raise ValueError(f"invalid transition: {current} -> {target}")
    if actor not in {record.get("owner"), record.get("next_owner"), record.get("reviewer")}:
        raise ValueError("actor is not a named participant in this handoff")
    if target == "returned" and not reason:
        raise ValueError("a return reason is required")
    candidate = copy.deepcopy(record)
    candidate["status"] = target
    candidate["return_reason"] = reason if target == "returned" else None
    if target == "accepted":
        candidate["owner"] = candidate["next_owner"]
    timestamp = now()
    candidate["updated_at"] = timestamp
    event = {"at": timestamp, "event": target, "actor": actor}
    if reason:
        event["reason"] = reason
    candidate["events"].append(event)
    errors = validate_handoff(candidate)
    if errors:
        raise ValueError("; ".join(errors))
    record.clear()
    record.update(candidate)
    return record


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path: str | Path, record: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, destination)
