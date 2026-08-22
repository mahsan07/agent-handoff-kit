# Product Definition

## One-sentence promise

Small, durable handoff records for multi-agent workflows.

## Problem

Agent-to-agent collaboration breaks when the next worker cannot tell what was done, what remains, which assumptions are valid, or what actions are approved.

## Solution

Provide a simple handoff schema, lifecycle, and validation rules that work across vendors and storage backends.

## Users

Builders creating multi-step or multi-agent workflows that need reliable continuity.

## Core workflow

- Create a handoff
- Attach scope and artifacts
- Record decisions and assumptions
- Transfer ownership
- Verify completion or return with a failure reason

## MVP acceptance criteria

- Handoff JSON schema
- Status transitions
- Artifact references
- Assumption and decision fields
- Owner and reviewer fields
- Validator CLI

## Non-goals for the first release

- No hosted multi-tenant service
- No embedded credentials or provider accounts
- No irreversible external actions without a visible approval boundary
- No claim of production readiness before tests and evidence exist
