#!/usr/bin/env python3
"""scripts/view.py의 시험. 실행: python3 scripts/test_view.py"""
import html
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import view  # noqa: E402

ROOT = view.ROOT


class RenderTest(unittest.TestCase):
    def test_표를_표로_그리고_백틱_안의_세로줄은_나누지_않는다(self):
        out = view.render_markdown("| 가 | 나 |\n|---|---|\n| `a|b` | c |\n")
        self.assertIn("<table>", out)
        self.assertIn("<code>a|b</code>", out)
        self.assertEqual(out.count("<td>"), 2)

    def test_굵은_키워드와_코드를_그린다(self):
        out = view.render_markdown("서버는 **반드시** `x`를 쓴다.")
        self.assertIn("<strong>반드시</strong>", out)
        self.assertIn("<code>x</code>", out)

    def test_html은_글자로_나온다(self):
        out = view.render_markdown("<script>alert(1)</script> 와 `<b>`")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_목록과_번호와_제목(self):
        out = view.render_markdown("# 제목\n\n- 가\n- 나\n\n1. 하나\n2. 둘\n")
        self.assertIn("<h1>제목</h1>", out)
        self.assertEqual(out.count("<li>"), 4)
        self.assertIn("<ol>", out)

    def test_코드_블록은_그대로(self):
        out = view.render_markdown("```\n<a> | b\n```\n")
        self.assertIn("<pre><code>&lt;a&gt; | b</code></pre>", out)


class PageTest(unittest.TestCase):
    def setUp(self):
        self.dir = ROOT / "_workspace" / "view-test"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.f = self.dir / "a.md"
        self.rel = str(self.f.relative_to(ROOT))

    def tearDown(self):
        for p in self.dir.glob("*"):
            p.unlink()
        self.dir.rmdir()

    def test_소스_탭은_파일의_글자_그대로이고_해시가_찍힌다(self):
        text = "- 상태: 제안\n\n| a | b |\n|---|---|\n| <x> | & |\n"
        self.f.write_text(text, encoding="utf-8")
        page, _ = view.build_page([self.rel], "HEAD")
        self.assertIn(html.escape(text), page)
        self.assertIn(view.sha256(text.encode()), page)

    def test_같은_내용은_같은_이름_다른_내용은_다른_이름(self):
        self.f.write_text("가\n", encoding="utf-8")
        _, k1 = view.build_page([self.rel], "HEAD")
        _, k2 = view.build_page([self.rel], "HEAD")
        self.f.write_text("나\n", encoding="utf-8")
        _, k3 = view.build_page([self.rel], "HEAD")
        self.assertEqual(k1, k2)
        self.assertNotEqual(k1, k3)

    def test_새_파일은_변경_탭에_모두_추가로_나온다(self):
        self.f.write_text("새 줄\n", encoding="utf-8")
        page, _ = view.build_page([self.rel], "HEAD")
        self.assertIn('class="ln add">+새 줄', page)

    def test_외부_주소를_부르지_않는다(self):
        self.f.write_text("글\n", encoding="utf-8")
        page, _ = view.build_page([self.rel], "HEAD")
        for bad in ("<script", "src=\"http", "<link", "@import"):
            self.assertNotIn(bad, page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
