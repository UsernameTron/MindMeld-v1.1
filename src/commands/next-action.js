import fs from 'fs';
/**
 * Determine next high-priority action based on your status file.
 * @param {{statusFile:string, format:string}} opts
 * @returns {number} exit code
 */
export async function runNextAction({ statusFile = 'PROJECT_STATUS.md', format = 'text' }) {
  try {
    const status = fs.readFileSync(statusFile, 'utf-8')
      .split(/\r?\n/)
      .map(l => l.trim())
      .filter(Boolean);
    // TODO: parse statuses, pick the first incomplete item from “now” or “next”
    const next = status.find(line => !line.endsWith('✔'));
    if (!next) {
      console.log('All items complete');
      return 0;
    }

    if (format === 'json') {
      console.log(JSON.stringify({ next }, null, 2));
    } else {
      console.log(`Next action: ${next}`);
    }
    return 1;
  } catch (err) {
    console.log(`Error: ${err.message}`);
    return 2;
  }
}
