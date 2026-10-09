import hashlib
import json
import unittest
from pathlib import Path


REPORTS = Path(__file__).with_name("reports")
FILES = (
    "01-clean-baseline.json",
    "02-lesson-03.json",
    "03-clean-custom-prompt.json",
)


class ReportArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports = [
            json.loads((REPORTS / name).read_text(encoding="utf-8"))
            for name in FILES
        ]

    def test_required_runs_share_the_same_set(self):
        self.assertEqual([30, 14, 11], [r["passed"] for r in self.reports])
        expected_hash = hashlib.sha256(
            Path(__file__).with_name("golden.jsonl").read_bytes()
        ).hexdigest()[:12]
        self.assertEqual({expected_hash}, {r["set_hash"] for r in self.reports})
        self.assertEqual("b4c3b413b6e9", expected_hash)

    def test_prompt_snapshots_are_self_verifying(self):
        for report in self.reports:
            prompt = report["prompt"]
            actual = hashlib.sha256(prompt["text"].encode("utf-8")).hexdigest()
            self.assertEqual(actual, prompt["sha256"])

        baseline, lesson, custom = self.reports
        self.assertEqual(baseline["prompt"]["sha256"], lesson["prompt"]["sha256"])
        self.assertNotEqual(baseline["prompt"]["sha256"], custom["prompt"]["sha256"])
        self.assertEqual(
            "13d3b5072f2689da59d0c6714fb836a8f5ad139225d834c4ba4190fac5732be5",
            custom["prompt"]["sha256"],
        )
        self.assertIn("increase every numeric value", custom["prompt"]["text"])

    def test_custom_prompt_run_matches_preregistered_experiment(self):
        custom = self.reports[2]
        failed_ids = [
            case["id"] for case in custom["cases"] if not case["verdict"]["passed"]
        ]

        self.assertEqual(
            [
                "FX-004",
                "CMP-003",
                "CMP-004",
                "FX-002",
                "FX-003",
                "FX-003-S",
                "FX-005",
                "DIS-001",
                "FX-006",
                "FX-007",
                "FX-007-S",
                "FX-008",
                "FX-009",
                "FX-009-S",
                "CMP-011-W",
                "CMP-012-W",
                "CMP-001-SWIFT",
                "CMP-013-TIER3",
                "C03-TECHMART",
            ],
            failed_ids,
        )
        self.assertEqual({"generation": 6, "action": 5}, {
            layer: values["passed"] for layer, values in custom["by_layer"].items()
        })

    def test_usage_aggregates_match_cases_and_cost(self):
        total_input = total_output = total_calls = 0
        for report in self.reports:
            usage = report["usage"]
            self.assertEqual(
                usage["input_tokens"],
                sum(case["usage"]["input_tokens"] for case in report["cases"]),
            )
            self.assertEqual(
                usage["output_tokens"],
                sum(case["usage"]["output_tokens"] for case in report["cases"]),
            )
            self.assertEqual(
                usage["model_calls"],
                sum(case["usage"]["model_calls"] for case in report["cases"]),
            )
            self.assertEqual(["gpt-5-mini-2025-08-07"], usage["agent_models"])
            total_input += usage["input_tokens"]
            total_output += usage["output_tokens"]
            total_calls += usage["model_calls"]

        self.assertEqual((257800, 147080, 185),
                         (total_input, total_output, total_calls))
        uncached_cost = total_input * 0.25 / 1_000_000
        uncached_cost += total_output * 2.00 / 1_000_000
        self.assertEqual(0.3586, round(uncached_cost, 4))


if __name__ == "__main__":
    unittest.main()
