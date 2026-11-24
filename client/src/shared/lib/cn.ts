import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** 조건부 className을 합치고, 충돌하는 Tailwind 클래스는 뒤쪽 값을 남긴다. */
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
