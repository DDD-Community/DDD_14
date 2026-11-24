import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: import.meta.env.VITE_APP_ENV === 'prod' ? 1 : 0,
      refetchOnWindowFocus: import.meta.env.VITE_APP_ENV === 'prod',
    },
    mutations: {
      retry: 0,
    },
  },
});
