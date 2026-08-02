import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "poem_to_video.py"
INPUT_DEFAULT = ROOT / "examples" / "poem_request.json"
INPUT_4X3 = ROOT / "tests" / "fixtures" / "poem_request_aspect_4_3.json"
BASELINE = ROOT / "tests" / "baselines" / "adapter_baseline_poem_request.json"


def run_pipeline(input_path: Path, output_dir: Path) -> dict:
    command = [
        sys.executable,
        str(SCRIPT),
        "--input",
        str(input_path),
        "--output",
        str(output_dir),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout.strip())


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class AdapterRegressionTests(unittest.TestCase):
    def test_deterministic_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory(prefix="inkcinema_reg_a_") as dir_a:
            with tempfile.TemporaryDirectory(prefix="inkcinema_reg_b_") as dir_b:
                out_a = Path(dir_a)
                out_b = Path(dir_b)

                run_pipeline(INPUT_DEFAULT, out_a)
                run_pipeline(INPUT_DEFAULT, out_b)

                for model in ["kling", "cogvideo", "wan", "veo"]:
                    prompts_a = read_jsonl(out_a / "prompts" / f"{model}.jsonl")
                    prompts_b = read_jsonl(out_b / "prompts" / f"{model}.jsonl")
                    self.assertEqual(prompts_a, prompts_b, f"{model} prompts should be deterministic")

    def test_model_adapter_baseline(self) -> None:
        baseline = read_json(BASELINE)

        with tempfile.TemporaryDirectory(prefix="inkcinema_reg_base_") as out_dir:
            out = Path(out_dir)
            run_pipeline(INPUT_DEFAULT, out)

            project = read_json(out / "project.json")
            qa_report = read_json(out / "qa_report.json")

            self.assertEqual(project["research"]["resolved_dynasty"], "唐")
            self.assertIn("overall_score", qa_report)
            self.assertGreaterEqual(qa_report["overall_score"], 75)

            for model in baseline["expected_models"]:
                expected = baseline["first_shot"][model]
                prompts = read_jsonl(out / "prompts" / f"{model}.jsonl")
                self.assertGreaterEqual(len(prompts), 1)
                shot = prompts[0]
                params = shot["params"]

                self.assertEqual(params["aspect_ratio"], expected["aspect_ratio"])
                self.assertEqual(params["duration"], expected["duration"])
                self.assertEqual(params["fps"], expected["fps"])
                self.assertEqual(params["resolution"], expected["resolution"])
                self.assertEqual(params["seed"], expected["seed"])
                self.assertAlmostEqual(params["motion_strength"], expected["motion_strength"], places=6)

                negative_empty = shot.get("negative_prompt", "") == ""
                self.assertEqual(negative_empty, expected["negative_prompt_empty"])

    def test_aspect_ratio_fallback_regression(self) -> None:
        with tempfile.TemporaryDirectory(prefix="inkcinema_reg_4x3_") as out_dir:
            out = Path(out_dir)
            run_pipeline(INPUT_4X3, out)

            kling = read_jsonl(out / "prompts" / "kling.jsonl")[0]
            wan = read_jsonl(out / "prompts" / "wan.jsonl")[0]
            veo = read_jsonl(out / "prompts" / "veo.jsonl")[0]

            self.assertEqual(kling["params"]["aspect_ratio"], "16:9")
            self.assertEqual(wan["params"]["aspect_ratio"], "16:9")
            self.assertEqual(veo["params"]["aspect_ratio"], "4:3")

            self.assertTrue(any("不支持 4:3" in warning for warning in kling.get("warnings", [])))
            self.assertTrue(any("不支持 4:3" in warning for warning in wan.get("warnings", [])))
            self.assertEqual(veo.get("warnings", []), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
