import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import { HomePage } from '@/pages/home/HomePage';
import { queryClient } from '@/shared/lib/query-client';

/** 앱 루트. 전역 Provider를 두고 페이지를 렌더링한다. */
export const App = () => (
  <QueryClientProvider client={queryClient}>
    <HomePage />
    <ReactQueryDevtools initialIsOpen={false} />
  </QueryClientProvider>
);
