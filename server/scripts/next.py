#!/usr/bin/env python3
"""시작할 수 있는 이슈를 계산한다. 읽기 전용이다.

시작할 수 있는 이슈: 열려 있고, 본문의 `의존: #1, #2` 줄에 적힌 이슈가 모두 닫혔다.
이슈마다 담당자를 보이고, 제목이 `종류: 요약`이 아니면 표시한다(종류가 브랜치 이름의 앞부분이 된다).
저장하지 않는다. 이슈의 열림과 닫힘에서 매번 계산한다.

역할 라벨: --label server 로 server 라벨이 붙은 이슈와 라벨이 없는 이슈만 보여 준다. 라벨이 없는 이슈는 어느 역할에도 보인다.
      의존한 이슈는 라벨과 관계없이 닫혔는지만 본다(클라이언트의 이슈에 서버가 의존할 수 있다).

사용: python3 scripts/next.py            (gh issue list를 읽는다)
      python3 scripts/next.py --label server
      python3 scripts/next.py --json F   (시험용. F는 gh issue list --json의 결과)
"""
import json
import re
import subprocess
import sys

FIELDS = "number,title,state,body,labels,assignees"


def load(argv):
    if "--json" in argv:
        return json.load(open(argv[argv.index("--json") + 1], encoding="utf-8"))
    r = subprocess.run(["gh", "issue", "list", "--state", "all", "--limit", "200", "--json", FIELDS],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("gh issue list가 실패했다: " + r.stderr.strip())
    return json.loads(r.stdout)


def deps_of(body):
    m = re.search(r"(?m)^\s*의존:\s*(.*)$", body or "")
    return [int(n) for n in re.findall(r"#(\d+)", m.group(1))] if m else []


ROLES = ("server", "client")


def label_names(issue):
    return {(l["name"] if isinstance(l, dict) else str(l)).lower() for l in issue.get("labels") or []}


def visible(issue, label):
    """라벨이 없으면 모두에게 보인다. 라벨이 있으면 역할 라벨에 label이 있어야 한다."""
    if not label:
        return True
    roles = label_names(issue) & set(ROLES)
    return not roles or label in roles


KINDS = ("test", "file", "docs", "chore", "setting", "feat", "refactor", "fix")


def kind_of(title):
    """제목의 앞부분 `종류: `에서 종류를 읽는다. 없으면 None이다."""
    m = re.match(r"\s*([a-z]+)\s*:", title or "")
    return m.group(1) if m and m.group(1) in KINDS else None


def owner_of(issue):
    names = [a["login"] if isinstance(a, dict) else str(a) for a in issue.get("assignees") or []]
    return ", ".join(names) if names else "담당 없음"


def line(issue):
    kind = kind_of(issue["title"])
    warn = "" if kind else " [제목에 종류가 없다]"
    return f"#{issue['number']} {issue['title']} ({owner_of(issue)}){warn}"


def compute(issues, label=None):
    state = {i["number"]: i["state"].upper() for i in issues}
    ready, waiting = [], []
    for i in sorted(issues, key=lambda x: x["number"]):
        if i["state"].upper() != "OPEN" or not visible(i, label):
            continue
        deps = deps_of(i.get("body"))
        unknown = [d for d in deps if d not in state]
        open_deps = [d for d in deps if state.get(d) == "OPEN"]
        if open_deps or unknown:
            waiting.append((i, open_deps, unknown))
        else:
            ready.append(i)
    return ready, waiting


def main():
    argv = sys.argv[1:]
    label = argv[argv.index("--label") + 1].lower() if "--label" in argv else None
    if label and label not in ROLES:
        sys.exit(f"--label은 {', '.join(ROLES)} 중 하나다: {label}")
    issues = load(argv)
    ready, waiting = compute(issues, label)
    done = sum(1 for i in issues if i["state"].upper() != "OPEN")
    print(f"닫힌 이슈 {done}개, 열린 이슈 {len(issues) - done}개" + (f" (역할: {label})" if label else "") + "\n")
    if ready:
        print("지금 시작할 수 있는 이슈:")
        for i in ready:
            deps = deps_of(i.get("body"))
            tail = f" (의존: {', '.join('#' + str(d) for d in deps)} 완료)" if deps else ""
            print(f"  {line(i)}{tail}")
    else:
        print("지금 시작할 수 있는 이슈가 없다.")
    if waiting:
        print("\n기다리는 이슈:")
        for i, open_deps, unknown in waiting:
            why = []
            if open_deps:
                why.append("먼저 끝나야 함 " + ", ".join(f"#{d}" for d in open_deps))
            if unknown:
                why.append("의존한 이슈를 찾을 수 없음 " + ", ".join(f"#{d}" for d in unknown))
            print(f"  {line(i)} ({'; '.join(why)})")


if __name__ == "__main__":
    main()
