# InkCinema Workflow State Machine

Version: 1.0.0

RFC: 0004

Status: Stable

---

# Purpose

This specification defines the official workflow lifecycle for every InkCinema project.

It guarantees that every Agent executes in the correct order.

No Agent may bypass the state machine.

---

# Philosophy

Workflow controls Agents.

Agents do not control Workflow.

An Agent never decides what runs next.

The Workflow Engine is the only authority responsible for state transitions.

---

# State Machine

Every project starts from

INIT

and must eventually end in either

COMPLETED

or

FAILED.

```

```text
INIT
 │
 ▼
PLANNING
 │
 ▼
RESEARCH
 │
 ▼
LITERATURE
 │
 ▼
CREATIVE
 │
 ▼
DIRECTING
 │
 ▼
STORYBOARD
 │
 ▼
VISUAL
 │
 ▼
AUDIO
 │
 ▼
PROMPT_COMPILATION
 │
 ▼
QUALITY_ASSURANCE
 │
 ▼
PUBLISHING
 │
 ▼
COMPLETED
```
