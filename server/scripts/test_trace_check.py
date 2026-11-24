import tempfile
import unittest
from pathlib import Path

import trace_check

SPEC = """# spec 01

- 상태: 승인

| ID | 수준 | 기준 | 근거 |
|---|---|---|---|
| AC-1.1 | MUST | a | 기술 결정 |
| AC-1.2 | MUST | b | 기술 결정 |
| AC-1.3 | MUST | c (폐기) | 기술 결정 |
"""

DOMAIN = """# domain 01

- 상태: 승인

| ID | 수준 | 규칙 |
|---|---|---|
| R-1.1 | MUST | r |
"""


def plan(rows):
    head = "# 슬라이스 01\n\n- 상태: 제안\n\n| 작업 | 다루는 ID | 검증할 내용 | 상태 |\n|---|---|---|---|\n"
    return head + "".join(f"| {name} | {ids} | 확인 | 대기 |\n" for name, ids in rows)


class PlanCoverage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        trace_check.ROOT = Path(self.tmp.name)
        self.write("spec/01-a.md", SPEC)
        self.write("domain/01-a.md", DOMAIN)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = trace_check.ROOT / "docs" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_plan이_없으면_문제가_없다(self):
        self.assertEqual(trace_check.plan_problems(), [])

    def test_모든_ID를_덮으면_문제가_없다(self):
        self.write("plan/01-a.md", plan([("1. a", "AC-1.1, R-1.1"), ("2. b", "AC-1.2")]))
        self.assertEqual(trace_check.plan_problems(), [])

    def test_빠진_ID를_알린다(self):
        self.write("plan/01-a.md", plan([("1. a", "AC-1.1, R-1.1")]))
        self.assertEqual(len(trace_check.plan_problems()), 1)
        self.assertIn("AC-1.2", trace_check.plan_problems()[0])

    def test_폐기된_ID는_덮지_않아도_되고_가리켜도_된다(self):
        self.write("plan/01-a.md", plan([("1. a", "AC-1.1, AC-1.2, AC-1.3, R-1.1")]))
        self.assertEqual(trace_check.plan_problems(), [])

    def test_ID가_없는_작업과_없는_ID를_알린다(self):
        self.write("plan/01-a.md", plan([("1. a", "AC-1.1, AC-1.2, R-1.1"), ("2. b", "없음"), ("3. c", "AC-1.9")]))
        found = trace_check.plan_problems()
        self.assertTrue(any("다루는 ID가 없는 작업: 2. b" in p for p in found))
        self.assertTrue(any("AC-1.9" in p for p in found))

    def test_plan이_다루지_않는_spec은_보지_않는다(self):
        self.write("spec/02-b.md", SPEC.replace("AC-1.", "AC-2."))
        self.write("plan/01-a.md", plan([("1. a", "AC-1.1, AC-1.2, R-1.1")]))
        self.assertEqual(trace_check.plan_problems(), [])


if __name__ == "__main__":
    unittest.main()
