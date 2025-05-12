import { describe, it, expect } from 'vitest';
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
});

describe('UserSchema validation', () => {
  it('should reject invalid payloads', () => {
    const invalid = { id: 123, email: 'not-an-email', name: 42 };
    const result = UserSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});
