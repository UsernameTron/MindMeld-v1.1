import execa from 'execa';

/**
 * Run the report-failures logic for projectctl.
 * @param {object} options
 * @returns {Promise<number>} exit code
 */
export async function runReportFailures(options) {
  const workflow = options.workflow;
  const branch = options.branch;
  const status = options.status;
  const since = options.since;
  const format = options.format;
  let ghArgs = [
    'run', 'list',
    '--workflow', workflow,
    '--branch', branch,
    '--status', status,
    '--json', 'conclusion,name,htmlUrl'
  ];
  if (since) ghArgs.push('--since', since);
  let result;
  try {
    result = await execa('gh', ghArgs);
  } catch (err) {
    return 2;
  }
  let runs;
  try {
    runs = JSON.parse(result.stdout);
  } catch (e) {
    return 2;
  }
  if (!Array.isArray(runs) || runs.length === 0) {
    if (format === 'json') {
      console.log(JSON.stringify({ [workflow]: { total: 0, byJob: {} } }, null, 2));
    } else {
      console.log(`No failures found for workflow ${workflow}`);
    }
    return 0;
  }
  // Group by job name
  const byJob = {};
  let total = 0;
  for (const run of runs) {
    const job = run.name || 'unknown';
    byJob[job] = (byJob[job] || 0) + 1;
    total++;
  }
  if (format === 'json') {
    console.log(JSON.stringify({ [workflow]: { total, byJob } }, null, 2));
  } else {
    console.log(`${workflow} (${total} failures)`);
    for (const [job, count] of Object.entries(byJob)) {
      console.log(`  • ${job}: ${count}`);
    }
  }
  return total > 0 ? 1 : 0;
}
