import tempfile
import unittest
from pathlib import Path

import ref_check


class Refs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        ref_check.ROOT = Path(self.tmp.name)
        self.write("scripts/check.sh", "")
        self.write(".claude/skills/work/references/plan.md", "")
        self.write(".claude/skills/work/references/shared/커밋과-PR.md", "")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = ref_check.ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_있는_파일과_자리표시는_통과한다(self):
        self.write(".claude/skills/work/SKILL.md",
                   "`references/plan.md` `shared/커밋과-PR.md` `./scripts/check.sh` `check.sh` "
                   "`references/<단계>.md` `docs/plan/NN-<슬라이스>.md`\n")
        self.write(".claude/agents/a.md", "`work/references/plan.md` `.claude/skills/work/references/plan.md`\n")
        self.assertEqual(ref_check.problems(), [])

    def test_없는_파일을_알린다(self):
        self.write("AGENTS.md", "`scripts/view.py`와 `view.py`\n")
        self.write(".claude/commands/issues.md", "`references/policy.md`\n")
        self.assertEqual(len(ref_check.problems()), 3)

    def test_ADR은_보지_않는다(self):
        self.write("docs/adr/0001-하네스.md", "버린 대안: `view.py`\n")
        self.assertEqual(ref_check.problems(), [])


if __name__ == "__main__":
    unittest.main()
