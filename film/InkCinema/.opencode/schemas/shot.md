# Schema: Shot

Version: 1.0.0

Status: Stable

---

# Purpose

Reusable shot-level contract used in storyboard and prompt compilation.

---

# JSON Schema (Draft 2020-12)

```json
{
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"$id": "https://inkcinema.dev/schema/shot-1.0.0.json",
	"title": "InkCinema Shot",
	"type": "object",
	"required": [
		"shot_id",
		"scene_id",
		"beat_id",
		"duration",
		"description",
		"camera",
		"lighting",
		"environment",
		"composition",
		"emotion"
	],
	"properties": {
		"shot_id": { "type": "string", "pattern": "^sh[0-9]{3}$" },
		"scene_id": { "type": "string", "pattern": "^sc[0-9]{2}$" },
		"beat_id": { "type": "string", "pattern": "^bt[0-9]{2}$" },
		"title": { "type": "string" },
		"purpose": { "type": "string" },
		"duration": { "type": "number", "minimum": 1, "maximum": 30 },
		"description": { "type": "string", "minLength": 1 },
		"camera": {
			"type": "object",
			"required": ["shot_type", "lens", "motion"],
			"properties": {
				"shot_type": {
					"type": "string",
					"enum": ["Extreme Wide", "Wide", "Medium", "Close Up", "POV", "Detail Shot"]
				},
				"lens": { "type": "string", "enum": ["35mm", "50mm", "85mm"] },
				"height": { "type": "string" },
				"angle": { "type": "string" },
				"motion": {
					"type": "string",
					"enum": ["Static", "Slow Push", "Slow Pull", "Slow Pan", "Slow Tilt", "Gentle Tracking"]
				}
			},
			"additionalProperties": true
		},
		"lighting": {
			"type": "object",
			"properties": {
				"time": { "type": "string" },
				"temperature": { "type": "string" },
				"contrast": { "type": "string" }
			},
			"additionalProperties": true
		},
		"environment": {
			"type": "object",
			"properties": {
				"location": { "type": "string" },
				"weather": { "type": "string" },
				"season": { "type": "string" }
			},
			"additionalProperties": true
		},
		"composition": { "type": "string" },
		"emotion": { "type": "string" },
		"continuity_notes": { "type": "array", "items": { "type": "string" } },
		"visual_constraints": { "type": "array", "items": { "type": "string" } },
		"priority": { "type": "string", "enum": ["high", "normal", "low"] }
	},
	"additionalProperties": true
}
```
