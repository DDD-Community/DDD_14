import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';

import { api } from '@/shared/lib/api';
import { server } from '@/test/server';

describe('api', () => {
  it('VITE_API_BASE_URL을 기준으로 요청한다', async () => {
    server.use(
      http.get(`${import.meta.env.VITE_API_BASE_URL}/health`, () =>
        HttpResponse.json({ status: 'ok' }),
      ),
    );

    const { data } = await api.get<{ status: string }>('/health');

    expect(data).toEqual({ status: 'ok' });
  });
});
