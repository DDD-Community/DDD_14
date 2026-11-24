#!/bin/bash
# 훅의 막는 경우와 통과하는 경우를 확인한다. 임시 디렉터리에 가짜 프로젝트를 만들어 쓴다.
# 사용: .claude/hooks/test-hooks.sh   (실패가 있으면 0이 아닌 값으로 끝난다)
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
proj="$tmp/server"   # 모노레포: git 저장소는 $tmp, 프로젝트 폴더는 $tmp/server
mkdir -p "$proj"
export CLAUDE_PROJECT_DIR="$proj"
mkdir -p "$proj/docs/plan" "$proj/docs/spec" "$proj/docs/journal" "$proj/scripts" "$proj/src/main"
cp "$here/../../scripts/docs_lint.py" "$proj/scripts/docs_lint.py"
pass=0; fail=0

expect() { # 이름 기대코드 훅 json
  local name=$1 want=$2 hook=$3 json=$4 got
  echo "$json" | "$here/$hook" >/dev/null 2>&1
  got=$?
  if [ "$got" = "$want" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "실패: $name (기대 $want, 실제 $got)"; fi
}
edit() { echo "{\"tool_name\":\"Edit\",\"cwd\":\"$proj\",\"tool_input\":{\"file_path\":\"$proj/$1\"}}"; }
agent_edit() { echo "{\"tool_name\":\"Write\",\"agent_type\":\"test-author\",\"cwd\":\"$proj\",\"tool_input\":{\"file_path\":\"$proj/$1\"}}"; }
bash_cmd() { jq -n --arg c "$1" --arg d "$proj" '{tool_name:"Bash",cwd:$d,tool_input:{command:$c}}'; }
agent_bash() { jq -n --arg c "$1" --arg d "$proj" '{tool_name:"Bash",agent_type:"test-author",cwd:$d,tool_input:{command:$c}}'; }
agent_read() { echo "{\"tool_name\":\"Read\",\"agent_type\":\"test-author\",\"cwd\":\"$proj\",\"tool_input\":{\"file_path\":\"$proj/$1\"}}"; }

# guard-edit: plan이 없으면 src/main은 막지 않고 알린다
printf '# plan\n\n- 상태: 제안 (AI가 제안)\n' > "$proj/docs/plan/01-a.md"
expect "plan 제안일 때 src/main 편집은 통과" 0 guard-edit.sh "$(edit src/main/A.java)"
expect "src/test 편집은 통과" 0 guard-edit.sh "$(edit src/test/ATest.java)"
expect ".env 편집" 2 guard-edit.sh "$(edit .env)"
expect ".env.example 편집은 통과" 0 guard-edit.sh "$(edit .env.example)"
printf '# plan\n\n- 상태: 승인 (사용자가 결정, 2026-11-22 일지 스텝 1)\n' > "$proj/docs/plan/01-a.md"
expect "plan 승인일 때 src/main 편집" 0 guard-edit.sh "$(edit src/main/A.java)"
printf '# spec\n\n- 상태: 승인 (사용자가 결정, 2026-11-22 일지 스텝 1)\n' > "$proj/docs/spec/01-a.md"
expect "구현 중 승인된 spec 편집" 2 guard-edit.sh "$(edit docs/spec/01-a.md)"
printf '# spec\n\n- 상태: 제안 (AI가 제안)\n' > "$proj/docs/spec/02-b.md"
expect "구현 중이어도 제안인 spec은 편집" 0 guard-edit.sh "$(edit docs/spec/02-b.md)"
printf '# plan\n\n- 상태: 닫음 (2026-11-22 일지 스텝 2)\n' > "$proj/docs/plan/01-a.md"
expect "plan이 닫히면 승인된 spec 편집" 0 guard-edit.sh "$(edit docs/spec/01-a.md)"

# restrict-test-author
expect "메인 세션은 src/main을 쓴다(제한 없음)" 0 restrict-test-author.sh "$(edit src/main/A.java)"
expect "test-author가 src/test 쓰기" 0 restrict-test-author.sh "$(agent_edit src/test/ATest.java)"
expect "test-author가 src/main 쓰기" 2 restrict-test-author.sh "$(agent_edit src/main/A.java)"
expect "test-author가 src/main 읽기" 2 restrict-test-author.sh "$(agent_read src/main/A.java)"
expect "test-author가 docs 읽기" 0 restrict-test-author.sh "$(agent_read docs/spec/01-a.md)"
reviewer() { jq -n --arg a "$1" --arg t "$2" --arg f "$proj/$3" --arg d "$proj" '{tool_name:$t,agent_type:$a,cwd:$d,tool_input:{file_path:$f,path:$f}}'; }
expect "doc-reviewer가 spec 읽기" 0 restrict-test-author.sh "$(reviewer doc-reviewer Read docs/spec/01-a.md)"
expect "doc-reviewer가 리뷰 문서 읽기" 2 restrict-test-author.sh "$(reviewer doc-reviewer Read docs/review/01-a.md)"
expect "code-reviewer가 리뷰 폴더 Grep" 2 restrict-test-author.sh "$(reviewer code-reviewer Grep docs/review)"
expect "doc-reviewer가 자기의 이전 리포트 읽기" 0 restrict-test-author.sh "$(reviewer doc-reviewer Read _workspace/review-01-doc-reviewer.md)"
expect "doc-reviewer가 code-reviewer의 리포트 읽기" 2 restrict-test-author.sh "$(reviewer doc-reviewer Read _workspace/review-01-code-reviewer.md)"
expect "code-reviewer가 doc-reviewer의 리포트 읽기" 2 restrict-test-author.sh "$(reviewer code-reviewer Read _workspace/review-01-doc-reviewer.md)"
expect "메인 세션은 리뷰 문서를 읽는다" 0 restrict-test-author.sh "$(reviewer '' Read docs/review/01-a.md)"
expect "test-author의 gradlew test" 0 restrict-test-author.sh "$(agent_bash './gradlew test --tests X')"
expect "test-author의 gradlew test에 명령을 이어 붙임(&&)" 2 restrict-test-author.sh "$(agent_bash './gradlew test && cat src/main/A.java')"
expect "test-author의 gradlew test에 $( ) 붙임" 2 restrict-test-author.sh "$(agent_bash './gradlew test $(cat src/main/A.java)')"
expect "test-author의 git 명령" 2 restrict-test-author.sh "$(agent_bash 'git status')"

# journal-check (git 저장소가 필요하다. 저장소는 $tmp, 프로젝트는 $proj)
( cd "$tmp" && git init -q && git config user.email t@t && git config user.name t )
mkdir -p "$proj/src/main"; echo x > "$proj/src/main/A.java"; ( cd "$proj" && git add src/main/A.java )
expect "일지 없는 코드 커밋" 2 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
echo x > "$proj/docs/journal/2026-11-22.md"; ( cd "$proj" && git add docs/journal/2026-11-22.md )
expect "옛 이름(날짜.md)의 일지" 2 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$proj" && git reset -q docs/journal/2026-11-22.md ); rm "$proj/docs/journal/2026-11-22.md"
echo x > "$proj/docs/journal/2026-11-22-seobang.md"; ( cd "$proj" && git add docs/journal/2026-11-22-seobang.md )
expect "이름이 있는 일지가 있는 커밋(handle 없음)" 0 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$proj" && git config harness.handle seobang )
expect "내 일지(handle=seobang)" 0 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
echo x > "$proj/docs/journal/2026-11-22-other.md"; ( cd "$proj" && git add docs/journal/2026-11-22-other.md )
expect "다른 사람의 일지" 2 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$proj" && git reset -q docs/journal/2026-11-22-other.md ); rm "$proj/docs/journal/2026-11-22-other.md"
expect "git add -A" 2 journal-check.sh "$(bash_cmd 'git add -A')"
expect "git add ." 2 journal-check.sh "$(bash_cmd 'git add .')"
expect "git add 경로 지정" 0 journal-check.sh "$(bash_cmd 'git add src/main/A.java')"
( cd "$proj" && git config --unset harness.handle )
# server/ 밖(예: client/)의 변경은 이 프로젝트의 일지를 요구하지 않는다
( cd "$proj" && git reset -q ); mkdir -p "$tmp/client"; echo x > "$tmp/client/a.ts"; ( cd "$tmp" && git add client/a.ts )
expect "server/ 밖의 변경만 있는 커밋" 0 journal-check.sh "$(bash_cmd 'git commit -m "feat: client"')"
( cd "$tmp" && git reset -q ); ( cd "$proj" && git add src/main/A.java docs/journal/2026-11-22-seobang.md )
expect "git commit -am" 2 journal-check.sh "$(bash_cmd 'git commit -am "feat: a"')"
expect "git commit -a -m" 2 journal-check.sh "$(bash_cmd 'git commit -a -m "feat: a"')"
expect "git commit --all" 2 journal-check.sh "$(bash_cmd 'git commit --all -m "feat: a"')"
expect "메시지 안의 -a는 막지 않는다" 0 journal-check.sh "$(bash_cmd 'git commit -m "feat: -a 옵션"')"
expect "--amend는 막지 않는다" 0 journal-check.sh "$(bash_cmd 'git commit --amend --no-edit')"
echo x > "$proj/.env"; ( cd "$proj" && git add .env )
expect "스테이징된 .env" 2 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$proj" && git reset -q .env ); rm "$proj/.env"
echo x > "$tmp/.env.local"; ( cd "$tmp" && git add .env.local )
expect "server/ 밖의 .env.local도 막는다" 2 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$tmp" && git reset -q .env.local ); rm "$tmp/.env.local"
mkdir -p "$proj/src/main/resources"; echo x > "$proj/src/main/resources/app.pem"; ( cd "$proj" && git add src/main/resources/app.pem )
expect "스테이징된 .pem" 2 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$proj" && git reset -q src/main/resources/app.pem ); rm -r "$proj/src/main/resources"
echo x > "$proj/.env.example"; ( cd "$proj" && git add .env.example )
expect ".env.example은 통과" 0 journal-check.sh "$(bash_cmd 'git commit -m "feat: a"')"
( cd "$proj" && git reset -q .env.example ); rm "$proj/.env.example"

# pre-push-check
( cd "$proj" && git commit -qm init && git checkout -q -b feature/a )
expect "check 기록 없이 push" 2 pre-push-check.sh "$(bash_cmd 'git push origin feature/a')"
( cd "$proj" && git rev-parse HEAD > "$(git rev-parse --git-path check-passed)" )
expect "check 기록이 있는 push" 0 pre-push-check.sh "$(bash_cmd 'git push origin feature/a')"
expect "기능 브랜치에서 인자 없는 push" 0 pre-push-check.sh "$(bash_cmd 'git push')"
expect "이름에 main이 들어간 브랜치" 0 pre-push-check.sh "$(bash_cmd 'git push -u origin feature/main-page')"
expect "main으로 push" 2 pre-push-check.sh "$(bash_cmd 'git push origin main')"
expect "HEAD:main" 2 pre-push-check.sh "$(bash_cmd 'git push origin HEAD:main')"
expect "refs/heads/main" 2 pre-push-check.sh "$(bash_cmd 'git push origin feature/a:refs/heads/main')"
expect "-u origin develop" 2 pre-push-check.sh "$(bash_cmd 'git push -u origin develop')"
expect "--force-with-lease" 2 pre-push-check.sh "$(bash_cmd 'git push --force-with-lease origin feature/a')"
expect "-f" 2 pre-push-check.sh "$(bash_cmd 'git push -f origin feature/a')"
expect "+refspec" 2 pre-push-check.sh "$(bash_cmd 'git push origin +feature/a')"
expect "--all" 2 pre-push-check.sh "$(bash_cmd 'git push --all origin')"
expect "명령을 이은 뒤의 main push" 2 pre-push-check.sh "$(bash_cmd 'git status && git push origin main')"
expect "둘째 줄의 main push" 2 pre-push-check.sh "$(bash_cmd $'git status\ngit push origin main')"
expect "heredoc 본문의 push 글자" 0 pre-push-check.sh "$(bash_cmd $'cat > a.sh <<\'EOF\'\ngit push origin main\nEOF')"
expect "<<-와 탭의 끝 표시" 0 pre-push-check.sh "$(bash_cmd $'cat <<-EOF > a.md\n\tgit push -f origin main\n\tEOF')"
expect "커밋 메시지의 heredoc" 0 pre-push-check.sh "$(bash_cmd $'git commit -F - <<"EOF"\ngit push origin main 은 막는다\nEOF')"
expect "heredoc 뒤의 main push" 2 pre-push-check.sh "$(bash_cmd $'cat > a.sh <<EOF\necho a\nEOF\ngit push origin main')"
expect "<<<는 heredoc이 아니다" 2 pre-push-check.sh "$(bash_cmd $'jq . <<<"$x"\ngit push origin main')"
( cd "$proj" && git checkout -q -B main )
expect "main에서 인자 없는 push" 2 pre-push-check.sh "$(bash_cmd 'git push')"
expect "main에서 원격만 준 push" 2 pre-push-check.sh "$(bash_cmd 'git push origin')"
expect "main에서 HEAD push" 2 pre-push-check.sh "$(bash_cmd 'git push origin HEAD')"
( cd "$proj" && git checkout -q feature/a )

# docs-lint
mkdir -p "$proj/docs/adr"
printf '# adr\n\n- 상태: 제안 (AI가 제안)\n\n- (1) 하나는 **반드시** 한다. [리뷰]\n' > "$proj/docs/adr/0001-a.md"
expect "docs-lint 통과" 0 docs-lint.sh "$(edit docs/adr/0001-a.md)"
printf '# adr\n\n- 상태: 제안 (AI가 제안)\n\n- (1) 하나는 한다. [리뷰]\n' > "$proj/docs/adr/0001-a.md"
expect "docs-lint 키워드 없음" 2 docs-lint.sh "$(edit docs/adr/0001-a.md)"
printf '# adr\n\n설명에 **반드시**가 있다.\n' > "$proj/docs/adr/0001-a.md"
expect "docs-lint 상태의 줄 없음과 표 밖 키워드" 2 docs-lint.sh "$(edit docs/adr/0001-a.md)"

echo "훅 테스트: 통과 $pass, 실패 $fail"
[ "$fail" -eq 0 ]
