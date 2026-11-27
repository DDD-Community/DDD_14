#!/usr/bin/env python3
"""위키의 정책이 정책 기록(docs/policy)을 쓴 뒤에 바뀌었는지 알려 준다. 읽기 전용이다.

정책 기록의 머리(상태의 줄 아래)에 세 줄이 있다.
  - 위키: <소유자>/<저장소>
  - 파일: <위키 저장소 안의 정책 파일 경로>
  - 해시: <기록한 시점의 커밋 해시>
이 스크립트는 그 해시의 정책과 위키의 최신 정책을 비교한다. 위키와 기록과 spec을 고치지 않는다.

정책은 위키에서 `- **UPL-03** 문장` 형태의 줄이고, 가장 가까운 위의 `### 확정|검토 중|미결정` 제목이 상태다.

사용: python3 scripts/policy_check.py                     (docs/policy의 모든 기록을 위키 최신과 비교)
      python3 scripts/policy_check.py --table 소유자/저장소 경로 [ref]
                                                            (기록에 붙일 정책 표를 출력)
      python3 scripts/policy_check.py --diff 옛파일 새파일  (로컬 파일 둘의 정책을 비교. 시험용)
      python3 scripts/policy_check.py --coverage 소유자/저장소 경로 [--json 이슈.json] [--wiki-file 파일]
                                                            (위키의 확정 정책 중 이슈의 `기획:` 줄에 없는 것을 찾는다)
종료 코드: 0 바뀐 것이 없다(--coverage는 빠진 정책이 없다), 1 바뀐 것이 있다(빠진 정책이 있다), 2 위키를 읽지 못했다.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY = re.compile(r"^-\s+\*\*([A-Z]{2,5}-\d{2,3})\*\*\s*(.*)$")
HEADING = re.compile(r"^#{2,4}\s+(.*)$")
STATUSES = ("확정", "검토 중", "미결정")


def parse_policies(text):
    """마크다운에서 {정책 번호: (상태, 문장)}을 모은다."""
    out, status = {}, "?"
    for line in text.splitlines():
        h = HEADING.match(line)
        if h:
            name = h.group(1).strip()
            if name in STATUSES:
                status = name
            continue
        m = POLICY.match(line)
        if m:
            pid, body = m.group(1), m.group(2).strip()
            out[pid] = ("폐기" if "폐기" in body else status, body)
    return out


def gh_api(path, raw=False):
    cmd = ["gh", "api", *path.split(" ")]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "gh api가 실패했다")
    return r.stdout


def fetch(repo, path, ref):
    return gh_api(f"repos/{repo}/contents/{path}?ref={ref}", raw=True)


def head_sha(repo):
    return gh_api(f"repos/{repo}/commits/HEAD --jq .sha").strip()


def read_record(path: Path):
    meta = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- (위키|파일|해시):\s*(\S+)", line)
        if m:
            meta[m.group(1)] = m.group(2)
        if line.startswith("## "):
            break
    return meta


def cited_by(pid):
    """spec에서 이 정책을 근거로 쓴 AC의 행을 찾는다."""
    hits = []
    for f in sorted((ROOT / "docs" / "spec").glob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("|") and re.search(rf"\b{re.escape(pid)}\b", line):
                cell = line.strip().strip("|").split("|")[0].strip()
                hits.append(f"{cell} ({f.relative_to(ROOT)}:{n})")
    return hits


def compare(old, new):
    """두 정책 모음의 차이를 줄로 돌려준다."""
    lines = []
    for pid in sorted(set(old) | set(new)):
        if pid not in old:
            lines.append((pid, f"추가: {new[pid][0]}, {new[pid][1]}"))
        elif pid not in new:
            lines.append((pid, "위키에서 사라졌다(번호는 지우지 않고 폐기로 표시하는 것이 위키의 규칙이다)"))
        else:
            (os_, ot), (ns, nt) = old[pid], new[pid]
            if os_ != ns:
                lines.append((pid, f"상태가 바뀌었다: {os_} → {ns}"))
            if ot != nt:
                lines.append((pid, f"문장이 바뀌었다: \"{ot}\" → \"{nt}\""))
    return lines


def report(label, diffs):
    for pid, msg in diffs:
        print(f"  {pid}: {msg}")
        cites = cited_by(pid)
        if cites:
            print(f"    이 정책을 근거로 쓰는 AC: {', '.join(cites)}")
    return bool(diffs)


def check_records():
    records = sorted((ROOT / "docs" / "policy").glob("*.md"))
    if not records:
        print("policy: 정책 기록이 없다(docs/policy/)")
        return 0
    changed, failed = False, False
    for rec in records:
        meta = read_record(rec)
        rel = rec.relative_to(ROOT)
        if not {"위키", "파일", "해시"} <= set(meta):
            print(f"{rel}: 위키, 파일, 해시 줄이 없어 비교하지 못한다")
            failed = True
            continue
        repo, path, old_ref = meta["위키"], meta["파일"], meta["해시"]
        try:
            new_ref = head_sha(repo)
            if not new_ref:
                raise RuntimeError("위키의 최신 해시를 읽지 못했다")
            if new_ref.startswith(old_ref) or old_ref.startswith(new_ref):
                print(f"{rel}: 위키와 같다({old_ref[:7]})")
                continue
            old = parse_policies(fetch(repo, path, old_ref))
            new = parse_policies(fetch(repo, path, new_ref))
        except Exception as e:
            print(f"{rel}: 위키를 읽지 못했다: {e}")
            failed = True
            continue
        diffs = compare(old, new)
        if not diffs:
            print(f"{rel}: 위키의 다른 파일만 바뀌었다({old_ref[:7]} → {new_ref[:7]}). 이 파일의 정책은 같다")
            continue
        print(f"{rel}: 위키가 바뀌었다({old_ref[:7]} → {new_ref[:7]})")
        changed |= report(str(rel), diffs)
        print("  순서: 정책 기록, spec, 코드 순으로 고친다. spec은 사용자의 승인을 받은 뒤 고친다.")
    if failed:
        return 2
    return 1 if changed else 0


ID_RANGE = re.compile(r"\b([A-Z]{2,5})-(\d{2,3})(?:\s*~\s*(?:([A-Z]{2,5})-)?(\d{2,3}))?\b")


def expand_ids(text):
    """`UPL-01~04`와 `UPL-01, UPL-03`에서 정책 번호의 집합을 만든다."""
    ids = set()
    for prefix, a, prefix2, b in ID_RANGE.findall(text or ""):
        width = len(a)
        lo, hi = int(a), int(b) if b else int(a)
        if prefix2 and prefix2 != prefix or hi < lo:
            ids.add(f"{prefix}-{a}")
            continue
        ids.update(f"{prefix}-{n:0{width}d}" for n in range(lo, hi + 1))
    return ids


def issue_policies(issues):
    """이슈 본문의 `기획:` 줄에서 {정책 번호: [이슈 번호]}를 모은다."""
    out = {}
    for i in issues:
        m = re.search(r"(?m)^\s*기획:\s*(.*)$", i.get("body") or "")
        for pid in expand_ids(m.group(1)) if m else ():
            out.setdefault(pid, []).append(i["number"])
    return out


def coverage(policies, issues):
    """(이슈가 없는 확정 정책, 확정이 아닌데 이슈가 있는 정책, 위키에 없는데 이슈가 가리키는 번호)."""
    cited = issue_policies(issues)
    missing = [pid for pid, (st, _) in policies.items() if st == "확정" and pid not in cited]
    premature = [(pid, st, cited[pid]) for pid, (st, _) in policies.items() if st in ("검토 중", "미결정") and pid in cited]
    ghosts = [(pid, nums) for pid, nums in cited.items() if pid not in policies and pid.split("-")[0] in {p.split("-")[0] for p in policies}]
    return missing, premature, ghosts


def load_issues(argv):
    if "--json" in argv:
        import json
        return json.load(open(argv[argv.index("--json") + 1], encoding="utf-8"))
    import json
    out = subprocess.run(["gh", "issue", "list", "--state", "all", "--limit", "200", "--json", "number,title,state,body"],
                         capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "gh issue list가 실패했다")
    return json.loads(out.stdout)


def run_coverage(argv):
    args = [a for a in argv[1:]]
    wiki_file = args[args.index("--wiki-file") + 1] if "--wiki-file" in args else None
    try:
        if wiki_file:
            policies = parse_policies(Path(wiki_file).read_text(encoding="utf-8"))
        else:
            repo, path = args[0], args[1]
            policies = parse_policies(fetch(repo, path, head_sha(repo)))
        issues = load_issues(args)
    except Exception as e:
        print(f"coverage: 읽지 못했다: {e}")
        return 2
    if not policies:
        print("coverage: 위키 파일에서 정책을 하나도 읽지 못했다. 위키의 정책 줄 형식(`- **UPL-03** 문장`)이 바뀌었는지 확인한다.")
        return 2
    missing, premature, ghosts = coverage(policies, issues)
    confirmed = sum(1 for st, _ in policies.values() if st == "확정")
    print(f"coverage: 확정 정책 {confirmed}개 중 이슈가 없는 것 {len(missing)}개")
    for pid in missing:
        print(f"  이슈 없음: {pid} {policies[pid][1][:60]}")
    for pid, st, nums in premature:
        print(f"  확정이 아닌데 이슈가 있다: {pid}({st}) 이슈 {', '.join('#' + str(n) for n in nums)}")
    for pid, nums in ghosts:
        print(f"  위키에 없는 번호를 가리킨다: {pid} 이슈 {', '.join('#' + str(n) for n in nums)}")
    return 1 if missing else 0


def main(argv):
    if argv[:1] == ["--diff"] and len(argv) == 3:
        old = parse_policies(Path(argv[1]).read_text(encoding="utf-8"))
        new = parse_policies(Path(argv[2]).read_text(encoding="utf-8"))
        return 1 if report("diff", compare(old, new)) else 0
    if argv[:1] == ["--coverage"]:
        return run_coverage(argv)
    if argv[:1] == ["--table"] and len(argv) in (3, 4):
        repo, path = argv[1], argv[2]
        ref = argv[3] if len(argv) == 4 else head_sha(repo)
        pol = parse_policies(fetch(repo, path, ref))
        print(f"<!-- 위키 {repo} {path} @ {ref} -->")
        print("| 번호 | 위키 상태 | 문장 | 이 슬라이스 |")
        print("|---|---|---|---|")
        for pid, (st, body) in pol.items():
            print(f"| {pid} | {st} | {body} | |")
        return 0
    if argv:
        print(__doc__)
        return 0
    return check_records()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
