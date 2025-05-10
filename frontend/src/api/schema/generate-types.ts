import { exec } from 'child_process';
import path from 'path';
import fs from 'fs/promises';

async function generateTypes() {
  try {
    const schemaPath = path.resolve(__dirname, 'openapi.yaml');
    const outputPath = path.resolve(__dirname, 'generated');

    // Ensure output directory exists
    await fs.mkdir(outputPath, { recursive: true });

    console.log('Generating TypeScript interfaces from OpenAPI schema...');

    // Generate types using openapi-typescript
    exec(
      `npx openapi-typescript ${schemaPath} --output ${path.join(outputPath, 'api-types.ts')}`,
      (error, stdout, stderr) => {
        if (error) {
          console.error(`❌ Error: ${error.message}`);
          return;
        }
        if (stderr) {
          console.error(`⚠️ Warning: ${stderr}`);
        }
        console.log(`✅ TypeScript interfaces generated at ${path.join(outputPath, 'api-types.ts')}`);
        console.log(stdout);
      }
    );
  } catch (error) {
    console.error('❌ Error generating TypeScript interfaces:', error);
    throw error;
  }
}

generateTypes();
