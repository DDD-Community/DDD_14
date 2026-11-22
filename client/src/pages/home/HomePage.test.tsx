import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { HomePage } from '@/pages/home/HomePage';

describe('HomePage', () => {
  it('서비스 이름을 보여 준다', () => {
    render(<HomePage />);

    expect(screen.getByRole('heading', { name: '타닥' })).toBeInTheDocument();
  });
});
