import { describe, it, expect } from 'vitest'
import { registerPrompt } from '/app/services/promptService.js'

describe('registerPrompt', () => {
  it('should register a valid prompt', async () => {
    const mockPrompt = {
      title: "test-prompt",
      description: "Hello, {{name}}",
      metadata: { tags: ["demo"] }
    }

    const result = await registerPrompt(mockPrompt)
    expect(result).toBe(true)
  })

  it('should throw if title or description is missing', async () => {
    const invalidPrompt = { metadata: {} }
    await expect(registerPrompt(invalidPrompt)).rejects.toThrow()
  })
})
