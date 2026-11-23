#!/usr/bin/env python3
"""policy_check.py의 정책 파싱, 번호 범위, 이슈 coverage를 확인한다. 사용: python3 -m unittest scripts/test_policy_check.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import policy_check as pc

WIKI = """# UPL
## 정책
### 확정
- **UPL-01** 글자로 된 PDF를 받는다.
- **UPL-02** 스캔 PDF는 받지 않는다.
- **UPL-03** 20MB까지다.
- **UPL-04** 하루 한도는 두지 않는다.
### 검토 중
- **UPL-05** 검사 후 추출한다.
### 미결정
- **UPL-08** 재시도 방식
"""


class ParseTest(unittest.TestCase):
    def test_status_by_heading(self):
        p = pc.parse_policies(WIKI)
        self.assertEqual(p["UPL-01"][0], "확정")
        self.assertEqual(p["UPL-05"][0], "검토 중")
        self.assertEqual(p["UPL-08"][0], "미결정")

    def test_abolished(self):
        p = pc.parse_policies(WIKI.replace("20MB까지다.", "폐기. 20MB까지다."))
        self.assertEqual(p["UPL-03"][0], "폐기")


class ExpandTest(unittest.TestCase):
    def test_range(self):
        self.assertEqual(pc.expand_ids("위키 UPL-01~04"), {"UPL-01", "UPL-02", "UPL-03", "UPL-04"})

    def test_list_and_range(self):
        self.assertEqual(pc.expand_ids("UPL-01, UPL-03~04"), {"UPL-01", "UPL-03", "UPL-04"})

    def test_prefix_on_both_ends(self):
        self.assertEqual(pc.expand_ids("UPL-01~UPL-02"), {"UPL-01", "UPL-02"})

    def test_reversed_range_is_single(self):
        self.assertEqual(pc.expand_ids("UPL-04~02"), {"UPL-04"})

    def test_ignores_ac_ids(self):
        self.assertEqual(pc.expand_ids("AC-1.2 와 R-1.1"), set())


class CoverageTest(unittest.TestCase):
    def issues(self, *bodies):
        return [{"number": n, "title": "t", "state": "OPEN", "body": b} for n, b in enumerate(bodies, 1)]

    def test_missing_and_premature_and_ghost(self):
        pol = pc.parse_policies(WIKI)
        iss = self.issues("기획: 위키 UPL-01~02\n의존: ", "기획: UPL-05, UPL-99")
        missing, premature, ghosts = pc.coverage(pol, iss)
        self.assertEqual(missing, ["UPL-03", "UPL-04"])
        self.assertEqual(premature, [("UPL-05", "검토 중", [2])])
        self.assertEqual(ghosts, [("UPL-99", [2])])

    def test_all_covered(self):
        pol = pc.parse_policies(WIKI)
        missing, _, _ = pc.coverage(pol, self.issues("기획: UPL-01~04"))
        self.assertEqual(missing, [])

    def test_issue_without_policy_line_is_ignored(self):
        pol = pc.parse_policies(WIKI)
        missing, _, _ = pc.coverage(pol, self.issues("그냥 본문 UPL-01~04"))
        self.assertEqual(len(missing), 4)


class ZeroPoliciesTest(unittest.TestCase):
    def test_zero_policies_fails_loudly(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            wiki, issues = Path(d) / "w.md", Path(d) / "i.json"
            wiki.write_text("# UPL\n\n정책 형식이 바뀌었다.\n", encoding="utf-8")
            issues.write_text(json.dumps([]), encoding="utf-8")
            code = pc.run_coverage(["--coverage", "--wiki-file", str(wiki), "--json", str(issues)])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
