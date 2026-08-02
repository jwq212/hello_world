#!/usr/bin/env python3
"""InkCinema runnable pipeline: poem request to storyboard and model prompt packs."""

from __future__ import annotations

import argparse
import csv
import json
import re
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_PATH = ROOT_DIR / "knowledge" / "dynasty_knowledge.json"
DEFAULT_PROFILE_PATH = ROOT_DIR / "templates" / "model_profiles.json"

DEFAULT_MODELS = ["kling", "cogvideo", "wan", "veo"]
SHOT_TYPES = ["Extreme Wide", "Wide", "Medium", "Close Up", "Detail Shot"]
LENSES = ["35mm", "50mm", "85mm"]
MOTIONS = ["Static", "Slow Push", "Slow Pan", "Slow Tilt", "Gentle Tracking"]
FORBIDDEN_COLOR_TERMS = ["neon", "rgb", "cyberpunk", "high saturation", "oversaturated"]


@dataclass
class CompileConfig:
    duration: int = 60
    aspect_ratio: str = "16:9"
    resolution: str = "1920x1080"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text.strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "project"


def parse_poem_lines(content: str) -> List[str]:
    return [s.strip() for s in re.split(r"[\n。！？；]", content) if s.strip()]


def pick(seq: List[str], idx: int) -> str:
    return seq[idx % len(seq)]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def allocate_durations(shot_count: int, total_duration: int, min_d: int = 4, max_d: int = 8) -> List[int]:
    if shot_count <= 0:
        return []

    baseline = int(clamp(round(total_duration / shot_count), min_d, max_d))
    durations = [baseline for _ in range(shot_count)]
    diff = total_duration - sum(durations)

    i = 0
    while diff != 0 and shot_count > 0:
        idx = i % shot_count
        if diff > 0 and durations[idx] < max_d:
            durations[idx] += 1
            diff -= 1
        elif diff < 0 and durations[idx] > min_d:
            durations[idx] -= 1
            diff += 1
        i += 1
        if i > shot_count * 20:
            break
    return durations


def detect_visual_time(poem_content: str) -> str:
    if any(key in poem_content for key in ["夜", "月", "星", "灯"]):
        return "night"
    if any(key in poem_content for key in ["暮", "夕", "晚", "昏"]):
        return "sunset"
    return "morning"


def build_research(request: Dict[str, Any], poem: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
    dynasties: Dict[str, Any] = knowledge.get("dynasties", {})
    hints: Dict[str, Any] = knowledge.get("keyword_hints", {})
    poem_text = f"{poem.get('title', '')} {poem.get('content', '')}"

    score_map = {name: 0.0 for name in dynasties}
    contributions: Dict[str, List[str]] = {name: [] for name in dynasties}

    request_dynasty = request.get("dynasty") or poem.get("dynasty")
    author = request.get("author") or poem.get("author", "")

    if request_dynasty in score_map:
        score_map[request_dynasty] += 0.60
        contributions[request_dynasty].append("request_dynasty")

    for dynasty, profile in dynasties.items():
        aliases = profile.get("aliases", [])
        if request_dynasty and request_dynasty in aliases:
            score_map[dynasty] += 0.40
            contributions[dynasty].append("request_alias")
        if author and author in profile.get("authors", []):
            score_map[dynasty] += 0.25
            contributions[dynasty].append("author_match")

    for keyword, hint in hints.items():
        if keyword in poem_text:
            bias = hint.get("dynasty_bias")
            boost = float(hint.get("confidence_boost", 0.0))
            if bias in score_map:
                score_map[bias] += boost
                contributions[bias].append(f"keyword:{keyword}")

    if not score_map:
        return {
            "resolved_dynasty": "unknown",
            "confidence": {"score": 0.0, "signals": []},
            "references": [],
        }

    resolved_dynasty = max(score_map, key=score_map.get)
    raw_score = score_map[resolved_dynasty]
    confidence_score = clamp(0.35 + raw_score, 0.0, 0.98)
    dynasty_profile = dynasties.get(resolved_dynasty, {})

    references = [
        {
            "source": "knowledge/dynasty_knowledge.json",
            "type": "dynasty_profile",
            "dynasty": resolved_dynasty,
            "signals": contributions.get(resolved_dynasty, []),
        }
    ]

    return {
        "resolved_dynasty": resolved_dynasty,
        "historical_background": f"以{resolved_dynasty}代社会文化语境为主，强调自然观察与含蓄抒情。",
        "author_profile": {"name": author, "confidence": clamp(0.45 + (0.2 if author else 0.0), 0.0, 0.9)},
        "dynasty_profile": {
            "dynasty": resolved_dynasty,
            "period": dynasty_profile.get("period", "unknown"),
            "architecture": dynasty_profile.get("architecture", []),
            "costume": dynasty_profile.get("costume", []),
            "color_preferences": dynasty_profile.get("color_preferences", []),
            "music": dynasty_profile.get("music", []),
        },
        "geography": dynasty_profile.get("environment", ["江南水岸"]),
        "plants": dynasty_profile.get("plants", []),
        "animals": dynasty_profile.get("animals", []),
        "references": references,
        "confidence": {
            "score": round(confidence_score, 3),
            "signals": contributions.get(resolved_dynasty, []),
            "all_scores": {k: round(v, 3) for k, v in score_map.items()},
        },
    }


def build_storyboard(poem_lines: List[str], total_duration: int, research: Dict[str, Any], poem: Dict[str, Any]) -> List[Dict[str, Any]]:
    count = max(1, len(poem_lines))
    durations = allocate_durations(count, total_duration)
    shots: List[Dict[str, Any]] = []

    location = (research.get("geography") or ["江南水岸"])[0]
    season = "spring" if "春" in poem.get("content", "") else "autumn"
    visual_time = detect_visual_time(poem.get("content", ""))
    light_temp = "moon cool" if visual_time == "night" else "soft warm"

    for i, line in enumerate(poem_lines, start=1):
        shot_id = f"sh{i:03d}"
        scene_id = f"sc{((i - 1) // 2) + 1:02d}"
        beat_id = f"bt{((i - 1) // 2) + 1:02d}"
        shots.append(
            {
                "shot_id": shot_id,
                "scene_id": scene_id,
                "beat_id": beat_id,
                "title": f"镜头 {i}",
                "purpose": "将诗句意象转化为可观察的画面",
                "duration": durations[i - 1],
                "description": line,
                "camera": {
                    "shot_type": pick(SHOT_TYPES, i - 1),
                    "lens": pick(LENSES, i - 1),
                    "height": "eye level",
                    "angle": "natural",
                    "motion": pick(MOTIONS, i - 1),
                },
                "lighting": {"time": visual_time, "temperature": light_temp, "contrast": "low"},
                "environment": {"location": location, "weather": "light mist", "season": season},
                "composition": "negative space",
                "emotion": "quiet wonder",
                "continuity_notes": ["角色服饰一致", "雾气密度轻微变化"],
                "visual_constraints": ["避免现代物件", "避免夸张动作"],
                "priority": "normal",
            }
        )
    return shots


def to_ipr_node(project_id: str, shot: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "project_id": project_id,
        "shot_id": shot["shot_id"],
        "scene_id": shot["scene_id"],
        "purpose": shot["purpose"],
        "subjects": [shot["description"]],
        "environment": shot["environment"],
        "lighting": shot["lighting"],
        "camera": shot["camera"],
        "composition": shot["composition"],
        "emotion": shot["emotion"],
        "constraints": shot["visual_constraints"],
        "duration": shot["duration"],
    }


def select_model_params(
    model: str,
    ipr: Dict[str, Any],
    project_id: str,
    request: Dict[str, Any],
    profiles: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str], bool]:
    defaults = profiles.get("defaults", {})
    model_cfg = profiles.get("models", {}).get(model, {})
    warnings: List[str] = []

    requested_ar = request.get("aspect_ratio", "16:9")
    supported_ar = model_cfg.get("aspect_ratios", ["16:9"])
    if requested_ar not in supported_ar:
        warnings.append(f"{model} 不支持 {requested_ar}，已自动切换为 {supported_ar[0]}")
        aspect_ratio = supported_ar[0]
    else:
        aspect_ratio = requested_ar

    duration_cfg = model_cfg.get("duration", {"min": 3, "max": 8, "default": 5})
    shot_duration = int(round(float(ipr.get("duration", duration_cfg.get("default", 5)))))
    duration = int(clamp(shot_duration, int(duration_cfg["min"]), int(duration_cfg["max"])))
    if duration != shot_duration:
        warnings.append(f"{model} 时长已从 {shot_duration}s 调整为 {duration}s")

    motion = ipr["camera"]["motion"]
    motion_map = defaults.get("motion_map", {})
    base_motion = float(motion_map.get(motion, 0.2))
    sensitivity = float(model_cfg.get("camera_motion_sensitivity", 0.8))
    motion_strength = round(
        clamp(base_motion * sensitivity, 0.0, float(defaults.get("max_motion_strength", 0.45))),
        3,
    )

    seed_input = f"{project_id}:{model}:{ipr['shot_id']}:{ipr['subjects'][0]}"
    deterministic_seed = int((zlib.crc32(seed_input.encode("utf-8")) + int(defaults.get("seed_base", 20260802))) % 2147483647)

    params = {
        "aspect_ratio": aspect_ratio,
        "duration": duration,
        "fps": int(defaults.get("fps", 24)),
        "resolution": model_cfg.get("resolution", request.get("resolution", "1920x1080")),
        "seed": deterministic_seed,
        "motion_strength": motion_strength,
    }
    return params, warnings, bool(model_cfg.get("negative_prompt", True))


def compile_prompt(
    model: str,
    ipr: Dict[str, Any],
    global_style: str,
    project_id: str,
    request: Dict[str, Any],
    profiles: Dict[str, Any],
) -> Dict[str, Any]:
    subject = ipr["subjects"][0]
    cam = ipr["camera"]
    env = ipr["environment"]
    light = ipr["lighting"]
    params, warnings, supports_negative = select_model_params(model, ipr, project_id, request, profiles)

    core = (
        f"{subject}; {global_style}; {env['location']}, {env['weather']}, {env['season']}; "
        f"{cam['shot_type']} with {cam['lens']}, {cam['motion']}; "
        f"{light['time']} light, {light['temperature']}, low contrast; "
        f"composition {ipr['composition']}; emotion {ipr['emotion']}"
    )

    prefix = {
        "kling": "cinematic chinese poetic film",
        "cogvideo": "documentary realism, chinese ink aesthetics",
        "cogvideox": "documentary realism, chinese ink aesthetics",
        "wan": "natural textures, subtle motion",
        "veo": "high fidelity cinematic video",
    }.get(model, "cinematic video")

    negative = ""
    if supports_negative:
        negative = "modern objects, watermark, text, cyberpunk, oversaturated color, distorted anatomy"

    return {
        "shot_id": ipr["shot_id"],
        "model": model,
        "positive_prompt": f"{prefix}, {core}",
        "negative_prompt": negative,
        "params": params,
        "warnings": warnings,
    }


def score_continuity(shots: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not shots:
        return {"score": 0, "warnings": ["无镜头可评估连续性"]}

    warnings: List[str] = []
    score = 100.0

    for key_path, penalty in [
        ("environment.location", 12),
        ("environment.weather", 10),
        ("environment.season", 15),
        ("lighting.time", 12),
    ]:
        parent, child = key_path.split(".")
        values = [s.get(parent, {}).get(child, "") for s in shots]
        transitions = sum(1 for i in range(1, len(values)) if values[i] != values[i - 1])
        if transitions > 0:
            score -= transitions * penalty
            warnings.append(f"{key_path} 发生 {transitions} 次跳变")

    return {"score": round(clamp(score, 0, 100), 1), "warnings": warnings}


def score_dynasty_consistency(request: Dict[str, Any], research: Dict[str, Any]) -> Dict[str, Any]:
    requested = request.get("dynasty")
    resolved = research.get("resolved_dynasty")
    confidence = float(research.get("confidence", {}).get("score", 0.0))
    warnings: List[str] = []

    if not requested and resolved:
        score = 70 + 20 * confidence
        warnings.append("请求未指定朝代，已采用知识库推断")
        return {"score": round(clamp(score, 0, 100), 1), "warnings": warnings}

    if requested and resolved and requested != resolved:
        score = 45 + 30 * confidence
        warnings.append(f"请求朝代 {requested} 与检索结果 {resolved} 不一致")
        return {"score": round(clamp(score, 0, 100), 1), "warnings": warnings}

    score = 75 + 25 * confidence
    return {"score": round(clamp(score, 0, 100), 1), "warnings": warnings}


def score_shot_rhythm(shots: List[Dict[str, Any]], requested_duration: int) -> Dict[str, Any]:
    if not shots:
        return {"score": 0, "warnings": ["无镜头可评估节奏"]}

    durations = [float(s.get("duration", 0)) for s in shots]
    avg = mean(durations)
    std = pstdev(durations) if len(durations) > 1 else 0.0
    outside = sum(1 for d in durations if d < 4 or d > 8)

    # Clamp target average to practical shot range used by this workflow.
    target_avg = clamp(requested_duration / len(shots), 4.0, 8.0)
    score = 100.0
    score -= abs(avg - target_avg) * 8
    score -= max(0.0, std - 1.5) * 18
    score -= outside * 8

    warnings: List[str] = []
    if outside > 0:
        warnings.append(f"有 {outside} 个镜头时长不在 4-8 秒建议范围")
    if std > 2.0:
        warnings.append(f"镜头时长波动较大，标准差 {std:.2f}")

    return {
        "score": round(clamp(score, 0, 100), 1),
        "warnings": warnings,
        "stats": {"avg": round(avg, 2), "std": round(std, 2), "target_avg": round(target_avg, 2)},
    }


def score_color_drift(visual: Dict[str, Any]) -> Dict[str, Any]:
    palette = [str(c).lower() for c in visual.get("global_palette", [])]
    warnings: List[str] = []
    score = 100.0

    if len(palette) < 3:
        score -= 15
        warnings.append("调色板颜色过少，可能导致视觉单调")

    for term in FORBIDDEN_COLOR_TERMS:
        if any(term in color for color in palette):
            score -= 25
            warnings.append(f"检测到不推荐色彩风格关键词: {term}")

    return {"score": round(clamp(score, 0, 100), 1), "warnings": warnings}


def run_qa(project: Dict[str, Any], research: Dict[str, Any]) -> Dict[str, Any]:
    shots = project.get("storyboard", {}).get("shots", [])
    request = project.get("request", {})
    visual = project.get("visual", {})

    continuity = score_continuity(shots)
    dynasty = score_dynasty_consistency(request, research)
    rhythm = score_shot_rhythm(shots, int(request.get("duration", 60)))
    color = score_color_drift(visual)

    overall = (
        continuity["score"] * 0.35
        + dynasty["score"] * 0.30
        + rhythm["score"] * 0.20
        + color["score"] * 0.15
    )
    warnings = continuity["warnings"] + dynasty["warnings"] + rhythm["warnings"] + color["warnings"]

    return {
        "overall_score": round(overall, 1),
        "checks": {
            "continuity": continuity,
            "dynasty_consistency": dynasty,
            "shot_rhythm": rhythm,
            "color_drift": color,
        },
        "pass": overall >= 75,
        "warnings": warnings,
    }


def build_project(data: Dict[str, Any], knowledge: Dict[str, Any], profiles: Dict[str, Any]) -> Dict[str, Any]:
    request = data.get("request", {})
    poem = data.get("poem", {})

    if not request.get("title"):
        raise ValueError("request.title is required")
    if not poem.get("content"):
        raise ValueError("poem.content is required")

    config = CompileConfig(
        duration=int(request.get("duration", 60)),
        aspect_ratio=request.get("aspect_ratio", "16:9"),
        resolution=request.get("resolution", "1920x1080"),
    )
    models = request.get("output_models", DEFAULT_MODELS)

    project_id = f"ic-{slugify(request['title'])}"
    timestamp = now_iso()

    research = build_research(request, poem, knowledge)
    poem_lines = parse_poem_lines(poem["content"])
    shots = build_storyboard(poem_lines, config.duration, research, poem)
    ipr_nodes = [to_ipr_node(project_id, s) for s in shots]

    style_dynasty = research.get("resolved_dynasty", "宋")
    global_style = f"{style_dynasty} dynasty ink documentary"
    prompt_pack = {
        model: [compile_prompt(model, node, global_style, project_id, request, profiles) for node in ipr_nodes]
        for model in models
    }

    project = {
        "metadata": {
            "id": project_id,
            "version": "1.0.0",
            "created_at": timestamp,
            "updated_at": timestamp,
            "language": "zh-CN",
            "status": "qa",
        },
        "request": {
            "title": request["title"],
            "author": request.get("author", "") or poem.get("author", ""),
            "dynasty": request.get("dynasty", poem.get("dynasty", "")),
            "style": request.get("style", "Auto"),
            "duration": config.duration,
            "resolution": config.resolution,
            "aspect_ratio": config.aspect_ratio,
            "output_models": models,
            "target_platform": request.get("target_platform", "web"),
        },
        "poem": poem,
        "research": research,
        "storyboard": {
            "total_duration": sum(s["duration"] for s in shots),
            "total_shots": len(shots),
            "shots": shots,
            "confidence": round(clamp(float(research.get("confidence", {}).get("score", 0.8)), 0.0, 1.0), 3),
        },
        "visual": {
            "style_profile": global_style,
            "global_palette": research.get("dynasty_profile", {}).get(
                "color_preferences", ["ink black", "jade green", "rice white", "warm earth"]
            ),
            "continuity": {
                "character_ids": ["char_main"],
                "environment_ids": ["env_primary"],
                "lighting_ids": ["light_primary"],
            },
        },
        "audio": {
            "global_audio_style": "quiet, natural, minimal",
            "narration": {"style": "Poetic", "frequency": "low"},
            "music": {
                "instruments": research.get("dynasty_profile", {}).get("music", ["guqin", "xiao"]),
                "silence_ratio": 0.35,
            },
        },
        "prompt": prompt_pack,
        "qa": {},
        "events": [],
    }

    qa_report = run_qa(project, research)
    project["qa"] = {
        "schema_valid": True,
        "continuity_valid": qa_report["checks"]["continuity"]["score"] >= 75,
        "historical_risk_reported": True,
        "score": qa_report["overall_score"],
        "pass": qa_report["pass"],
        "warnings": qa_report["warnings"],
    }

    project["events"] = [
        {
            "event_id": "evt_000001",
            "sequence": 1,
            "timestamp": timestamp,
            "agent": "ExecutiveProducer",
            "event_type": "ProjectCreated",
            "payload": {"title": request["title"]},
        },
        {
            "event_id": "evt_000002",
            "sequence": 2,
            "timestamp": timestamp,
            "agent": "Research",
            "event_type": "ResearchCompleted",
            "payload": {
                "resolved_dynasty": research.get("resolved_dynasty"),
                "confidence": research.get("confidence", {}).get("score"),
            },
        },
        {
            "event_id": "evt_000003",
            "sequence": 3,
            "timestamp": timestamp,
            "agent": "Storyboard",
            "event_type": "StoryboardCompleted",
            "payload": {"shot_count": len(shots)},
        },
        {
            "event_id": "evt_000004",
            "sequence": 4,
            "timestamp": timestamp,
            "agent": "PromptCompiler",
            "event_type": "PromptCompiled",
            "payload": {"targets": models},
        },
        {
            "event_id": "evt_000005",
            "sequence": 5,
            "timestamp": timestamp,
            "agent": "QA",
            "event_type": "QACompleted",
            "payload": {"overall_score": qa_report["overall_score"], "pass": qa_report["pass"]},
        },
    ]

    project["metadata"]["status"] = "published" if qa_report["pass"] else "qa"
    return project


def write_outputs(project: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "project.json").write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "research.json").write_text(json.dumps(project["research"], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "storyboard.json").write_text(
        json.dumps(project["storyboard"], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    qa_report = run_qa(project, project.get("research", {}))
    (out_dir / "qa_report.json").write_text(json.dumps(qa_report, ensure_ascii=False, indent=2), encoding="utf-8")

    shots = project["storyboard"]["shots"]
    with (out_dir / "storyboard.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["shot_id", "scene_id", "beat_id", "duration", "description", "shot_type", "lens", "motion"],
        )
        writer.writeheader()
        for shot in shots:
            writer.writerow(
                {
                    "shot_id": shot["shot_id"],
                    "scene_id": shot["scene_id"],
                    "beat_id": shot["beat_id"],
                    "duration": shot["duration"],
                    "description": shot["description"],
                    "shot_type": shot["camera"]["shot_type"],
                    "lens": shot["camera"]["lens"],
                    "motion": shot["camera"]["motion"],
                }
            )

    for model, prompts in project["prompt"].items():
        with (prompt_dir / f"{model}.jsonl").open("w", encoding="utf-8") as f:
            for item in prompts:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    manifest = {
        "project_id": project["metadata"]["id"],
        "generated_at": now_iso(),
        "files": [
            "project.json",
            "research.json",
            "storyboard.json",
            "storyboard.csv",
            "qa_report.json",
            "prompts/",
        ],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile poem request into InkCinema project package")
    parser.add_argument("--input", required=True, help="Path to input JSON")
    parser.add_argument("--output", required=True, help="Output folder")
    parser.add_argument("--knowledge", default=str(DEFAULT_KNOWLEDGE_PATH), help="Path to dynasty knowledge base JSON")
    parser.add_argument("--profiles", default=str(DEFAULT_PROFILE_PATH), help="Path to model profile templates JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    knowledge = load_json(Path(args.knowledge))
    profiles = load_json(Path(args.profiles))

    data = json.loads(input_path.read_text(encoding="utf-8"))
    project = build_project(data, knowledge, profiles)
    write_outputs(project, output_path)

    print(
        json.dumps(
            {
                "ok": True,
                "project_id": project["metadata"]["id"],
                "output": str(output_path),
                "qa_score": project["qa"]["score"],
                "qa_pass": project["qa"]["pass"],
                "resolved_dynasty": project["research"].get("resolved_dynasty", "unknown"),
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
