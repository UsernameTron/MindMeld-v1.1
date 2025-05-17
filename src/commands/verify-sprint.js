import fs from 'fs';

/**
 * Checks if all sprint items are complete.
 * @param {object} opts
 * @param {string} opts.sprintFile
 * @param {string} opts.statusFile
 * @param {string} opts.format
 * @returns {Promise<number>} exit code
 */
export async function runVerifySprint({ sprintFile = 'current-sprint-item.md', statusFile = 'PROJECT_STATUS.md', format = 'text' }) {
  // 1. Read sprintFile: extract list of required component IDs
  let required = [];
  try {
    const sprintText = fs.readFileSync(sprintFile, 'utf8');
    required = sprintText.match(/\b[A-Za-z0-9_\-]+\b/g) || [];
    required = Array.from(new Set(required));
  } catch (e) {
    console.log(`Error reading sprint file: ${sprintFile}`);
    return 2;
  }
  // 2. Read statusFile: parse which components are marked complete
  let complete = [];
  try {
    const statusText = fs.readFileSync(statusFile, 'utf8');
    // Assume completed components are marked with a checkmark (✅) and a component name
    complete = (statusText.match(/\u2705\s*([A-Za-z0-9_\-]+)/g) || []).map(s => s.replace(/\u2705\s*/, ''));
  } catch (e) {
    console.log(`Error reading status file: ${statusFile}`);
    return 2;
  }
  // 3. Compare sets: missing = required - complete
  const missing = required.filter(item => !complete.includes(item));
  // 4. Output
  if (missing.length === 0) {
    if (format === 'json') {
      console.log(JSON.stringify({ complete: true, missing: [] }, null, 2));
    } else {
      console.log('All sprint items complete');
    }
    return 0;
  } else {
    if (format === 'json') {
      console.log(JSON.stringify({ complete: false, missing }, null, 2));
    } else {
      console.log('Missing sprint items:');
      missing.forEach(item => console.log(`  - ${item}`));
    }
    return 1;
  }
}
