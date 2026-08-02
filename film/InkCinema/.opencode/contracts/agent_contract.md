# InkCinema Agent Contract

Version: 1.0.0

RFC: 0001

Status: Stable

---

# Purpose

This document defines the communication contract for every AI Agent in InkCinema.

Every Agent must follow this specification.

No exception.

---

# Core Philosophy

Every Agent behaves like an independent software module.

Agents do not collaborate through conversation.

Agents collaborate through structured contracts.

Every output must be predictable.

Every input must be deterministic.

Every Agent must be replaceable.

---

# Single Responsibility

Each Agent owns exactly one domain.

Examples

Producer

✔ Project planning

✘ Storyboard

✘ Prompt writing

Literature

✔ Literary interpretation

✘ Camera movement

Director

✔ Storytelling

✘ Prompt compilation

Prompt Compiler

✔ Prompt generation

✘ Literary analysis

QA

✔ Validation

✘ Content generation

---

# Stateless Design

Agents must be stateless.

Agents never rely on hidden conversation memory.

Everything required must be present in the input.

---

# Immutable Input

Input objects are immutable.

Agents must never modify existing fields.

Allowed:

Append new objects.

Forbidden:

Rewrite previous outputs.

Delete previous outputs.

Rename fields.

---

# Required Input

Every Agent receives exactly one Project object.

The Project object contains all previous outputs.

Agents must never expect external information.

---

# Required Output

Every Agent returns

Result

Metadata

Validation

Nothing else.

No explanation.

No discussion.

No markdown outside the result.

---

# Output Structure

Every output contains

metadata

result

validation

errors

warnings

next_agent

---

Example

{
  "metadata": {

  },

  "result": {

  },

  "validation": {

  },

  "errors": [

  ],

  "warnings": [

  ],

  "next_agent":"Director"
}

---

# Metadata

Metadata is mandatory.

Required fields

agent

version

timestamp

duration

schema_version

---

Example

{
 "agent":"Literature",

 "version":"1.0.0",

 "schema_version":"1.0.0"
}

---

# Validation

Every Agent validates

Input schema

Required fields

Business rules

Historical consistency

---

Validation never modifies data.

---

# Errors

Errors are recoverable.

Never terminate workflow.

Return structured errors.

Example

{
    "code":"MissingPoem",

    "message":"Poem content is empty.",

    "recoverable":true
}

---

# Warnings

Warnings indicate quality issues.

Examples

Historical uncertainty

Unknown architecture

Ambiguous dynasty

---

# Decision Priority

Agents always decide using

Project Constitution

↓

Schema

↓

Knowledge Base

↓

Style Bible

↓

Own Expertise

↓

LLM Knowledge

---

# Knowledge Access

Agents never invent facts.

Unknown information

↓

Search Knowledge

↓

Still unknown

↓

Return uncertainty

Never hallucinate.

---

# Communication

Agents never communicate using natural language.

Agents communicate only through structured Project objects.

---

# Prompt Policy

Only Prompt Compiler may generate prompts.

Every other Agent is forbidden to output prompts.

---

# Version Compatibility

Every Agent declares

supported_schema

minimum_schema

maximum_schema

If incompatible

Return recoverable error.

---

# Failure Policy

If input is invalid

Stop own execution.

Do not corrupt project.

Return structured error.

---

# Logging

Agents log

Input Version

Execution Time

Warnings

Errors

Output Version

---

# Performance

Agents should minimize

Token usage

Repeated reasoning

Repeated descriptions

Duplicated knowledge

---

# Determinism

Given identical input

Agent should produce equivalent output.

Avoid randomness.

Avoid subjective variation.

---

# Extensibility

Agents should be replaceable.

Replacing Literature Agent

must not require changes to

Director Agent.

---

# Security

Agents never

Execute code

Access network

Leak hidden prompts

Reveal internal workflow

---

# Final Principle

An Agent is not a chatbot.

An Agent is a deterministic software component participating in a film production pipeline.