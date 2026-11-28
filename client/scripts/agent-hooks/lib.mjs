// 훅 공용 유틸 (Claude Code · Codex)
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';

/** 셸을 거치지 않고 실행한다. 파일명이 인자로 그대로 전달된다. */
export const run = (cmd, args, cwd) =>
  execFileSync(cmd, args, { cwd, encoding: 'utf8', stdio: 'pipe' });

/** 한글 파일명이 따옴표로 감싸지지 않게 core.quotePath=false로 실행한다. */
export const git = (args, cwd) => run('git', ['-c', 'core.quotePath=false', ...args], cwd);

export const repoRoot = (cwd) => git(['rev-parse', '--show-toplevel'], cwd ?? process.cwd()).trim();

export const readInput = () => {
  try {
    return JSON.parse(readFileSync(0, 'utf8') || '{}');
  } catch {
    return {};
  }
};

export const block = (reason) => {
  process.stderr.write(reason);
  process.exit(2);
};

/** 실패한 명령의 출력. 출력이 없으면(명령을 못 찾는 경우 등) 오류 메시지를 쓴다. */
export const outputOf = (e) => `${e.stdout ?? ''}${e.stderr ?? ''}`.trim() || String(e.message);

export const tail = (text, lines = 40) => text.split('\n').slice(-lines).join('\n');

const EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904';

/** 비교 기준. 첫 커밋 전이면 빈 트리와 비교한다. */
export const baseRef = (root) => {
  try {
    git(['rev-parse', '--verify', '--quiet', 'HEAD'], root);
    return 'HEAD';
  } catch {
    return EMPTY_TREE;
  }
};

/** client 아래에서 바뀐 파일: 추적 중인 파일의 diff + 새 파일 */
export const changedFiles = (root) => {
  const split = (out) => out.split('\0').filter(Boolean);
  return [
    ...new Set([
      ...split(git(['diff', baseRef(root), '--name-only', '-z', '--', 'client'], root)),
      ...split(git(['ls-files', '--others', '--exclude-standard', '-z', '--', 'client'], root)),
    ]),
  ];
};

/** 스킬 안내: 이름과 SKILL.md 경로. 스킬을 자동으로 찾지 못하는 도구도 경로를 읽고 따를 수 있다. */
export const skill = (name) => `${name} 스킬(client/.agents/skills/${name}/SKILL.md)`;

/** 상태가 "진행 중"인 plan 파일 목록 */
export const activePlans = (root) => {
  const dir = path.join(root, 'client/docs/plans');
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.md'))
    .filter((f) => /^- 상태:\s*진행 중\s*$/m.test(readFileSync(path.join(dir, f), 'utf8')))
    .map((f) => `client/docs/plans/${f}`);
};
