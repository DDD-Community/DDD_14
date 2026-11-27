import tempfile
import unittest
from pathlib import Path

import docs_lint


def review(rows):
    head = ("# 리뷰 01. a\n\n## 문서 r1 (doc-reviewer, docs)\n\n### 처리 (2026-11-24 일지 스텝 1)\n\n"
            "| 지적 | 처리 | 이유 | 결정한 사람 |\n|---|---|---|---|\n")
    return head + "".join(f"| {a} | {b} | {c} | {d} |\n" for a, b, c, d in rows)


class Lint(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        docs_lint.ROOT = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text="# 제목\n\n- 상태: 제안\n"):
        p = docs_lint.ROOT / "docs" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def l5(self, rel, text="# 제목\n\n- 상태: 제안\n"):
        return [p for p in docs_lint.lint_file(self.write(rel, text)) if "L5" in p]

    def test_지도에_있는_문서는_통과한다(self):
        for rel in ("README.md", "policy/UPL.md", "spec/01-upload.md", "domain/01-자료.md",
                    "adr/0007-오류-응답.md", "plan/01-upload.md", "review/.gitkeep"):
            self.assertEqual(self.l5(rel), [], rel)
        self.assertEqual(self.l5("journal/2026-11-24-seobang.md", "# 일지\n"), [])

    def test_지도에_없는_문서를_알린다(self):
        for rel in ("api.md", "api/upload.md", "spec/upload.md", "adr/7-x.md", "status/now.md",
                    "journal/today.md", "spec/01-a/b.md"):
            self.assertEqual(len(self.l5(rel)), 1, rel)

    def l6(self, rows):
        return [p for p in docs_lint.lint_file(self.write("review/01-a.md", review(rows))) if "L6" in p]

    def test_처리의_값이_맞으면_통과한다(self):
        self.assertEqual(self.l6([("DOC-1", "받아들임", "고쳤다", "AI"),
                                  ("DOC-2", "받아들이지 않음", "범위 밖이다", "사용자"),
                                  ("DOC-3", "보류", "PM의 답", "사용자")]), [])

    def test_처리의_값이_아니면_알린다(self):
        self.assertEqual(len(self.l6([("DOC-1", "반영", "고쳤다", "AI")])), 1)

    def test_받아들이지_않음은_사용자가_이유와_함께_정한다(self):
        self.assertEqual(len(self.l6([("DOC-1", "받아들이지 않음", "", "AI")])), 2)


if __name__ == "__main__":
    unittest.main()
