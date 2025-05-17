import { runNextAction } from '../src/commands/next-action';
import fs from 'fs';
jest.mock('fs');

describe('projectctl next-action', () => {
  it('reports all complete when no open items', async () => {
    fs.readFileSync.mockReturnValue(['task1 ✔','task2 ✔'].join('\n'));
    const log = jest.spyOn(console,'log').mockImplementation();
    const code = await runNextAction({ format: 'text' });
    expect(log).toHaveBeenCalledWith('All items complete');
    expect(code).toBe(0);
    log.mockRestore();
  });

  it('prints next incomplete item in text', async () => {
    fs.readFileSync.mockReturnValue(['a ✔','b','c ✔'].join('\n'));
    const log = jest.spyOn(console,'log').mockImplementation();
    const code = await runNextAction({ format: 'text' });
    expect(log).toHaveBeenCalledWith('Next action: b');
    expect(code).toBe(1);
    log.mockRestore();
  });

  it('prints JSON when format=json', async () => {
    fs.readFileSync.mockReturnValue(['x','y ✔'].join('\n'));
    const log = jest.spyOn(console,'log').mockImplementation();
    const code = await runNextAction({ format: 'json' });
    expect(log).toHaveBeenCalledWith(JSON.stringify({ next:'x' },null,2));
    expect(code).toBe(1);
    log.mockRestore();
  });

  it('handles file errors and exits 2', async () => {
    fs.readFileSync.mockImplementation(()=>{ throw new Error('fail') });
    const code = await runNextAction({});
    expect(code).toBe(2);
  });
});
