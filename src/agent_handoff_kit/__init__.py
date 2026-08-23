"""Public API for Agent Handoff Kit."""

from importlib import resources

from .handoff import create_handoff, transition, validate_handoff

__all__ = ["create_handoff", "transition", "validate_handoff", "schema_text"]
__version__ = "0.1.0"


def schema_text() -> str:
    """Return the bundled JSON Schema as text."""
    return resources.files(__package__).joinpath("handoff.schema.json").read_text(encoding="utf-8")
