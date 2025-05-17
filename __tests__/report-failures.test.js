import { runReportFailures } from '../src/commands/report-failures';
import execa from 'execa';

jest.mock('execa');

describe('projectctl report-failures', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('exits 0 and prints "No failures" when there are none', async () => {
    execa.mockResolvedValue({ stdout: '[]' });
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runReportFailures({
      workflow: 'ci-status.yml',
      branch: 'main',
      status: 'failure',
      since: null,
      format: 'text',
    });
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith('No failures found for workflow ci-status.yml');
    log.mockRestore();
  });

  it('groups and prints failures in text format and exits 1', async () => {
    const sample = JSON.stringify([
      { name: 'job-a', conclusion: 'failure', htmlUrl: 'url1' },
      { name: 'job-b', conclusion: 'failure', htmlUrl: 'url2' },
      { name: 'job-a', conclusion: 'failure', htmlUrl: 'url3' },
    ]);
    execa.mockResolvedValue({ stdout: sample });
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runReportFailures({
      workflow: 'ci-status.yml',
      branch: 'main',
      status: 'failure',
      since: '24h',
      format: 'text',
    });
    expect(log).toHaveBeenCalledWith('ci-status.yml (3 failures)');
    expect(log).toHaveBeenCalledWith('  • job-a: 2');
    expect(log).toHaveBeenCalledWith('  • job-b: 1');
    expect(code).toBe(1);
    log.mockRestore();
  });

  it('outputs JSON when requested and exits 1', async () => {
    const sample = JSON.stringify([
      { name: 'job-a', conclusion: 'failure', htmlUrl: 'url1' },
    ]);
    execa.mockResolvedValue({ stdout: sample });
    const log = jest.spyOn(console, 'log').mockImplementation();
    const code = await runReportFailures({
      workflow: 'ci-status.yml',
      branch: 'main',
      status: 'failure',
      since: null,
      format: 'json',
    });
    const expected = {
      'ci-status.yml': {
        total: 1,
        byJob: { 'job-a': 1 },
      },
    };
    expect(log).toHaveBeenCalledWith(JSON.stringify(expected, null, 2));
    expect(code).toBe(1);
    log.mockRestore();
  });

  it('handles CLI/parsing errors and exits 2', async () => {
    execa.mockRejectedValue(new Error('gh CLI not found'));
    const code = await runReportFailures({
      workflow: 'ci-status.yml',
      branch: 'main',
      status: 'failure',
      since: null,
      format: 'text',
    });
    expect(code).toBe(2);
  });
});
