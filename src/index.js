#!/usr/bin/env node
import { Command } from 'commander';
import { runReportFailures } from './commands/report-failures';
import { runVerifySprint } from './commands/verify-sprint';
import { runStatus } from './commands/status';
import { runUpdateStatus } from './commands/update-status';

const program = new Command();
program
  .name('projectctl')
  .description('CLI for project tracking commands')
  .version('0.1.0');

program
  .command('report-failures')
  .description('List GH Actions failures for a workflow')
  .requiredOption('--workflow <name>', 'workflow filename')
  .requiredOption('--branch <name>', 'branch to inspect')
  .option('--status <state>', 'run status', 'failure')
  .option('--since <period>', 'only since (e.g. 24h)')
  .option('--format <fmt>', 'output format: text|json', 'text')
  .action(async (opts) => {
    const code = await runReportFailures(opts);
    process.exit(code);
  });

program
  .command('verify-sprint')
  .description('Verify sprint completion')
  .option('--sprint-file <path>', 'sprint file', 'current-sprint-item.md')
  .option('--status-file <path>', 'status file', 'PROJECT_STATUS.md')
  .option('--format <fmt>', 'output format: text|json', 'text')
  .action(async (opts) => {
    const code = await runVerifySprint(opts);
    process.exit(code);
  });

program
  .command('next-action')
  .description('Show next high-priority incomplete item from status file')
  .option('--status-file <path>', 'status file', 'PROJECT_STATUS.md')
  .option('--format <fmt>', 'output format: text|json', 'text')
  .action(async (opts) => {
    const { runNextAction } = await import('./commands/next-action.js');
    const code = await runNextAction(opts);
    process.exit(code);
  });

program
  .command('status')
  .description('Show overall completion percentage')
  .option('--status-file <path>', 'status file', 'PROJECT_STATUS.md')
  .option('--format <fmt>', 'output format: text|json', 'text')
  .action(async (opts) => {
    const code = await runStatus(opts);
    process.exit(code);
  });

program
  .command('update-status')
  .description('Recalculate and update project completion in PROJECT_STATUS.md')
  .option('--status-file <path>', 'status file', 'PROJECT_STATUS.md')
  .option('--criteria-file <path>', 'criteria file', 'COMPLETION_CRITERIA.md')
  .option('--commit', 'commit the update', false)
  .action(async (opts) => {
    const code = await runUpdateStatus(opts);
    process.exit(code);
  });

program.parse(process.argv);
