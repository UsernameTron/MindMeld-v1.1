import { runVerifySprint } from '../src/commands/verify-sprint';
jest.mock('fs');

describe('projectctl verify-sprint', () => {
  it('passes when all items complete', async () => {
    const fs = require('fs');
    fs.readFileSync.mockImplementation((file) => {
      if (file === 'current-sprint-item.md') return 'Button Card';
      if (file === 'PROJECT_STATUS.md') return '\u2705 Button\n\u2705 Card';
      return '';
    });
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runVerifySprint({});
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith('All sprint items complete');
    log.mockRestore();
  });
  it('fails and lists missing items in text', async () => {
    const fs = require('fs');
    fs.readFileSync.mockImplementation((file) => {
      if (file === 'current-sprint-item.md') return 'Button Card Select';
      if (file === 'PROJECT_STATUS.md') return '\u2705 Button\n\u2705 Card';
      return '';
    });
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runVerifySprint({});
    expect(code).toBe(1);
    expect(log).toHaveBeenCalledWith('Missing sprint items:');
    expect(log).toHaveBeenCalledWith('  - Select');
    log.mockRestore();
  });
  it('outputs JSON when --format json', async () => {
    const fs = require('fs');
    fs.readFileSync.mockImplementation((file) => {
      if (file === 'current-sprint-item.md') return 'Button Card Select';
      if (file === 'PROJECT_STATUS.md') return '\u2705 Button\n\u2705 Card';
      return '';
    });
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runVerifySprint({ format: 'json' });
    expect(code).toBe(1);
    expect(log).toHaveBeenCalledWith(
      JSON.stringify({ complete: false, missing: ['Select'] }, null, 2)
    );
    log.mockRestore();
  });
});
