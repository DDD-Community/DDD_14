#!/usr/bin/env python3
"""spec의 AC와 domain의 R이 테스트에 닿는지 확인한다(`@Covers`).

- docs/spec, docs/domain의 표 첫 칸에 있는 `AC-n.m`, `R-n.m`을 모은다. 행에 "폐기"가 있으면 뺀다.
- src/test의 `@Covers("AC-1.1")`, `@Covers({"AC-1.1", "R-1.2"})`에서 ID를 모은다.
- ID에 테스트가 없으면 실패한다. 테스트가 없는 ID를 가리켜도 실패한다.
- 근거: spec의 AC 행은 근거의 정책 번호(예: UPL-03)를 가진다. 정책이 아닌 기술 결정이면 행에 "기술 결정"을 쓴다.
  정책 번호는 docs/policy의 기록에 있어야 하고 위키 상태가 확정이어야 한다(검토 중과 미결정은 구현하지 않는다).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r"^(?:AC|R)-\d+\.\d+$")
POLICY_ID = re.compile(r"\b[A-Z]{2,5}-\d{2,3}\b")
TECH_BASIS = "기술 결정"


def defined_ids():
    ids = {}
    for d in ("spec", "domain"):
        for f in sorted((ROOT / "docs" / d).glob("*.md")):
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if not line.startswith("|"):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if cells and ID.match(cells[0]) and "폐기" not in line:
                    ids[cells[0]] = f"{f.relative_to(ROOT)}:{n}"
    return ids


def policy_status():
    """docs/policy의 기록에서 {정책 번호: 위키 상태}를 모은다."""
    out = {}
    for f in sorted((ROOT / "docs" / "policy").glob("*.md")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and POLICY_ID.fullmatch(cells[0]):
                out[cells[0]] = cells[1]
    return out


def basis_problems():
    """spec의 AC가 확정된 정책을 근거로 가지는지 검사한다."""
    known = policy_status()
    problems = []
    for f in sorted((ROOT / "docs" / "spec").glob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not (cells and ID.match(cells[0]) and cells[0].startswith("AC-")) or "폐기" in line:
                continue
            where = f"{f.relative_to(ROOT)}:{n}"
            cited = POLICY_ID.findall(" ".join(cells[1:]))
            if not cited and TECH_BASIS not in line:
                problems.append(f"근거가 없는 AC: {cells[0]} ({where}). 정책 번호나 \"{TECH_BASIS}\"를 쓴다")
            for pid in cited:
                st = known.get(pid)
                if st is None:
                    problems.append(f"정책 기록에 없는 정책: {cells[0]}의 {pid} ({where})")
                elif st != "확정":
                    problems.append(f"확정이 아닌 정책을 근거로 쓴다: {cells[0]}의 {pid}는 {st} ({where})")
    return problems


def covered_ids():
    cov = {}
    test_dir = ROOT / "src" / "test"
    if not test_dir.exists():
        return cov
    pat = re.compile(r"@Covers\(\s*(\{[^}]*\}|\"[^\"]*\")\s*\)")
    for f in sorted(test_dir.rglob("*.java")):
        text = f.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            for i in re.findall(r"\"([^\"]+)\"", m.group(1)):
                cov.setdefault(i, []).append(str(f.relative_to(ROOT)))
    return cov


def main():
    defined, covered = defined_ids(), covered_ids()
    problems = basis_problems()
    for i, where in sorted(defined.items()):
        if i not in covered:
            problems.append(f"테스트가 없는 ID: {i} ({where})")
    for i, files in sorted(covered.items()):
        if i not in defined:
            problems.append(f"정의에 없는 ID를 가리킨다: {i} ({files[0]})")
    if not defined and not covered:
        print("trace: AC와 R이 아직 없다(spec과 domain이 없다)")
        return 0
    for p in problems:
        print(p)
    print(f"trace: 정의 {len(defined)}개, 테스트가 닿은 ID {len(set(covered) & set(defined))}개, 문제 {len(problems)}건")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
