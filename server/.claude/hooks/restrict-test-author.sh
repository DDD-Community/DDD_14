#!/bin/bash
# PreToolUse(Edit|Write|MultiEdit|Bash|Read|Grep|Glob): test-author가 도는 동안의 제한(ADR-0001의 8번).
#   - 쓰기는 src/test와 _workspace만.
#   - Bash는 ./gradlew compileTestJava와 ./gradlew test만. 명령을 이어 붙이는 문자가 있으면 막는다.
#   - src/main은 읽지 않는다(Read, 경로를 지정한 Grep과 Glob).
# 한계: 변수나 따옴표를 쓴 교묘한 우회는 못 막는다. 경로 없이 저장소 전체를 Grep하면 src/main이 섞일 수 있다. 에이전트의 지시문으로 보완한다(ADR-0001의 정하지 않은 것 4번).
# test-author가 아닌 호출(메인 세션, 다른 에이전트)은 항상 통과시킨다.
input=$(cat)
agent=$(jq -r '.agent_type // empty' <<<"$input" 2>/dev/null)
[ "$agent" = "test-author" ] || exit 0
tool=$(jq -r '.tool_name // empty' <<<"$input" 2>/dev/null)
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
proj=${CLAUDE_PROJECT_DIR:-${cwd:-.}}

case "$tool" in
  Bash)
    cmd=$(jq -r '.tool_input.command // empty' <<<"$input" 2>/dev/null)
    # 명령을 이어 붙이는 문자(; & | ` $( > <, 줄바꿈)가 있으면 허용한 명령으로 시작해도 막는다.
    if ! grep -q '[;&|`<>]' <<<"$cmd" && [[ "$cmd" != *'$('* ]] && [[ "$cmd" != *$'\n'* ]]; then
      case "$cmd" in
        "./gradlew compileTestJava"*|"./gradlew test"*) exit 0 ;;
      esac
    fi
    echo "차단: test-author는 Bash로 ./gradlew compileTestJava와 ./gradlew test만 실행한다(명령을 이어 붙이지 않는다). 실행하려던 명령: $cmd" >&2
    exit 2 ;;
  Read|Grep|Glob)
    path=$(jq -r '.tool_input.file_path // .tool_input.path // empty' <<<"$input" 2>/dev/null)
    pattern=$(jq -r '.tool_input.pattern // empty' <<<"$input" 2>/dev/null)
    case "$path$pattern" in
      *src/main*)
        echo "차단: test-author는 src/main을 읽지 않는다. 기대값은 문서(AC, R)에서만 가져온다." >&2
        exit 2 ;;
    esac
    exit 0 ;;
  Edit|Write|MultiEdit)
    file=$(jq -r '.tool_input.file_path // empty' <<<"$input" 2>/dev/null)
    [ -z "$file" ] && exit 0
    rel=${file#"$proj"/}
    case "$rel" in
      src/test/*|_workspace/*) exit 0 ;;
    esac
    echo "차단: test-author는 src/test/**와 _workspace/** 밖을 쓰지 않는다($rel). 구현은 메인 세션의 몫이다." >&2
    exit 2 ;;
esac
exit 0
