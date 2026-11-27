#!/usr/bin/env python3
"""지시문이 가리키는 파일이 있는지 확인한다.

- 지시문은 `.claude/` 아래의 md, `AGENTS.md`, `docs/README.md`다. ADR과 일지는 지운 파일을 기록으로 말하므로 보지 않는다.
- 백틱 안의 `.md`, `.py`, `.sh`, `.json`으로 끝나는 경로를 모은다. 자리표시(`<…>`, `NN`, `YYYY`, `*`, `{…}`, `$`)와
  작업 중에만 생기는 `_workspace/`의 파일은 건너뛴다.
- 경로는 프로젝트 폴더, `.claude/`, `.claude/skills/`, 그 지시문의 스킬 폴더와 그 `references/`에서 찾는다.
  폴더가 없는 이름(`check.sh`)은 프로젝트 안의 같은 이름의 파일을 찾는다.
- 찾지 못하면 실패한다.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = re.compile(r"`([^`\s]+)`")
FILE = re.compile(r"\.(md|py|sh|json)$")
PLACEHOLDER = re.compile(r"[<>*{}$]|NN|YYYY")
SKIP_DIRS = {".git", "_workspace", "build", ".gradle", "node_modules", "__pycache__"}


def instruction_files():
    files = sorted((ROOT / ".claude").rglob("*.md"))
    return files + [f for f in (ROOT / "AGENTS.md", ROOT / "docs" / "README.md") if f.exists()]


def project_names():
    names = set()
    for f in ROOT.rglob("*"):
        if f.is_file() and not SKIP_DIRS & set(f.relative_to(ROOT).parts):
            names.add(f.name)
    return names


def skill_dir(f: Path):
    parts = f.relative_to(ROOT).parts
    if len(parts) >= 3 and parts[:2] == (".claude", "skills"):
        return ROOT.joinpath(*parts[:3])
    return None


def resolves(token: str, source: Path, names) -> bool:
    t = token.removeprefix("./").removeprefix("server/").removeprefix("@")
    if "/" not in t:
        return t in names
    bases = [ROOT, ROOT / ".claude", ROOT / ".claude" / "skills", source.parent]
    sd = skill_dir(source)
    if sd:
        bases += [sd, sd / "references"]
    return any((b / t).exists() for b in bases)


def problems():
    names = project_names()
    out = []
    for f in instruction_files():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for t in TOKEN.findall(line):
                if not FILE.search(t) or PLACEHOLDER.search(t) or t.startswith("_workspace/"):
                    continue
                if not resolves(t, f, names):
                    out.append(f"없는 파일을 가리킨다: {t} ({f.relative_to(ROOT)}:{n})")
    return out


def main():
    found = problems()
    for p in found:
        print(p)
    if found:
        print(f"ref: 문제 {len(found)}건", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
