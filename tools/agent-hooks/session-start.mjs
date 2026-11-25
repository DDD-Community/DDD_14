// SessionStart: 진행 중인 plan을 알려 줘서 새 세션(또는 다른 사람)이 이어서 작업하게 한다.
// stdout은 에이전트 컨텍스트에 들어간다.
import { activePlans, readInput, repoRoot } from './lib.mjs';

const plans = activePlans(repoRoot(readInput().cwd));
if (plans.length) {
  console.log(
    `진행 중인 plan: ${plans.join(', ')}\n이어서 작업한다면 해당 plan의 단계 체크리스트와 진행 로그부터 읽으세요.`,
  );
}
