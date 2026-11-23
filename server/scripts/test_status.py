import tempfile
import unittest
from pathlib import Path

import status


def doc(path, state, issue=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 제목", "", f"- 상태: {state}"]
    if issue:
        lines.append(f"- 이슈: {issue}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class PerSlice(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        status.ROOT, status.DOCS = root, root / "docs"
        # 첫 슬라이스(#3)는 끝났다: spec 승인, plan 닫음
        doc(status.DOCS / "policy/UPL.md", "승인", "#3")
        doc(status.DOCS / "spec/01-upload.md", "승인", "#3")
        doc(status.DOCS / "plan/01-upload.md", "닫음", "#3")

    def tearDown(self):
        self.tmp.cleanup()

    def stage(self, issue):
        return status.compute(status.collect(), issue)[0]

    def test_브랜치에서_이슈_번호를_읽는다(self):
        self.assertEqual(status.issue_of_branch("feat/20-new-feature"), 20)
        self.assertIsNone(status.issue_of_branch("develop"))
        self.assertIsNone(status.issue_of_branch("docs/branch-kinds"))

    def test_새_이슈는_정책_읽기부터다(self):
        self.assertTrue(self.stage(20).startswith("1."))

    def test_끝난_이슈는_종료_뒤다(self):
        self.assertTrue(self.stage(3).startswith("8."))

    def test_정책_기록만_있으면_문서다(self):
        doc(status.DOCS / "policy/UPL2.md", "승인", "#20")
        self.assertTrue(self.stage(20).startswith("2."))

    def test_spec이_승인되고_plan이_없으면_계획이다(self):
        doc(status.DOCS / "policy/UPL2.md", "승인", "#20")
        doc(status.DOCS / "spec/02-thumb.md", "승인", "#20")
        self.assertTrue(self.stage(20).startswith("3."))

    def test_이슈를_모르면_모든_문서를_본다(self):
        self.assertTrue(self.stage(None).startswith("3."))


if __name__ == "__main__":
    unittest.main()
