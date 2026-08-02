# Global Config

Version: 1.0.0

Status: Stable

---

# Purpose

This file defines default runtime behavior for all InkCinema OpenCode workflows.

Every workflow should read this config first, then allow per-project overrides.

---

# Runtime Defaults

runtime

timezone: Asia/Shanghai

language: zh-CN

schema_version: 1.0.0

event_protocol: 1.0.0

agent_contract: 1.0.0

---

# Pipeline Defaults

pipeline

default_workflow: poem_to_video

default_duration_seconds: 60

default_aspect_ratio: 16:9

default_resolution: 1920x1080

default_frame_rate: 24

default_shot_duration_min: 4

default_shot_duration_max: 8

---

# Agent Order

agent_order

1. executive_producer

2. research

3. literature

4. creative_director

5. director

6. storyboard

7. visual

8. audio

9. prompt_compiler

10. qa

11. publisher

---

# Target Models

targets

video_models

- kling

- cogvideo

- wan

- veo

- seedance

image_models

- flux

- midjourney

- stable_diffusion

---

# Quality Gates

quality_gates

required

- schema_valid

- timeline_valid

- continuity_valid

- historical_risk_reported

- prompt_non_empty

- export_profile_valid

warn_only

- color_palette_drift

- inconsistent_mist_density

- excessive_camera_motion

---

# Naming Convention

asset_naming

project_prefix: ic

event_prefix: evt

shot_prefix: sh

scene_prefix: sc

prompt_prefix: prm

pattern: "{project_id}/{stage}/{entity_id}.{ext}"

---

# Export Profiles

export_profiles

museum

resolution: 3840x2160

fps: 24

audio: stereo_48k

bitrate: high

web

resolution: 1920x1080

fps: 24

audio: stereo_48k

bitrate: medium

social

resolution: 1080x1920

fps: 30

audio: stereo_48k

bitrate: medium

---

# Minimal Override Example

project_overrides

duration_seconds: 45

aspect_ratio: 9:16

targets:

- kling

- wan
