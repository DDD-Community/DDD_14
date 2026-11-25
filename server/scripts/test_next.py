import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("next_script", Path(__file__).parent / "next.py")
next_script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(next_script)


class Kinds(unittest.TestCase):
    def test_규칙의_종류를_읽는다(self):
        self.assertEqual(next_script.kind_of("ci: 검사를 더한다"), "ci")

    def test_범위가_있는_제목의_종류를_읽는다(self):
        self.assertEqual(next_script.kind_of("feat(upload): 자료를 올린다"), "feat")

    def test_규칙에_없는_종류는_읽지_않는다(self):
        self.assertIsNone(next_script.kind_of("setting: 빌드를 고친다"))
        self.assertIsNone(next_script.kind_of("file: 파일을 옮긴다"))


if __name__ == "__main__":
    unittest.main()
