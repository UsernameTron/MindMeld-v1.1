import { runUpdateStatus } from '../src/commands/update-status';
import fs from 'fs';
import { execSync } from 'child_process';
jest.mock('fs');
jest.mock('child_process');

describe('projectctl update-status', () => {
  beforeEach(() => jest.resetAllMocks());

  it('injects header if not present', async () => {
    fs.readFileSync.mockImplementation((file) => {
      if (file === 'COMPLETION_CRITERIA.md') return 'A\nB\nC';
      if (file === 'PROJECT_STATUS.md') return 'A ✔\nB\nC ✔';
    });
    let written;
    fs.writeFileSync.mockImplementation((file, data) => { written = data; });
    const code = await runUpdateStatus({});
    expect(written.startsWith('# Project Completion — 2/3 (67%)')).toBe(true);
    expect(code).toBe(0);
  });

  it('overwrites old header if present', async () => {
    fs.readFileSync.mockImplementation((file) => {
      if (file === 'COMPLETION_CRITERIA.md') return 'A\nB';
      if (file === 'PROJECT_STATUS.md') return '# Project Completion — 1/2 (50%)\n\nA ✔\nB';
    });
    let written;
    fs.writeFileSync.mockImplementation((file, data) => { written = data; });
    const code = await runUpdateStatus({});
    expect(written.startsWith('# Project Completion — 1/2 (50%)')).toBe(true);
    expect(written.split('\n')[2]).toBe('A ✔');
    expect(code).toBe(0);
  });

  it('commits when --commit is set', async () => {
    fs.readFileSync.mockImplementation((file) => {
      if (file === 'COMPLETION_CRITERIA.md') return 'A\nB';
      if (file === 'PROJECT_STATUS.md') return 'A ✔\nB';
    });
    fs.writeFileSync.mockImplementation(() => {});
    execSync.mockImplementation(() => {});
    const code = await runUpdateStatus({ commit: true });
    expect(execSync).toHaveBeenCalledWith('git add PROJECT_STATUS.md');
    expect(execSync).toHaveBeenCalledWith(expect.stringContaining('git commit -m'));
    expect(code).toBe(0);
  });

  it('returns 2 on file not found', async () => {
    fs.readFileSync.mockImplementation(() => { const err = new Error('nope'); err.code = 'ENOENT'; throw err; });
    const code = await runUpdateStatus({});
    expect(code).toBe(2);
  });
});
