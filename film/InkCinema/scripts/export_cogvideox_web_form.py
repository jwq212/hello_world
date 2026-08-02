#!/usr/bin/env python3
"""Convert CogVideoX JSONL prompts to web-form pasteable text blocks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at line {idx}: {exc}") from exc
    if not items:
        raise ValueError("Input JSONL has no rows")
    return items


def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    params = row.get("params", {})
    return {
        "shot_id": row.get("shot_id", "unknown"),
        "prompt": row.get("positive_prompt", ""),
        "negative_prompt": row.get("negative_prompt", ""),
        "aspect_ratio": params.get("aspect_ratio", ""),
        "duration": params.get("duration", ""),
        "resolution": params.get("resolution", ""),
        "fps": params.get("fps", ""),
        "seed": params.get("seed", ""),
        "motion_strength": params.get("motion_strength", ""),
    }


def to_blocks(rows: List[Dict[str, Any]]) -> str:
    sections: List[str] = []
    for index, row in enumerate(rows, start=1):
        sections.append(
            "\n".join(
                [
                    f"### Shot {index} ({row['shot_id']})",
                    "Prompt:",
                    str(row["prompt"]),
                    "",
                    "Negative Prompt:",
                    str(row["negative_prompt"]),
                    "",
                    "Aspect Ratio:",
                    str(row["aspect_ratio"]),
                    "",
                    "Duration (s):",
                    str(row["duration"]),
                    "",
                    "Resolution:",
                    str(row["resolution"]),
                    "",
                    "FPS:",
                    str(row["fps"]),
                    "",
                    "Seed:",
                    str(row["seed"]),
                    "",
                    "Motion Strength:",
                    str(row["motion_strength"]),
                ]
            )
        )
    return "\n\n" + "\n\n---\n\n".join(sections) + "\n"


def to_tsv(rows: List[Dict[str, Any]]) -> str:
    headers = [
        "shot_id",
        "prompt",
        "negative_prompt",
        "aspect_ratio",
        "duration",
        "resolution",
        "fps",
        "seed",
        "motion_strength",
    ]

    def esc(value: Any) -> str:
        text = str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")
        return text

    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(esc(row.get(h, "")) for h in headers))
    return "\n".join(lines) + "\n"


def render_shot_block(row: Dict[str, Any], index: int) -> str:
    return "\n".join(
        [
            f"### Shot {index} ({row['shot_id']})",
            "Prompt:",
            str(row["prompt"]),
            "",
            "Negative Prompt:",
            str(row["negative_prompt"]),
            "",
            "Aspect Ratio:",
            str(row["aspect_ratio"]),
            "",
            "Duration (s):",
            str(row["duration"]),
            "",
            "Resolution:",
            str(row["resolution"]),
            "",
            "FPS:",
            str(row["fps"]),
            "",
            "Seed:",
            str(row["seed"]),
            "",
            "Motion Strength:",
            str(row["motion_strength"]),
            "",
        ]
    )


def write_split_shot_files(rows: List[Dict[str, Any]], output_path: Path) -> Path:
    split_dir = output_path.parent / f"{output_path.stem}_shots"
    split_dir.mkdir(parents=True, exist_ok=True)

    index_lines: List[str] = []
    for index, row in enumerate(rows, start=1):
        filename = f"shot_{index:03d}_{row['shot_id']}.txt"
        file_path = split_dir / filename
        file_path.write_text(render_shot_block(row, index), encoding="utf-8")
        index_lines.append(f"{index}\t{row['shot_id']}\t{filename}")

    (split_dir / "index.tsv").write_text("order\tshot_id\tfile\n" + "\n".join(index_lines) + "\n", encoding="utf-8")
    return split_dir


def copy_to_clipboard(text: str) -> bool:
    try:
        import tkinter  # pylint: disable=import-outside-toplevel

        root = tkinter.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export CogVideoX JSONL prompts to web-form fields")
    parser.add_argument("--input", required=True, help="Path to CogVideoX JSONL prompt file")
    parser.add_argument("--output", help="Path to output text/tsv file")
    parser.add_argument("--format", choices=["blocks", "tsv"], default="blocks", help="Export format")
    parser.add_argument("--copy", action="store_true", help="Copy export text to clipboard")
    parser.add_argument(
        "--split-shots",
        action="store_true",
        help="Also export one numbered text file per shot for step-by-step web form filling",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    rows = [normalize_row(row) for row in read_jsonl(input_path)]

    rendered = to_blocks(rows) if args.format == "blocks" else to_tsv(rows)

    if args.output:
        output_path = Path(args.output)
    else:
        suffix = "txt" if args.format == "blocks" else "tsv"
        output_path = input_path.with_name(f"{input_path.stem}_web_form.{suffix}")

    output_path.write_text(rendered, encoding="utf-8")

    split_dir = None
    if args.split_shots:
        split_dir = write_split_shot_files(rows, output_path)

    copied = False
    if args.copy:
        copied = copy_to_clipboard(rendered)

    print(
        json.dumps(
            {
                "ok": True,
                "input": str(input_path),
                "output": str(output_path),
                "rows": len(rows),
                "format": args.format,
                "clipboard": copied,
                "split_shots": bool(args.split_shots),
                "split_dir": str(split_dir) if split_dir else "",
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
