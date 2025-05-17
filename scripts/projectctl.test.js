const { execSync } = require('child_process');

describe('projectctl CLI', () => {
  it('should show help for no args', () => {
    try {
      execSync('node scripts/projectctl.js', { stdio: 'pipe' });
    } catch (e) {
      expect(e.status).toBe(1);
      expect(e.stdout.toString()).toMatch(/You need a command/);
    }
  });

  it('should fail for unknown command', () => {
    try {
      execSync('node scripts/projectctl.js unknown', { stdio: 'pipe' });
    } catch (e) {
      expect(e.status).toBe(1);
      expect(e.stdout.toString()).toMatch(/Unknown command/);
    }
  });

  it('should exit 1 for stubbed commands', () => {
    ['report-failures', 'verify-sprint', 'next-action', 'status'].forEach(cmd => {
      try {
        execSync(`node scripts/projectctl.js ${cmd}`, { stdio: 'pipe' });
      } catch (e) {
        expect(e.status).toBe(1); // stub returns 1 for unimplemented commands
        expect(e.stdout.toString()).toMatch(/Not yet implemented/);
      }
    });
  });
});
