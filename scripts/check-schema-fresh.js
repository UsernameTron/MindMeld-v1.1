import fs from 'fs';
import fetch from 'node-fetch';

(async () => {
  const remote = await fetch(process.env.NEXT_PUBLIC_API_SCHEMA_URL).then(r => r.text());
  const local  = fs.readFileSync('frontend/src/api/schema/openapi.json', 'utf8');
  if (remote !== local) {
    console.warn('⚠️ openapi.json is out of date with remote schema.');
    process.exitCode = 1;
  }
})();
