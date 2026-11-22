import { setupServer } from 'msw/node';

import { handlers } from '@/test/handlers';

/** 테스트용 MSW 서버. 수명 주기는 `src/test/setup.ts`가 관리한다. */
export const server = setupServer(...handlers);
