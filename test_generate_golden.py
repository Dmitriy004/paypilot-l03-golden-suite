import unittest

import generate_golden


class GoldenGeneratorTests(unittest.TestCase):
    def test_fx_boundaries_use_engine_derived_values(self):
        cases = {case["id"]: case for case in generate_golden.fx_cases()}
        expected = {
            "FX-006": 1086.96,
            "FX-007": 1078.25,
            "FX-008": 217.39,
            "FX-009": 216.51,
        }

        for case_id, expected_number in expected.items():
            with self.subTest(case_id=case_id):
                case = cases[case_id]
                meta = case["additional_metadata"]
                self.assertEqual(expected_number, meta["expected_number"])
                self.assertEqual("edge", meta["source"])
                self.assertEqual("hw2", meta["added_in"])
                self.assertTrue(meta["engine_call"])

    def test_fx_boundaries_include_spread_companions(self):
        cases = {case["id"]: case for case in generate_golden.fx_cases()}

        self.assertEqual("not_contains", cases["FX-006-S"]["additional_metadata"]["assertion"])
        self.assertEqual("contains", cases["FX-007-S"]["additional_metadata"]["assertion"])
        self.assertEqual("not_contains", cases["FX-008-S"]["additional_metadata"]["assertion"])
        self.assertEqual("contains", cases["FX-009-S"]["additional_metadata"]["assertion"])

    def test_complaint_disputes_are_computed_from_policy_and_engine(self):
        cases = {case["id"]: case for case in generate_golden.complaint_dispute_cases()}

        self.assertEqual("120 days", cases["CMP-011-W"]["expected_output"])
        self.assertEqual("60 days", cases["CMP-012-W"]["expected_output"])
        self.assertTrue(cases["CMP-011-E"]["additional_metadata"]["expected_flag"])
        self.assertTrue(cases["CMP-012-E"]["additional_metadata"]["expected_flag"])
        for case in cases.values():
            meta = case["additional_metadata"]
            self.assertEqual("complaint", meta["source"])
            self.assertEqual("hw2", meta["added_in"])
            self.assertTrue(meta["engine_call"])

    def test_generator_adds_fourteen_hw2_engine_cases(self):
        cases = generate_golden.all_cases()
        own = [case for case in cases
               if case["additional_metadata"].get("added_in") == "hw2"]

        self.assertEqual(14, len(own))
        self.assertEqual(35, len(cases))
        self.assertEqual(len(cases), len({case["id"] for case in cases}))

    def test_context_recovered_complaints_are_engine_grounded(self):
        cases = {case["id"]: case for case in generate_golden.all_cases()}

        expected = {
            "C03-TECHMART": ("C-03", False),
            "C09-MONTHLY-AFTER": ("C-09", 864666.0),
        }
        for case_id, (complaint_id, value) in expected.items():
            with self.subTest(case_id=case_id):
                case = cases[case_id]
                meta = case["additional_metadata"]
                self.assertEqual("complaint", meta["source"])
                self.assertEqual("hw2", meta["added_in"])
                self.assertEqual(complaint_id, meta["complaint_id"])
                self.assertTrue(meta["engine_call"])
                if isinstance(value, bool):
                    self.assertEqual(value, meta["expected_flag"])
                else:
                    self.assertEqual(value, meta["expected_number"])


if __name__ == "__main__":
    unittest.main()
