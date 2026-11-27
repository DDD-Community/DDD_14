#!/usr/bin/env python3
"""docs/README.md의 규칙 중 기계가 판정할 수 있는 것을 검사한다.

검사:
  L1 상태의 줄: 일지와 리뷰를 뺀 문서의 첫 항목은 `- 상태:`다.
  L2 수준과 키워드: 요구의 표에서 수준(MUST 등)과 문장의 굵은 키워드가 같다.
     요구의 목록(`- (번호) 문장 [지키는 것]`)에서는 한 줄에 굵은 키워드가 정확히 한 종류다.
  L3 키워드의 자리: adr, spec, domain에서 굵은 키워드는 요구의 표와 요구의 목록에만 있다.
  L4 쌓기만 하는 문서: 일지와 리뷰의 기존 줄을 지우지 않았다(git이 있을 때).
  L5 문서의 지도: docs/ 아래의 파일은 README의 "문서의 지도"에 있는 종류와 이름이다.
  L6 리뷰의 처리: 처리는 받아들임, 받아들이지 않음, 보류 중 하나다. 받아들이지 않음은 이유가 있고 사용자가 정한다.

사용: docs_lint.py <파일>...   또는   docs_lint.py --all
위반이 있으면 한 줄씩 출력하고 종료 코드 1을 돌려준다.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVEL_KEYWORDS = {
    "MUST": re.compile(r"\*\*반드시\*\*"),
    "MUST NOT": re.compile(r"\*\*절대\*\*"),
    "SHOULD": re.compile(r"\*\*권장한다\*\*"),
    "MAY": re.compile(r"\*\*[^*]*수 있다\*\*|수 있다\*\*"),
}
STATUS_DIRS = ("adr", "spec", "domain", "plan", "policy")
KEYWORD_DIRS = ("adr", "spec", "domain")
REQ_BULLET = re.compile(r"^- \(([^)]+)\) ")
ANY_KEYWORD = re.compile(r"\*\*(반드시|절대|권장한다)\*\*|수 있다\*\*")
DOC_MAP = [
    re.compile(r"README\.md"),
    re.compile(r"(policy|spec|domain|adr|plan|journal|review)/\.gitkeep"),
    re.compile(r"policy/[A-Z]{2,5}\.md"),
    re.compile(r"(spec|domain|plan|review)/\d{2}-[^/]+\.md"),
    re.compile(r"adr/\d{4}-[^/]+\.md"),
    re.compile(r"journal/\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.md"),
]
DISPOSITIONS = ("받아들임", "받아들이지 않음", "보류")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def doc_kind(path: Path):
    parts = path.resolve().relative_to(ROOT).parts if path.resolve().is_relative_to(ROOT) else ()
    if len(parts) >= 3 and parts[0] == "docs":
        return parts[1]
    if parts == ("docs", "README.md") or parts == ("AGENTS.md",):
        return "root"
    return None


def map_problem(path: Path):
    """docs/ 아래의 파일이 문서의 지도에 없으면 위반 한 줄을 돌려준다."""
    try:
        parts = path.resolve().relative_to(ROOT / "docs").parts
    except ValueError:
        return None
    if parts[-1].startswith(".") and parts[-1] != ".gitkeep":
        return None
    if any(rx.fullmatch("/".join(parts)) for rx in DOC_MAP):
        return None
    return (f"{rel(path)}: L5 문서의 지도에 없는 문서다. 새 종류가 필요하면 docs/README.md의 "
            f"\"문서의 지도\"를 먼저 고친다")


def disposition_problems(path: Path, lines):
    """리뷰의 "처리" 표에서 처리의 값과 받아들이지 않음의 이유와 결정한 사람을 검사한다."""
    problems = []
    cols = None
    for i, line in enumerate(lines, 1):
        if not line.startswith("|"):
            cols = None
            continue
        cells = split_row(line)
        if "처리" in cells and "결정한 사람" in cells:
            cols = (cells.index("처리"), cells.index("이유") if "이유" in cells else None,
                    cells.index("결정한 사람"))
            continue
        if cols is None or all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        what, why, who = cols
        if len(cells) <= max(c for c in cols if c is not None):
            continue
        value = cells[what]
        if value not in DISPOSITIONS:
            problems.append(f"{rel(path)}:{i}: L6 처리는 {', '.join(DISPOSITIONS)} 중 하나다(지금: {value or '없음'})")
        elif value == "받아들이지 않음":
            if why is None or not cells[why]:
                problems.append(f"{rel(path)}:{i}: L6 받아들이지 않음에는 이유를 적는다")
            if cells[who] != "사용자":
                problems.append(f"{rel(path)}:{i}: L6 받아들이지 않음은 사용자만 정한다(지금: {cells[who] or '없음'})")
    return problems


def split_row(line: str):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def lint_file(path: Path):
    problems = []
    mp = map_problem(path)
    if mp:
        problems.append(mp)
    kind = doc_kind(path)
    if kind is None or path.suffix != ".md":
        return problems
    lines = path.read_text(encoding="utf-8").splitlines()

    if kind == "review":
        problems += disposition_problems(path, lines)

    # L1 상태의 줄
    if kind in STATUS_DIRS or kind == "root":
        first = next((l for l in lines if l.startswith("- ")), None)
        if first is None or not first.startswith("- 상태:"):
            problems.append(f"{rel(path)}: L1 첫 항목이 `- 상태:`가 아니다")

    # L2, L3
    level_col = None
    in_table = False
    for i, line in enumerate(lines, 1):
        if line.startswith("|"):
            cells = split_row(line)
            if "수준" in cells and not re.fullmatch(r"-+", cells[0] or "x"):
                level_col = cells.index("수준")
                in_table = True
                continue
            if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                continue
            if in_table and level_col is not None and len(cells) > level_col:
                level = cells[level_col]
                if level in LEVEL_KEYWORDS:
                    present = {k for k, rx in LEVEL_KEYWORDS.items() if rx.search(line)}
                    # MUST NOT의 문장은 "절대"만 쓰고 "반드시"를 쓰지 않는다.
                    if present != {level}:
                        got = ", ".join(sorted(present)) or "없음"
                        problems.append(
                            f"{rel(path)}:{i}: L2 수준은 {level}인데 문장의 키워드는 {got}이다")
            continue
        in_table = False
        level_col = None
        if REQ_BULLET.match(line):
            present = {k for k, rx in LEVEL_KEYWORDS.items() if rx.search(line)}
            if len(present) != 1:
                got = ", ".join(sorted(present)) or "없음"
                problems.append(
                    f"{rel(path)}:{i}: L2 요구의 줄에는 굵은 키워드가 한 종류여야 한다(지금: {got})")
            continue
        if kind in KEYWORD_DIRS and ANY_KEYWORD.search(line):
            problems.append(f"{rel(path)}:{i}: L3 굵은 키워드가 요구의 표와 목록 밖에 있다")

    # L4 쌓기만 하는 문서
    if kind in ("journal", "review"):
        try:
            out = subprocess.run(
                ["git", "-C", str(ROOT), "diff", "HEAD", "--unified=0", "--", str(path)],
                capture_output=True, text=True, timeout=10)
        except Exception:
            out = None
        if out is not None and out.returncode == 0:
            removed = [l for l in out.stdout.splitlines() if l.startswith("-") and not l.startswith("---")]
            if removed:
                problems.append(f"{rel(path)}: L4 일지와 리뷰의 기존 {len(removed)}줄이 지워졌거나 고쳐졌다")
    return problems


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    if argv == ["--all"]:
        files = sorted(f for f in ROOT.glob("docs/**/*") if f.is_file()) + [ROOT / "AGENTS.md"]
    else:
        files = [Path(a) for a in argv]
    all_problems = []
    for f in files:
        if f.exists():
            all_problems += lint_file(f)
    for p in all_problems:
        print(p)
    if all_problems:
        print(f"docs-lint: {len(all_problems)}건", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
