import fs from 'fs';
import { execSync } from 'child_process';

/**
 * Recalculate completion percentage and update PROJECT_STATUS.md.
 * @param {{ statusFile:string, criteriaFile:string, commit:boolean }} opts
 * @returns {number} exit code
 */
export async function runUpdateStatus({
  statusFile = 'PROJECT_STATUS.md',
  criteriaFile = 'COMPLETION_CRITERIA.md',
  commit = false,
}) {
  try {
    // 1. Read criteriaFile to count total items
    const criteria = fs.readFileSync(criteriaFile, 'utf-8')
      .split(/\r?\n/).filter(Boolean);
    const total = criteria.length;

    // 2. Read statusFile to count completed (lines ending with ✔)
    const status = fs.readFileSync(statusFile, 'utf-8')
      .split(/\r?\n/)
      .filter(Boolean);
    const done = status.filter(l => l.trim().endsWith('✔')).length;

    const percent = total === 0 ? 0 : Math.round((done / total) * 100);

    // 3. Inject or update a summary line at top of statusFile
    const header = `# Project Completion — ${done}/${total} (${percent}%)`;
    const body = status.filter(l => !l.startsWith('# Project Completion'));
    const updated = [header, '', ...body].join('\n');

    fs.writeFileSync(statusFile, updated, 'utf-8');

    // 4. Optionally commit the change
    if (commit) {
      execSync(`git add ${statusFile}`);
      execSync(`git commit -m "chore: update project status to ${percent}%"`);
    }

    return 0;
  } catch (err) {
    console.log(`Error: ${err.message}`);
    if (err.code === 'ENOENT') return 2;
    return 1;
  }
}
