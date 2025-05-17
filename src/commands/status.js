import fs from 'fs';

/**
 * Show overall project completion percentage from PROJECT_STATUS.md.
 * Exits 0 if status printed, 1 if parsing error, 2 on file error.
 * @param {{statusFile:string, format:string}} opts
 * @returns {number}
 */
export async function runStatus({ statusFile = 'PROJECT_STATUS.md', format = 'text' }) {
  try {
    const lines = fs.readFileSync(statusFile, 'utf-8')
      .split(/\r?\n/)
      .map(l => l.trim())
      .filter(Boolean);

    const total = lines.length;
    const done = lines.filter(l => l.endsWith('✔')).length;
    const percent = total === 0 ? 0 : Math.round((done / total) * 100);

    if (format === 'json') {
      console.log(JSON.stringify({ total, done, percent }, null, 2));
    } else {
      console.log(`Completed: ${done}/${total} (${percent}%)`);
    }
    return 0;
  } catch (err) {
    console.log(`Error: ${err.message}`);
    return err.code === 'ENOENT' ? 2 : 1;
  }
}
