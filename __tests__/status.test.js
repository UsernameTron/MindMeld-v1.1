import { runStatus } from '../src/commands/status';
import fs from 'fs';
jest.mock('fs');

describe('projectctl status', () => {
  beforeEach(() => jest.resetAllMocks());

  it('prints progress in text format', async () => {
    const data = ['a ✔','b','c ✔','d'].join('\n');
    fs.readFileSync.mockReturnValue(data);
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runStatus({ format: 'text' });
    expect(log).toHaveBeenCalledWith('Completed: 2/4 (50%)');
    expect(code).toBe(0);
    log.mockRestore();
  });

  it('prints JSON when --format json', async () => {
    const data = ['x ✔','y ✔','z'].join('\n');
    fs.readFileSync.mockReturnValue(data);
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runStatus({ format: 'json' });
    expect(log).toHaveBeenCalledWith(
      JSON.stringify({ total:3, done:2, percent:67 }, null, 2)
    );
    expect(code).toBe(0);
    log.mockRestore();
  });

  it('handles missing file and exits 2', async () => {
    const err = new Error('not found'); err.code = 'ENOENT';
    fs.readFileSync.mockImplementation(() => { throw err; });
    const code = await runStatus({});
    expect(code).toBe(2);
  });

  it('handles generic parse error and exits 1', async () => {
    const err = new Error('bad'); err.code = 'EOTHER';
    fs.readFileSync.mockImplementation(() => { throw err; });
    const code = await runStatus({});
    expect(code).toBe(1);
  });
});
