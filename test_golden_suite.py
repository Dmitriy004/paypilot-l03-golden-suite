import json
import re
import unittest
from pathlib import Path


LEVELS = {
    "equals": 1,
    "exact": 1,
    "tool_result_flag": 1,
    "tool_result_numeric": 2,
    "tool_grounded_numeric": 2,
    "numeric": 2,
    "contains": 3,
    "regex": 3,
    "not_contains": 4,
    "not_regex": 4,
    "judge": 7,
}


class GoldenSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("golden.jsonl")
        cls.cases = {
            case["id"]: case
            for case in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
        }

    def test_swift_fee_regex_accepts_currency_before_amount(self):
        case = self.cases["CMP-001-SWIFT"]
        pattern = case["additional_metadata"]["pattern"]

        self.assertRegex("Verta flat fee: EUR 15.00; percentage fee: 0.3%.", pattern)
        self.assertIsNone(re.search(pattern, "The SWIFT fee is 1.5%."))
        self.assertIn("Verta tariff schedule", case["input"])
        self.assertIn("exact", case["input"].lower())

    def test_current_lms_dataset_checklist(self):
        cases = list(self.cases.values())
        own = [case for case in cases
               if case["additional_metadata"].get("added_in") == "hw2"]
        own_human = [case for case in own
                     if case["additional_metadata"]["oracle"] == "human"]

        self.assertGreaterEqual(len(cases), 30)
        self.assertLessEqual(len(cases), 40)
        self.assertGreaterEqual(len(own), 15)
        self.assertLessEqual(len(own_human), 5)
        self.assertGreaterEqual(len(own_human), 5)
        self.assertEqual({"complaint", "engine", "edge"}, {
            case["additional_metadata"]["source"] for case in cases
        })
        self.assertEqual({1, 2, 3, 4, 7}, {
            LEVELS[case["additional_metadata"]["assertion"]]
            for case in cases
        })

        for case in cases:
            meta = case["additional_metadata"]
            self.assertTrue(case["expected_output"], case["id"])
            self.assertTrue(meta.get("oracle"), case["id"])
            self.assertTrue(meta.get("severity"), case["id"])
            self.assertTrue(meta.get("why_this_level"), case["id"])

        for case in own_human:
            meta = case["additional_metadata"]
            self.assertEqual(5, meta["runs"], case["id"])
            self.assertEqual("release", meta["gate"], case["id"])

    def test_required_complaints_have_traceable_own_cases(self):
        own = [case for case in self.cases.values()
               if case["additional_metadata"].get("added_in") == "hw2"]
        complaint_ids = {
            case["additional_metadata"].get("complaint_id") for case in own
        }
        self.assertTrue({"C-03", "C-09", "C-11", "C-12"} <= complaint_ids)

        for case in own:
            meta = case["additional_metadata"]
            if meta["oracle"] == "engine":
                self.assertTrue(meta.get("engine_call"), case["id"])


if __name__ == "__main__":
    unittest.main()
