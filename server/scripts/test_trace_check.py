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


POLICY = """# 정책 기록 UPL

- 상태: 승인

| 번호 | 위키 상태 | 문장 | 이 슬라이스 |
|---|---|---|---|
| UPL-01 | 확정 | a | 예 |

## 기획 질문

| # | 질문 | 정책 | 상태 |
|---|---|---|---|
| 3 | 단위는 | UPL-01 | 열림 |
| 8 | 어느 이유를 | UPL-01 | 닫힘 (일지 스텝 9: 형식) |
"""


class Basis(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        trace_check.ROOT = Path(self.tmp.name)
        p = trace_check.ROOT / "docs" / "policy" / "UPL.md"
        p.parent.mkdir(parents=True)
        p.write_text(POLICY, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def basis(self, cell):
        p = trace_check.ROOT / "docs" / "spec" / "01-a.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("| ID | 수준 | 기준 | 근거 |\n|---|---|---|---|\n"
                     f"| AC-1.1 | MUST | a(질문 3) | {cell} |\n", encoding="utf-8")
        return trace_check.basis_problems()

    def test_정책_번호와_기술_결정과_닫힌_질문은_근거다(self):
        for cell in ("UPL-01", "기술 결정", "UPL-Q8"):
            self.assertEqual(self.basis(cell), [], cell)

    def test_열린_질문은_근거가_아니다(self):
        self.assertIn("닫히지 않은", self.basis("UPL-Q3")[0])

    def test_없는_질문을_알린다(self):
        self.assertIn("없는 기획 질문", self.basis("UPL-Q9")[0])

    def test_근거가_없으면_알린다(self):
        self.assertIn("근거가 없는 AC", self.basis("")[0])


if __name__ == "__main__":
    unittest.main()
