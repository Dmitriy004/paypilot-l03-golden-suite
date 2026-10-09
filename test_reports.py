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
        self.assertEqual([30, 14, 30], [r["passed"] for r in self.reports])
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
        self.assertIn("omit exact numeric amounts", custom["prompt"]["text"])

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

        self.assertEqual((254935, 95948, 185),
                         (total_input, total_output, total_calls))
        uncached_cost = total_input * 0.25 / 1_000_000
        uncached_cost += total_output * 2.00 / 1_000_000
        self.assertEqual(0.2556, round(uncached_cost, 4))


if __name__ == "__main__":
    unittest.main()
