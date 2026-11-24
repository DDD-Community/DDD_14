#!/usr/bin/env python3
"""문서와 git에서 지금 단계를 계산한다. 상태는 저장하지 않는다.

출력: 브랜치, 문서의 상태, 처리를 기다리는 리뷰, 안내, 마지막 일지의 마지막 스텝의 "남은 일", 계산한 단계와 이유.
단계는 추정이다. 구현과 검증이 끝났는지는 scripts/check.sh의 결과가 있어야 안다.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
STATUS_DIRS = ("policy", "domain", "spec", "adr", "plan")


def git(*args):
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def doc_status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- 상태:"):
            return line[len("- 상태:"):].strip().split(" ")[0] or "?"
        if line.startswith("- "):
            return "상태의 줄 없음"
    return "상태의 줄 없음"


def collect():
    out = {}
    for d in STATUS_DIRS:
        for f in sorted((DOCS / d).glob("*.md")):
            out.setdefault(d, []).append((f.relative_to(ROOT), doc_status(f)))
    return out


def my_handle():
    """git config harness.handle. 일지 파일 이름 `날짜-이름.md`의 이름이다."""
    return git("config", "harness.handle")


def journal_files():
    """내 일지가 있으면 내 일지만, 없으면 모든 일지를 날짜 순서로 돌려준다."""
    files = sorted((DOCS / "journal").glob("*.md"), key=lambda f: f.name)
    mine = my_handle()
    if mine:
        own = [f for f in files if f.stem.endswith("-" + mine)]
        if own:
            return own
    return files


def last_journal_remaining():
    journals = journal_files()
    if not journals:
        return None, []
    j = journals[-1]
    text = j.read_text(encoding="utf-8")
    steps = re.split(r"(?m)^## 스텝 ", text)
    if len(steps) < 2:
        return j, []
    last = steps[-1]
    title = "스텝 " + last.splitlines()[0]
    m = re.search(r"\*\*남은 일\*\*:\s*\n((?:- .*\n?|\s+.*\n?)+)", last)
    items = [l[2:].strip() for l in (m.group(1).splitlines() if m else []) if l.startswith("- ")]
    return (j.relative_to(ROOT), title), items


def unprocessed_reviews():
    """슬라이스의 리뷰 문서에서 "### 처리"가 없는 리뷰의 절과, 보류가 남은 절을 찾는다. 리뷰 한 번이 `## ` 절 하나다."""
    out = []
    for f in sorted((DOCS / "review").glob("*.md")):
        rel = f.relative_to(ROOT)
        for sec in re.split(r"(?m)^## ", f.read_text(encoding="utf-8"))[1:]:
            name = sec.splitlines()[0].strip()
            if "### 처리" not in sec:
                out.append(f"{rel} ({name})")
            elif re.search(r"\|\s*보류\s*\|", sec) and "처리의 변경" not in sec:
                out.append(f"{rel} ({name}, 보류가 남았다)")
    return out


def open_questions():
    """docs/policy의 기획 질문 표에서 상태가 "열림"인 행을 센다."""
    n = 0
    for f in sorted((DOCS / "policy").glob("*.md")):
        for line in f.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
            if cells and cells[-1].startswith("열림"):
                n += 1
    return n


def plan_tasks(plan: Path):
    counts = {"대기": 0, "진행": 0, "완료": 0}
    for line in plan.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            last = [c.strip() for c in line.strip().strip("|").split("|")][-1]
            if last in counts:
                counts[last] += 1
    return counts


def issue_of_branch(branch):
    """브랜치 `종류/<이슈번호>-<영문-요약>`에서 이슈 번호를 읽는다. 없으면 None."""
    m = re.match(r"^[a-z]+/(\d+)-", branch or "")
    return int(m.group(1)) if m else None


def marked(path, issue):
    """문서의 `- 이슈: #3, #7` 줄에 이 이슈 번호가 있는가."""
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("- 이슈:"):
            return issue in [int(n) for n in re.findall(r"#(\d+)", line)]
    return False


def compute(docs, issue=None):
    """issue가 있으면 그 이슈의 문서(`- 이슈: #번호`)만 보고 단계를 정한다. 없으면 모든 문서를 본다."""
    reasons = []
    if issue is not None:
        docs = {d: [(p, s) for p, s in items if d not in ("policy", "domain", "spec", "plan") or marked(p, issue)]
                for d, items in docs.items()}
        reasons.append(f"이슈 #{issue}의 문서만 본다")
        if not docs.get("policy"):
            return "1. 정책 읽기", reasons + [f"docs/policy에 `- 이슈: #{issue}`가 있는 정책 기록이 없다"]
        unconfirmed = [str(p) for p, s in docs["policy"] if not s.startswith("승인")]
        if unconfirmed:
            return "1. 정책 읽기", reasons + [f"사용자의 컨펌을 기다리는 정책 기록: {', '.join(unconfirmed)}"]
        content = [(p, s) for d in ("domain", "spec") for (p, s) in docs.get(d, [])]
        if not content:
            return "2. 문서", reasons + ["정책 기록은 있고 이 이슈의 domain과 spec이 아직 없다"]
    else:
        content = [(p, s) for d in ("domain", "spec") for (p, s) in docs.get(d, [])]
        if not content:
            if not docs.get("policy"):
                return "1. 정책 읽기", ["docs/policy에 정책 기록이 없다"]
            return "2. 문서", ["정책 기록은 있고 domain과 spec이 아직 없다"]
    q = open_questions()
    if q:
        reasons.append(f"기획 질문 {q}개가 열려 있다. 답이 필요한 정책은 구현하지 않고 다른 이슈를 한다")
    pending = [str(p) for p, s in content if not s.startswith("승인")]
    if pending:
        return "2. 문서", reasons + [f"승인을 기다리는 문서: {', '.join(pending)}"]
    plans = docs.get("plan", [])
    open_plans = [(p, s) for p, s in plans if not s.startswith("닫음")]
    if issue is not None and plans and not open_plans:
        return "8. 종료 뒤", reasons + ["이 이슈의 plan이 닫혔다. PR의 병합을 기다린다"]
    if not open_plans:
        return "3. 계획", reasons + ["열린 plan이 없다"]
    unapproved = [str(p) for p, s in open_plans if not s.startswith("승인")]
    if unapproved:
        return "3. 계획", reasons + [f"승인을 기다리는 plan: {', '.join(unapproved)}"]
    plan = ROOT / open_plans[0][0]
    c = plan_tasks(plan)
    reasons.append(f"plan {open_plans[0][0]}의 작업: 대기 {c['대기']}, 진행 {c['진행']}, 완료 {c['완료']}")
    if c["대기"] + c["진행"] == 0 and c["완료"] > 0:
        return "8. 종료 (7. 이해는 선택)", reasons + ["모든 작업이 완료다"]
    tests = list((ROOT / "src" / "test").rglob("*.java")) if (ROOT / "src" / "test").exists() else []
    if not tests:
        return "4. 테스트", reasons + ["src/test에 테스트가 없다"]
    return "5. 구현 또는 6. 검증", reasons + ["테스트는 있다. 구현의 진행과 검증은 check.sh의 결과가 필요하다"]


def stage_report(branch, docs):
    """단계의 출력 줄. 브랜치에 이슈 번호가 없으면 슬라이스 밖이라고 먼저 알리고, 모든 문서로 계산한 단계는 참고로 보인다."""
    issue = issue_of_branch(branch)
    stage, reasons = compute(docs, issue)
    if issue is not None:
        return [f"단계(추정): {stage}"] + [f"  - {r}" for r in reasons]
    return [
        "단계: 슬라이스 밖 (브랜치에 이슈 번호가 없다)",
        "  - 슬라이스는 `<종류>/<이슈번호>-<영문-요약>` 브랜치에서 한다. 새 슬라이스는 /next다",
        f"  - 참고: 모든 문서로 계산한 단계는 {stage}",
    ] + [f"    - {r}" for r in reasons]


def main():
    branch = git("branch", "--show-current") or "(git 저장소가 아니거나 커밋이 없다)"
    docs = collect()
    print(f"브랜치: {branch}")
    print("\n문서의 상태:")
    for d, items in docs.items():
        counts = {}
        for _, s in items:
            counts[s] = counts.get(s, 0) + 1
        print(f"  {d}: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    waiting = [(str(p), s) for items in docs.values() for p, s in items if s in ("초안", "제안")]
    if waiting:
        print("\n승인을 기다리는 문서:")
        for p, s in waiting:
            print(f"  - {p} ({s})")
    pending_reviews = unprocessed_reviews()
    if pending_reviews:
        print("\n처리 대기 리뷰(지적의 처리가 없다):")
        for r in pending_reviews:
            print(f"  - {r}")
    if docs.get("policy"):
        print("\n정책 기록이 있다. 위키가 바뀌었는지: python3 scripts/policy_check.py")
    if not my_handle():
        print("\n일지 이름이 없다. git config harness.handle <영문-이름>으로 정한다(일지 파일은 날짜-이름.md).")
    where, items = last_journal_remaining()
    print("\n마지막 일지의 남은 일:")
    if where is None:
        print("  (일지가 없다)")
    else:
        print(f"  {where[0]} {where[1]}")
        for i in items:
            print(f"  - {i}")
    print()
    for line in stage_report(branch, docs):
        print(line)


if __name__ == "__main__":
    main()
