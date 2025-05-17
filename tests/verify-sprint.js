import fs from 'fs';

/**
 * Verify sprint completion by comparing required vs. completed components.
 * @param {Object} options
 * @param {string} options.sprintFile - Path to sprint definition file (defaults: current-sprint-item.md)
 * @param {string} options.statusFile - Path to status file (defaults: PROJECT_STATUS.md)
 * @param {string} options.format - Output format: 'text' or 'json'
 * @returns {number} Exit code: 0 if all complete, 1 if missing items, 2 on error
 */
export async function runVerifySprint({ sprintFile = 'current-sprint-item.md', statusFile = 'PROJECT_STATUS.md', format = 'text' }) {
  try {
    // 1. Read sprintFile
    const sprintContent = fs.readFileSync(sprintFile, 'utf-8');
    const required = sprintContent
      .split(/\r?\n/)                // split lines
      .map(line => line.trim())
      .filter(Boolean);               // drop empty lines

    // 2. Read statusFile
    const statusContent = fs.readFileSync(statusFile, 'utf-8');
    const completed = statusContent
      .split(/\r?\n/)                // split lines
      .map(line => line.trim())
      .filter(line => line.endsWith('✔'))  // assume complete items marked with a check
      .map(line => line.replace(/\s*✔$/, ''));

    // 3. Compare sets
    const missing = required.filter(item => !completed.includes(item));

    // 4. Output
    if (missing.length === 0) {
      console.log('All sprint items complete');
      return 0;
    }

    if (format === 'json') {
      console.log(JSON.stringify({ missing }, null, 2));
    } else {
      console.log('Missing sprint items:');
      missing.forEach(item => console.log('  • ' + item));
    }

    return 1;
  } catch (err) {
    console.log('Error: ' + err.message);
    return 2;
  }
}
