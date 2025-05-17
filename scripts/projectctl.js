#!/usr/bin/env node

// projectctl: Unified CLI for project board, sprint, and workflow management
// Usage: projectctl <command> [options]

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const commands = {
  'report-failures': {
    desc: 'Summarize recent GitHub Actions workflow failures',
    builder: (yargs) => yargs
      .option('workflow', {
        type: 'string',
        describe: 'Workflow filename to filter (e.g. ci-status.yml)',
        demandOption: true,
      })
      .option('branch', {
        type: 'string',
        describe: 'Branch to filter (e.g. main)',
        demandOption: true,
      })
      .option('status', {
        type: 'string',
        describe: 'Workflow run status (e.g. failure)',
        default: 'failure',
      })
      .option('since', {
        type: 'string',
        describe: 'Only include runs from the last Xh or Xd (e.g. 24h, 7d)',
      })
      .option('format', {
        type: 'string',
        describe: 'Output format (json, text)',
        default: 'text',
      }),
    handler: async (options) => {
      // Use the extracted logic for testability
      const { runReportFailures } = require('../src/commands/report-failures');
      const code = await runReportFailures(options);
      process.exit(code);
    },
  },
  'verify-sprint': {
    desc: 'Check if all sprint components are complete',
    builder: (yargs) => yargs
      .option('sprint-file', {
        type: 'string',
        describe: 'Path to sprint file',
        default: 'current-sprint-item.md',
      })
      .option('status-file', {
        type: 'string',
        describe: 'Path to project status file',
        default: 'PROJECT_STATUS.md',
      })
      .option('format', {
        type: 'string',
        describe: 'Output format (json, text)',
        default: 'text',
      }),
    handler: async (options) => {
      const { runVerifySprint } = require('../src/commands/verify-sprint');
      const code = await runVerifySprint({
        sprintFile: options['sprint-file'],
        statusFile: options['status-file'],
        format: options.format,
      });
      process.exit(code);
    },
  },
  'next-action': {
    desc: 'Determine next priority action',
    handler: () => {
      // Placeholder: migrate next-action.sh logic here
      console.log('Not yet implemented: next-action');
      process.exit(2);
    },
  },
  'status': {
    desc: 'Show project status and completion %',
    handler: () => {
      // Placeholder: migrate push.sh status logic here
      console.log('Not yet implemented: status');
      process.exit(2);
    },
  },
  'test': {
    desc: 'Run projectctl unit tests',
    handler: () => {
      try {
        execSync('npm test', { stdio: 'inherit' });
      } catch (e) {
        process.exit(1);
      }
    },
  },
};

const y = yargs(hideBin(process.argv))
  .scriptName('projectctl')
  .usage('$0 <cmd> [args]')
  .help(false)
  .version(false)
  .option('help', {
    alias: 'h',
    type: 'boolean',
    describe: 'Show help',
  })
  .fail((msg, err, yargs) => {
    const output = msg || (err && err.message) || '';
    if (output) console.log(output);
    console.log(yargs.help());
    process.exit(1);
  })
  .command('report-failures', commands['report-failures'].desc, commands['report-failures'].builder, commands['report-failures'].handler)
  .command('verify-sprint', commands['verify-sprint'].desc, () => {}, commands['verify-sprint'].handler)
  .command('next-action', commands['next-action'].desc, () => {}, commands['next-action'].handler)
  .command('status', commands['status'].desc, () => {}, commands['status'].handler)
  .command('test', commands['test'].desc, () => {}, commands['test'].handler)
  .option('format', { type: 'string', describe: 'Output format (json, text)', default: 'text' })
  .option('dry-run', { type: 'boolean', describe: 'Show what would be done, but don\'t make changes' })
  .demandCommand(1, 'You need a command')
  .help();

const argv = y.parse();

if (argv.help) {
  console.log(y.getHelp());
  process.exit(0);
}
