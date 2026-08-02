# Examples

This folder contains runnable examples for the InkCinema workflow.

## Files

- `poem_request.json`: minimal poem input request

## Run

From repository root:

```powershell
python scripts/poem_to_video.py --input examples/poem_request.json --output outputs/poem_yonge
```

Optional custom data sources:

```powershell
python scripts/poem_to_video.py --input examples/poem_request.json --output outputs/poem_yonge --knowledge knowledge/dynasty_knowledge.json --profiles templates/model_profiles.json
```

## Expected Outputs

- `outputs/poem_yonge/project.json`
- `outputs/poem_yonge/storyboard.json`
- `outputs/poem_yonge/storyboard.csv`
- `outputs/poem_yonge/research.json`
- `outputs/poem_yonge/qa_report.json`
- `outputs/poem_yonge/prompts/kling.jsonl`
- `outputs/poem_yonge/prompts/cogvideo.jsonl`
- `outputs/poem_yonge/prompts/wan.jsonl`
- `outputs/poem_yonge/prompts/veo.jsonl`
- `outputs/poem_yonge/manifest.json`

## Regression Test

```powershell
python -m unittest tests/test_adapter_regression.py -v
```

What it validates:

- stable prompt outputs across repeated runs
- model adapter parameter baselines
- aspect ratio fallback behavior (`4:3` fixture)

## CogVideoX Web Form Export

Generate paste-ready text and copy to clipboard:

```powershell
python scripts/export_cogvideox_web_form.py --input outputs/poem_yonge_cogvideox/prompts/cogvideox.jsonl --output outputs/poem_yonge_cogvideox/cogvideox_web_form.txt --format blocks --copy
```

Output file:

- `outputs/poem_yonge_cogvideox/cogvideox_web_form.txt`

Per-shot files:

```powershell
python scripts/export_cogvideox_web_form.py --input outputs/poem_yonge_cogvideox/prompts/cogvideox.jsonl --output outputs/poem_yonge_cogvideox/cogvideox_web_form.txt --format blocks --copy --split-shots
```

- `outputs/poem_yonge_cogvideox/cogvideox_web_form_shots/index.tsv`
- `outputs/poem_yonge_cogvideox/cogvideox_web_form_shots/shot_001_sh001.txt`
