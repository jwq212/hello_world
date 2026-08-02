# Agent Event Protocol (AEP)

Version: 1.0.0

RFC: 0003

Status: Stable

---

# Purpose

This specification defines how AI Agents communicate through immutable events.

Agents never overwrite project state.

Agents append events.

The current Project state is reconstructed from the event stream.

---

# Philosophy

State is temporary.

Events are permanent.

Every important decision must become an event.

Every event must be reproducible.

Every event must be auditable.

---

# Event Sourcing

InkCinema follows an Event Sourcing architecture.

Project

↓

Event Stream

↓

Snapshot

↓

Current State

Current State must never become the source of truth.

The Event Stream is the source of truth.

---

# Event Principles

Every event must satisfy:

Immutable

Append-only

Timestamped

Versioned

Deterministic

Auditable

---

# Event Structure

Every event contains

event_id

project_id

workflow_id

sequence

timestamp

agent

event_type

schema_version

payload

metadata

---

Example

{
  "event_id": "evt_000001",
  "project_id": "poem_0001",
  "workflow_id": "workflow_001",
  "sequence": 1,
  "timestamp": "2026-08-02T12:00:00Z",
  "agent": "Producer",
  "event_type": "ProjectCreated",
  "schema_version": "1.0.0",
  "payload": {},
  "metadata": {}
}

---

# Event IDs

Every event_id must be globally unique.

Format

evt_000001

evt_000002

evt_000003

Never reuse IDs.

---

# Sequence

Events are ordered.

Sequence must always increase.

No gaps.

No duplicates.

---

# Event Types

ProjectCreated

ResearchCompleted

LiteratureCompleted

CreativeCompleted

DirectorCompleted

StoryboardCompleted

VisualCompleted

AudioCompleted

PromptCompiled

QACompleted

PublishCompleted

WorkflowCompleted

WorkflowFailed

AgentFailed

RetryRequested

SnapshotCreated

ProjectArchived

Future versions may introduce additional event types.

---

# Payload

Payload contains only data produced by the current Agent.

Never copy the entire Project.

Only append new information.

---

# Metadata

Metadata may contain

execution_time

token_usage

llm

model

temperature

retry_count

trace_id

---

# Immutable Rule

Events must never change.

If a correction is required

Create a new event.

Never edit previous events.

---

# Retry

Retries are represented as events.

Example

RetryRequested

↓

LiteratureCompleted

Previous events remain untouched.

---

# Rollback

Rollback never deletes events.

Rollback creates

RollbackRequested

↓

RollbackCompleted

The workflow reconstructs state before the target event.

---

# Snapshots

Snapshots improve performance.

Snapshots are disposable.

Snapshots may be regenerated at any time.

Event Stream always has higher priority.

---

# Event Replay

The entire Project must be reproducible by replaying events.

Replay

↓

Current Project

No hidden state is allowed.

---

# Failure

When an Agent fails

Generate

AgentFailed

Payload contains

reason

recoverable

recommendation

No exception should silently terminate the workflow.

---

# Validation

Before appending

Validate

schema_version

sequence

ownership

dependencies

---

# Ownership

Only the executing Agent may create its own completion event.

Example

Literature Agent

↓

LiteratureCompleted

QA Agent

↓

QACompleted

Producer Agent must never emit

StoryboardCompleted

---

# Audit Trail

Every important decision must become an event.

Nothing important should exist only inside prompts.

---

# Event Version

Each event declares

schema_version

event_version

Future parsers should ignore unknown fields.

---

# Compatibility

Events are append-only.

Older consumers should continue functioning.

Breaking changes require a new schema version.

---

# Security

Events must never contain

API Keys

Hidden prompts

Secrets

Credentials

Private user data

---

# Final Principle

The history of the project is more valuable than the current state.

Never lose history.

Never rewrite history.

Only append truth.