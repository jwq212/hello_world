# Schema: Project

Version: 1.0.0

Status: Stable

---

# Purpose

Machine-readable project data contract used by all agents.

---

# JSON Schema (Draft 2020-12)

```json
{
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"$id": "https://inkcinema.dev/schema/project-1.0.0.json",
	"title": "InkCinema Project",
	"type": "object",
	"required": ["metadata", "request", "poem"],
	"properties": {
		"metadata": {
			"type": "object",
			"required": ["id", "version", "created_at", "updated_at", "language", "status"],
			"properties": {
				"id": { "type": "string", "minLength": 3 },
				"version": { "type": "string" },
				"created_at": { "type": "string", "format": "date-time" },
				"updated_at": { "type": "string", "format": "date-time" },
				"language": { "type": "string", "default": "zh-CN" },
				"status": {
					"type": "string",
					"enum": ["draft", "planning", "in_progress", "qa", "published", "failed"]
				}
			},
			"additionalProperties": true
		},
		"request": {
			"type": "object",
			"required": ["title"],
			"properties": {
				"title": { "type": "string", "minLength": 1 },
				"author": { "type": "string" },
				"dynasty": { "type": "string" },
				"style": { "type": "string" },
				"duration": { "type": "integer", "minimum": 15, "maximum": 900 },
				"resolution": { "type": "string" },
				"aspect_ratio": { "type": "string", "pattern": "^[0-9]+:[0-9]+$" },
				"output_models": {
					"type": "array",
					"items": { "type": "string" },
					"default": ["kling", "cogvideo"]
				}
			},
			"additionalProperties": true
		},
		"poem": {
			"type": "object",
			"required": ["content"],
			"properties": {
				"title": { "type": "string" },
				"author": { "type": "string" },
				"dynasty": { "type": "string" },
				"content": { "type": "string", "minLength": 1 },
				"translation": { "type": "string" },
				"annotations": { "type": "array", "items": { "type": "string" } },
				"keywords": { "type": "array", "items": { "type": "string" } }
			},
			"additionalProperties": true
		},
		"research": { "type": "object" },
		"literature": { "type": "object" },
		"creative": { "type": "object" },
		"director": { "type": "object" },
		"storyboard": {
			"type": "object",
			"properties": {
				"shots": {
					"type": "array",
					"items": { "$ref": "https://inkcinema.dev/schema/shot-1.0.0.json" }
				}
			},
			"additionalProperties": true
		},
		"visual": { "type": "object" },
		"audio": { "type": "object" },
		"prompt": { "type": "object" },
		"qa": { "type": "object" },
		"publish": { "type": "object" },
		"events": {
			"type": "array",
			"items": {
				"type": "object",
				"required": ["event_id", "sequence", "timestamp", "agent", "event_type"],
				"properties": {
					"event_id": { "type": "string" },
					"sequence": { "type": "integer", "minimum": 1 },
					"timestamp": { "type": "string", "format": "date-time" },
					"agent": { "type": "string" },
					"event_type": { "type": "string" },
					"payload": { "type": "object" }
				},
				"additionalProperties": true
			}
		}
	},
	"additionalProperties": true
}
```
