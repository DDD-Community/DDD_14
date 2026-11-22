import { describe, expect, it } from 'vitest';

import { cn } from '@/shared/lib/cn';

describe('cn', () => {
  it('조건부 className을 합친다', () => {
    expect(cn('px-2', { hidden: false, 'py-1': true }, undefined)).toBe('px-2 py-1');
  });

  it('충돌하는 Tailwind 클래스는 뒤쪽 값을 남긴다', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4');
  });
});
