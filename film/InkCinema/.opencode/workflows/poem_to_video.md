# Workflow: Poem to Video

Version: 1.0.0

Status: Stable

---

# Objective

Convert one poem request into a production-ready package:

- structured project object

- shot-by-shot storyboard

- visual/audio specification

- model-specific prompt pack

- export metadata

---

# Inputs

Required

- request.title

- poem.content

Optional

- request.author

- request.dynasty

- request.duration

- request.aspect_ratio

- request.output_models

---

# Stage Graph

INIT

-> PLANNING

-> RESEARCH

-> LITERATURE

-> CREATIVE

-> DIRECTING

-> STORYBOARD

-> VISUAL

-> AUDIO

-> PROMPT_COMPILATION

-> QUALITY_ASSURANCE

-> PUBLISHING

-> COMPLETED

---

# Stage Definitions

## 1) Planning (Executive Producer)

Input: user request

Output: metadata, request, workflow, planning, events

Rule: reject when title missing

Event: ProjectCreated

## 2) Research

Input: planning result

Output: research

Rule: must mark uncertainty instead of guessing

Event: ResearchCompleted

## 3) Literature

Input: project + research

Output: literature

Rule: no shot-level decisions

Event: LiteratureCompleted

## 4) Creative

Input: literature + research

Output: creative

Rule: one dominant film identity

Event: CreativeCompleted

## 5) Directing

Input: creative + literature + research

Output: director

Rule: scene-level only, no individual shots

Event: DirectorCompleted

## 6) Storyboard

Input: director + creative

Output: storyboard

Rule: each beat has at least 2 shots

Event: StoryboardCompleted

## 7) Visual

Input: storyboard + research + creative

Output: visual

Rule: keep character/environment continuity ids

Event: VisualCompleted

## 8) Audio

Input: storyboard + visual + creative

Output: audio

Rule: silence is deliberate design, not missing data

Event: AudioCompleted

## 9) Prompt Compilation

Input: storyboard + visual + audio

Output: prompt

Rule: compile from IPR; no re-interpretation

Event: PromptCompiled

## 10) QA

Input: full project

Output: qa

Rule: must report historical/continuity/schema checks

Event: QACompleted

## 11) Publishing

Input: full project + qa

Output: publish, assets index

Rule: export profile must match target platform

Event: PublishCompleted, WorkflowCompleted

---

# Retry Policy

- Agent failure appends AgentFailed

- Workflow may append RetryRequested and rerun same stage

- No event deletion allowed

---

# Minimal Deliverables

A run is considered successful only when all exist:

- `project.json`

- `storyboard.json`

- `prompts/kling.jsonl`

- `prompts/cogvideo.jsonl`

- `qa_report.json`

- `manifest.json`

---

# Shot Metadata Contract (Required Keys)

Each shot must include:

- shot_id

- scene_id

- beat_id

- duration

- camera

- lighting

- environment

- composition

- emotion

- continuity_notes

---

# Model Adapter Contract

Each adapter receives one IPR node and returns:

- positive_prompt

- negative_prompt

- params

- warnings

Adapters must never mutate source project data.
