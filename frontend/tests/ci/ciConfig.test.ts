import { readFileSync } from 'node:fs'
import { load } from 'js-yaml'
import { describe, it, expect } from 'vitest'

const ciPath = '/Users/cpconnor/projects/mindmeld-fresh/.github/workflows/ci.yml'

describe('Phase 4 CI/CD Configuration', () => {
  let config: any

  beforeAll(() => {
    const raw = readFileSync(ciPath, 'utf8')
    config = load(raw)
  })

  it('defines all required jobs', () => {
    const jobs = config.jobs
    expect(jobs).toHaveProperty('lint-format-type')
    expect(jobs).toHaveProperty('test')
    expect(jobs).toHaveProperty('build')
    expect(jobs).toHaveProperty('preview-deploy')
  })

  it('caches node_modules via setup-node', () => {
    const lintSteps = config.jobs['lint-format-type'].steps
    const setupNode = lintSteps.find((s: any) => s.uses?.includes('actions/setup-node'))
    expect(setupNode).toBeDefined()
    expect(setupNode.with.cache).toBe('npm')
  })

  it('enforces coverage thresholds in test job', () => {
    const testSteps = config.jobs.test.steps.map((s: any) => s.run || '')
    const hasCoverageCheck = testSteps.some((r: string) =>
      r.includes('if (( $(echo "$LINE_COVERAGE < 80"')
    )
    expect(hasCoverageCheck).toBe(true)
  })

  it('deploys preview only on pull_request', () => {
    const preview = config.jobs['preview-deploy']
    expect(config.on.pull_request.branches).toContain('main')
    expect(preview.if).toMatch(/github\.event_name == 'pull_request'/)
  })
})
// Removed invalid YAML and GitHub Actions config below. This file should only contain TypeScript test code.
