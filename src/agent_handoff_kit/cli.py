from __future__ import annotations

import argparse
import json

from .handoff import create_handoff, load, save, transition, validate_handoff


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="agent-handoff")
    commands = root.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="create a draft handoff")
    create.add_argument("path")
    create.add_argument("--title", required=True)
    create.add_argument("--objective", required=True)
    create.add_argument("--owner", required=True)
    create.add_argument("--next-owner", required=True)
    create.add_argument("--reviewer", required=True)
    create.add_argument("--scope", action="append", default=[])
    create.add_argument("--id")
    validate = commands.add_parser("validate", help="validate a handoff")
    validate.add_argument("path")
    show = commands.add_parser("show", help="print a handoff")
    show.add_argument("path")
    update = commands.add_parser("add", help="append structured context")
    update.add_argument("path")
    update.add_argument("field", choices=["scope", "decisions", "assumptions", "risks", "next_actions", "verification"])
    update.add_argument("value")
    artifact = commands.add_parser("add-artifact", help="attach an artifact reference")
    artifact.add_argument("path")
    artifact.add_argument("--kind", choices=["file", "url", "commit", "note"], required=True)
    artifact.add_argument("--uri", required=True)
    artifact.add_argument("--description", default="")
    move = commands.add_parser("transition", help="move through the handoff lifecycle")
    move.add_argument("path")
    move.add_argument("status", choices=["ready", "accepted", "completed", "returned"])
    move.add_argument("--actor", required=True)
    move.add_argument("--reason")
    return root


def main(argv: list[str] | None = None) -> int:
    root = parser()
    args = root.parse_args(argv)
    try:
        if args.command == "create":
            record = create_handoff(args.title, args.objective, args.owner, args.next_owner, args.reviewer,
                                    handoff_id=args.id, scope=args.scope)
            save(args.path, record)
            output = record
        else:
            record = load(args.path)
            if args.command == "validate":
                errors = validate_handoff(record)
                output = {"valid": not errors, "errors": errors}
                print(json.dumps(output, indent=2, sort_keys=True))
                return 0 if not errors else 1
            if args.command == "show":
                output = record
            elif args.command == "add":
                record[args.field].append(args.value)
                save(args.path, record)
                output = record
            elif args.command == "add-artifact":
                record["artifacts"].append({"kind": args.kind, "uri": args.uri, "description": args.description})
                save(args.path, record)
                output = record
            else:
                output = transition(record, args.status, args.actor, reason=args.reason)
                save(args.path, output)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        root.error(str(error))
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0
