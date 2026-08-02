#!/usr/bin/env python3
"""Post-process generated shot videos into one final poem video.

Features:
- Concatenate multiple clips in shot order.
- Generate subtitles from storyboard shot descriptions.
- Optional narration audio from a provided file.
- Optional TTS narration generation using edge-tts.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence


def run_cmd(cmd: Sequence[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + "\n\nstdout:\n"
            + proc.stdout
            + "\n\nstderr:\n"
            + proc.stderr
        )


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg and ensure it is available in PATH.")


def load_storyboard(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "shots" not in data or not isinstance(data["shots"], list):
        raise ValueError(f"Invalid storyboard format: {path}")
    return data


def format_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt_lines(storyboard: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    t = 0.0
    for idx, shot in enumerate(storyboard["shots"], start=1):
        duration = float(shot.get("duration", 0))
        text = str(shot.get("description", "")).strip()
        if not text:
            text = f"镜头 {idx}"
        start = format_srt_time(t)
        end = format_srt_time(t + max(duration, 0.01))
        lines.extend([str(idx), f"{start} --> {end}", text, ""])
        t += max(duration, 0.0)
    return lines


def write_concat_list(clips: List[Path], path: Path) -> None:
    rows = []
    for clip in clips:
        # ffmpeg concat demuxer accepts POSIX-style forward slashes.
        rows.append(f"file '{clip.resolve().as_posix()}'")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def escape_subtitle_filter_path(path: Path) -> str:
    # Escape for ffmpeg subtitles filter on Windows.
    raw = path.resolve().as_posix()
    raw = raw.replace("\\", "\\\\")
    raw = raw.replace(":", "\\:")
    raw = raw.replace("'", "\\'")
    return raw


def tts_edge(text: str, output_audio: Path, voice: str) -> None:
    try:
        import asyncio
        import edge_tts  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "edge-tts is not installed. Install with: pip install edge-tts"
        ) from exc

    async def _run() -> None:
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(str(output_audio))

    asyncio.run(_run())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble poem clips with subtitles and narration")
    parser.add_argument("--storyboard", required=True, help="Path to storyboard.json")
    parser.add_argument("--clips", nargs="+", required=True, help="Ordered clip paths, one per shot")
    parser.add_argument("--output", required=True, help="Final output .mp4 path")
    parser.add_argument("--srt-output", help="Optional path to save generated .srt")
    parser.add_argument("--narration-audio", help="Optional pre-recorded narration audio file (.mp3/.wav/.m4a)")
    parser.add_argument("--tts", action="store_true", help="Generate narration audio with edge-tts")
    parser.add_argument("--tts-text", help="Narration text for TTS. Default: all shot descriptions concatenated")
    parser.add_argument("--tts-voice", default="zh-CN-XiaoxiaoNeural", help="edge-tts voice name")
    parser.add_argument(
        "--subtitle-style",
        default="FontName=Microsoft YaHei,FontSize=26,Outline=1,Shadow=0,MarginV=40",
        help="ASS style string passed to subtitles force_style",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_ffmpeg()

    storyboard_path = Path(args.storyboard)
    clip_paths = [Path(p) for p in args.clips]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for clip in clip_paths:
        if not clip.exists():
            raise FileNotFoundError(f"Missing clip: {clip}")

    storyboard = load_storyboard(storyboard_path)
    shot_count = len(storyboard["shots"])
    if shot_count != len(clip_paths):
        raise ValueError(f"Shot count ({shot_count}) and clip count ({len(clip_paths)}) do not match")

    work_dir = output_path.parent / f".{output_path.stem}_tmp"
    work_dir.mkdir(parents=True, exist_ok=True)

    concat_txt = work_dir / "concat.txt"
    merged_mp4 = work_dir / "merged.mp4"
    with_audio_mp4 = work_dir / "with_audio.mp4"

    srt_path = Path(args.srt_output) if args.srt_output else output_path.with_suffix(".srt")
    srt_lines = build_srt_lines(storyboard)
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    write_concat_list(clip_paths, concat_txt)
    run_cmd([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_txt),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(merged_mp4),
    ])

    narration_audio = Path(args.narration_audio) if args.narration_audio else None

    if args.tts:
        tts_text = args.tts_text
        if not tts_text:
            tts_text = "。".join(str(shot.get("description", "")).strip() for shot in storyboard["shots"]).strip("。") + "。"
        narration_audio = work_dir / "narration_tts.mp3"
        tts_edge(tts_text, narration_audio, args.tts_voice)

    input_for_sub = merged_mp4
    if narration_audio is not None:
        if not narration_audio.exists():
            raise FileNotFoundError(f"Narration audio not found: {narration_audio}")
        run_cmd([
            "ffmpeg",
            "-y",
            "-i",
            str(merged_mp4),
            "-i",
            str(narration_audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(with_audio_mp4),
        ])
        input_for_sub = with_audio_mp4

    sub_filter_path = escape_subtitle_filter_path(srt_path)
    run_cmd([
        "ffmpeg",
        "-y",
        "-i",
        str(input_for_sub),
        "-vf",
        f"subtitles='{sub_filter_path}':force_style='{args.subtitle_style}'",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "medium",
        "-c:a",
        "copy",
        str(output_path),
    ])

    print(
        json.dumps(
            {
                "ok": True,
                "storyboard": str(storyboard_path),
                "clips": [str(p) for p in clip_paths],
                "srt": str(srt_path),
                "output": str(output_path),
                "narration": str(narration_audio) if narration_audio else "",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
