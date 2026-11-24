import type { AnyHandler } from 'msw';

/**
 * 모든 테스트에 기본으로 적용할 MSW 핸들러.
 * 테스트마다 다른 응답이 필요하면 테스트 안에서 `server.use(...)`로 덮어쓴다.
 */
export const handlers: AnyHandler[] = [];
