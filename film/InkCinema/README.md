# InkCinema

> AI-native filmmaking framework for Chinese classical literature.

InkCinema is an OpenCode-first multi-agent filmmaking framework designed to transform Chinese classical poetry into museum-quality cinematic AI videos.

Instead of writing prompts manually, InkCinema organizes a professional virtual film crew powered by specialized AI Agents.

Each agent has a single responsibility and communicates through a shared project protocol.

The final output can be directly used for:

- Kling
- CogVideo
- Wan
- Seedance
- Veo
- Midjourney
- Flux
- Stable Diffusion

---

# Vision

Build the world's best AI filmmaking framework for Chinese culture.

Not another prompt collection.

Not another AI workflow.

InkCinema aims to become the operating system for AI-native Chinese cultural filmmaking.

---

# Quick Start (Runnable)

1) Prepare an input request JSON (example provided)

`examples/poem_request.json`

2) Run the local compiler pipeline

```powershell
python scripts/poem_to_video.py --input examples/poem_request.json --output outputs/poem_yonge
```

Optional custom sources:

```powershell
python scripts/poem_to_video.py --input examples/poem_request.json --output outputs/poem_yonge --knowledge knowledge/dynasty_knowledge.json --profiles templates/model_profiles.json
```

3) Use generated model prompt packs

- `outputs/poem_yonge/prompts/kling.jsonl`
- `outputs/poem_yonge/prompts/cogvideo.jsonl`
- `outputs/poem_yonge/prompts/wan.jsonl`
- `outputs/poem_yonge/prompts/veo.jsonl`

4) Inspect storyboard and project state

- `outputs/poem_yonge/storyboard.json`
- `outputs/poem_yonge/project.json`
- `outputs/poem_yonge/research.json`
- `outputs/poem_yonge/qa_report.json`

5) Run adapter regression tests

```powershell
python -m unittest tests/test_adapter_regression.py -v
```

Regression suite coverage:

- deterministic prompt generation across repeated runs
- per-model parameter baseline lock (duration, resolution, seed, motion strength)
- aspect ratio fallback behavior by model profile

6) One-click export for CogVideoX web form

```powershell
python scripts/export_cogvideox_web_form.py --input outputs/poem_yonge_cogvideox/prompts/cogvideox.jsonl --output outputs/poem_yonge_cogvideox/cogvideox_web_form.txt --format blocks --copy
```

Then paste directly into the CogVideoX web form fields by shot.

Generate per-shot numbered files at the same time:

```powershell
python scripts/export_cogvideox_web_form.py --input outputs/poem_yonge_cogvideox/prompts/cogvideox.jsonl --output outputs/poem_yonge_cogvideox/cogvideox_web_form.txt --format blocks --copy --split-shots
```

This creates:

- `outputs/poem_yonge_cogvideox/cogvideox_web_form_shots/index.tsv`
- `outputs/poem_yonge_cogvideox/cogvideox_web_form_shots/shot_001_sh001.txt`
- `outputs/poem_yonge_cogvideox/cogvideox_web_form_shots/shot_002_sh002.txt`

7) Post-production: merge clips + add subtitles + add narration

Install required tools first:

```powershell
pip install edge-tts
```

Prepare generated shot videos in order (example names):

- `outputs/poem_yonge_cogvideox/renders/sh001.mp4`
- `outputs/poem_yonge_cogvideox/renders/sh002.mp4`

Run one command to concatenate, generate SRT from storyboard, create TTS narration, and burn subtitles:

```powershell
python scripts/assemble_poem_video.py --storyboard outputs/poem_yonge_cogvideox/storyboard.json --clips outputs/poem_yonge_cogvideox/renders/sh001.mp4 outputs/poem_yonge_cogvideox/renders/sh002.mp4 --tts --output outputs/poem_yonge_cogvideox/final_poem_video.mp4
```

If you already have your own narration audio file:

```powershell
python scripts/assemble_poem_video.py --storyboard outputs/poem_yonge_cogvideox/storyboard.json --clips outputs/poem_yonge_cogvideox/renders/sh001.mp4 outputs/poem_yonge_cogvideox/renders/sh002.mp4 --narration-audio outputs/poem_yonge_cogvideox/narration.mp3 --output outputs/poem_yonge_cogvideox/final_poem_video.mp4
```

---

# Current Implementation Status

Implemented in this repository now:

- OpenCode agent role documents
- Workflow contract for poem-to-video
- Global runtime configuration
- Project and Shot machine-readable schema definitions
- Runnable local pipeline script (poem request -> storyboard -> prompt pack)
- Local historical knowledge retrieval with confidence scoring
- Model parameter template library with per-platform auto adaptation
- Automatic QA scorer (continuity, dynasty consistency, rhythm, color drift)
- Example request and output artifact structure
- Adapter regression test suite with baseline assertions

Planned next:

- Agent-level execution orchestration
- Prompt regression tests for model adapters
- Expanded dynasty knowledge coverage

---

# Design Philosophy

InkCinema follows several core principles.

## AI Agents instead of Monolithic Prompts

Each agent performs exactly one professional responsibility.

Example:

User

↓

Producer

↓

Literature

↓

Creative Director

↓

Director

↓

Storyboard

↓

Visual

↓

Prompt Compiler

↓

QA

↓

Publisher

---

## Prompt is NOT the source of truth.

Prompt is compiled.

The source of truth is structured knowledge.

Agents generate structured outputs.

Prompt Compiler converts structured outputs into model-specific prompts.

---

## Model Independent

InkCinema never depends on a specific model.

Today:

Kling

Tomorrow:

CogVideo

Future:

Unknown AI model

The workflow should never change.

Only Prompt Compiler changes.

---

## Historical Accuracy First

Every generated scene should respect

- Dynasty
- Architecture
- Costume
- Plants
- Animals
- Geography
- Etiquette
- Culture

---

## Chinese Aesthetics First

InkCinema does not pursue exaggerated visual effects.

It pursues

Space

Rhythm

Silence

Breathing

Mood

Oriental philosophy

---

# Architecture

```text
User
 │
 ▼
Producer
 │
 ▼
Literature
 │
 ▼
Creative Director
 │
 ▼
Director
 │
 ▼
Storyboard
 │
 ▼
Visual
 │
 ▼
Prompt Compiler
 │
 ▼
QA
 │
 ▼
Publisher
```

---

# Repository Structure

```
inkcinema/

README.md

.opencode/

agents/

workflows/

schemas/

memory/

knowledge/

templates/

outputs/

examples/
```

---

# Agent Principles

Every Agent should:

- Have only one responsibility
- Produce structured outputs
- Never generate unrelated content
- Never modify another Agent's responsibilities
- Follow project schema
- Respect Style Bible
- Remain model independent

---

# Workflow

Every project follows the same workflow.

Poem

↓

Project

↓

Literature

↓

Director

↓

Storyboard

↓

Visual

↓

Prompt Compiler

↓

QA

↓

Publisher

---

# Supported Video Models

Current:

- Kling
- CogVideo
- Wan
- Veo
- Seedance

Future adapters can be added without changing any workflow.

---

# Project Goals

Version 0.1

- OpenCode Workflow
- Poetry to Storyboard
- Prompt Compiler
- Kling Support
- CogVideo Support
- Wan Support

Version 0.2

- Knowledge Base
- Character Bible
- Environment Bible
- Style Bible

Version 0.3

- Automatic QA
- Automatic Consistency Checking
- Prompt Optimization

Version 1.0

Open Source Release

---

# License

MIT License

---

# Author

Designed for AI-native filmmaking.

Built with OpenCode.