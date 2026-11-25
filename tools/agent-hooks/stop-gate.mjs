// Stop 훅 (Claude Code · Codex 공용): 에이전트가 작업을 끝내려 할 때
//   ① client 변경이 있으면 verify:fast + 바뀐 파일과 관련된 테스트 → 실패하면 되돌려 고치게 한다
//      같은 작업에서 3번 넘게 실패하면 더 막지 않는다 (lefthook·CI가 다시 잡는다)
//   ② 통과하면 변경 내용을 보고 필요한 스킬을 골라 한 번에 요청한다 (같은 변경에는 한 번만)
//      - client/src를 바꿨는데 plan이 없음 → new-feature
//      - 화면 파일(.tsx, .css)을 바꿈 → verify-ui
//      - 새 의존성 추가 → write-adr
//      - 항상 → review-changes
// 끄기: TTADAK_STOP_GATE=0 (전체), TTADAK_AUTO_SKILLS=0 (스킬 요청만. 검증은 계속 돈다)
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import {
  activePlans,
  baseRef,
  block,
  changedFiles,
  git,
  outputOf,
  readInput,
  repoRoot,
  run,
  tail,
} from './lib.mjs';

if (process.env.TTADAK_STOP_GATE === '0') process.exit(0);

const input = readInput();
const root = repoRoot(input.cwd);
const changed = changedFiles(root);
if (!changed.length) process.exit(0);

const marker = path.resolve(
  root,
  git(['rev-parse', '--git-dir'], root).trim(),
  'ttadak-stop-gate.json',
);
const state = existsSync(marker) ? JSON.parse(readFileSync(marker, 'utf8')) : {};
const save = (next) => writeFileSync(marker, JSON.stringify(next));

// ① 검증
const MAX_FAILURES = 3;
const clientDir = path.join(root, 'client');
const fail = (what, e) => {
  const failures = (state.failures ?? 0) + 1;
  if (failures > MAX_FAILURES) {
    save({ ...state, failures: 0 });
    process.stderr.write(
      `${what} 실패가 ${MAX_FAILURES}번 반복되어 더 막지 않습니다. 남은 오류를 사람에게 보고하세요.`,
    );
    process.exit(0);
  }
  save({ ...state, failures });
  block(
    `${what} 실패 (${failures}/${MAX_FAILURES}). 아래 오류를 고친 뒤 끝내세요.\n${tail(outputOf(e))}`,
  );
};
try {
  run('pnpm', ['-s', 'verify:fast'], clientDir);
} catch (e) {
  fail('verify:fast', e);
}
const srcFiles = changed
  .filter((f) => /^client\/src\/.+\.(ts|tsx)$/.test(f) && existsSync(path.join(root, f)))
  .map((f) => f.slice('client/'.length));
if (srcFiles.length) {
  try {
    run(
      'pnpm',
      ['-s', 'exec', 'vitest', 'related', '--run', '--passWithNoTests', ...srcFiles],
      clientDir,
    );
  } catch (e) {
    fail('관련 테스트', e);
  }
}
delete state.failures;
if (process.env.TTADAK_AUTO_SKILLS === '0') {
  save(state);
  process.exit(0);
}

// ② 스킬 요청
const fingerprint = (files) => {
  const hash = createHash('sha1');
  for (const f of files) {
    const file = path.join(root, f);
    hash.update(f).update(existsSync(file) ? readFileSync(file) : '');
  }
  return hash.digest('hex');
};
const uiFiles = changed.filter((f) => /^client\/src\/.+(?<!\.test)\.(tsx|css)$/.test(f));
const deps = (json) => Object.keys({ ...json?.dependencies, ...json?.devDependencies });
let newDeps = [];
try {
  const before = deps(JSON.parse(git(['show', `${baseRef(root)}:client/package.json`], root)));
  const now = deps(JSON.parse(readFileSync(path.join(clientDir, 'package.json'), 'utf8')));
  newDeps = now.filter((d) => !before.includes(d));
} catch {
  // 첫 커밋 전이거나 package.json이 없으면 비교하지 않는다
}
const current = { all: fingerprint(changed), ui: fingerprint(uiFiles), deps: newDeps.join(',') };

// 요청한 다음 Stop이면 반영을 마친 것으로 본다. (stop_hook_active를 보내지 않는 도구도 있어 이 필드에 기대지 않는다)
if (state.pending) {
  save({ done: current });
  process.exit(0);
}
const done = state.done ?? {};
if (done.all === current.all) {
  save(state);
  process.exit(0);
}

const hasPlan =
  activePlans(root).length > 0 || changed.some((f) => f.startsWith('client/docs/plans/'));
const tasks = [];
if (changed.some((f) => f.startsWith('client/src/')) && !hasPlan)
  tasks.push('new-feature 스킬 절차대로 이번 작업의 plan을 client/docs/plans/에 남기세요.');
if (uiFiles.length && done.ui !== current.ui)
  tasks.push('verify-ui 스킬로 바뀐 화면을 브라우저에서 확인하세요.');
if (newDeps.length && done.deps !== current.deps)
  tasks.push(`새 의존성(${newDeps.join(', ')})을 write-adr 스킬로 ADR에 기록하세요.`);
tasks.push('review-changes 스킬로 이번 변경을 독립 리뷰하고 지적을 반영하세요.');

save({ done, pending: true });
block(`검증 통과. 끝내기 전에 차례로 하세요.\n${tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}`);
