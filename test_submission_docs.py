import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class SubmissionDocumentTests(unittest.TestCase):
    def test_readme_contains_required_lms_sections_and_evidence(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        for heading in ("## Скарги", "## Генератор", "## Прогони"):
            self.assertIn(heading, text)
        for complaint in ("C-03", "C-09", "C-11", "C-12"):
            self.assertIn(complaint, text)
        self.assertIn("b4c3b413b6e9", text)
        self.assertIn("gpt-5-mini-2025-08-07", text)
        self.assertIn("30/30", text)
        self.assertIn("14/30", text)

    def test_residual_risk_follows_template_and_reconciles_cost(self):
        text = (ROOT / "residual-risk.md").read_text(encoding="utf-8")

        for heading in (
            "## 1. Матриця покриття",
            "## 2. Чого набір не ловить",
            "## 3. Розмір набору",
        ):
            self.assertIn(heading, text)
        self.assertIn("Скарги поза набором:", text)
        self.assertIn("Мандат: **Ship it**", text)
        self.assertIn("30 × 1 = 30", text)
        self.assertIn("64", text)
        self.assertIn("119,426", text)
        self.assertIn("$0.0837", text)
        self.assertIn("0 кейсах із 30", text)
        self.assertIn("Zero regulatory risk", text)


if __name__ == "__main__":
    unittest.main()
