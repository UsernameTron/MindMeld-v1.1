import { baseTokens } from './tokens/index.js';

export const tailwindTheme = {
  extend: {
    colors: {
      // Base colors
      primary: baseTokens.colors.primary,
      neutral: baseTokens.colors.neutral,
      // Feature category colors
      analyze: baseTokens.colors.analyze,
      chat: baseTokens.colors.chat,
      rewrite: baseTokens.colors.rewrite,
      persona: baseTokens.colors.persona,
      // Status colors
      success: baseTokens.colors.success,
      warning: baseTokens.colors.warning,
      error: baseTokens.colors.error,
    },
    fontFamily: baseTokens.typography.fontFamily,
    fontSize: {
      xs: baseTokens.typography.fontSize.xs,
      sm: baseTokens.typography.fontSize.sm,
      base: baseTokens.typography.fontSize.base,
      lg: baseTokens.typography.fontSize.lg,
      xl: baseTokens.typography.fontSize.xl,
      '2xl': baseTokens.typography.fontSize['2xl'],
      '3xl': baseTokens.typography.fontSize['3xl'],
      '4xl': baseTokens.typography.fontSize['4xl'],
      '5xl': baseTokens.typography.fontSize['5xl'],
    },
    fontWeight: baseTokens.typography.fontWeight,
    lineHeight: baseTokens.typography.lineHeight,
    borderRadius: baseTokens.borderRadius,
    boxShadow: baseTokens.boxShadow,
    animation: {
      'spin-slow': 'spin 2s linear infinite',
      ping: 'ping 1s cubic-bezier(0, 0, 0.2, 1) infinite',
      pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      bounce: 'bounce 1s infinite',
    },
    keyframes: {
      spin: {
        to: { transform: 'rotate(360deg)' },
      },
      ping: {
        '75%, 100%': { transform: 'scale(2)', opacity: '0' },
      },
      pulse: {
        '50%': { opacity: '.5' },
      },
      bounce: {
        '0%, 100%': {
          transform: 'translateY(-25%)',
          animationTimingFunction: 'cubic-bezier(0.8,0,1,1)',
        },
        '50%': {
          transform: 'none',
          animationTimingFunction: 'cubic-bezier(0,0,0.2,1)',
        },
      },
    },
  },
};
