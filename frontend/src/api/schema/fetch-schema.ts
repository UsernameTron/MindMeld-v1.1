import SwaggerParser from '@apidevtools/swagger-parser';
import fs from 'fs/promises';
import path from 'path';
import dotenv from 'dotenv';

// Load .env.local if present
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function fetchAndValidateSchema() {
  try {
    // Prefer env variable, fallback to local openapi.yaml
    const apiUrl = process.env.NEXT_PUBLIC_API_SCHEMA_URL || path.resolve(__dirname, 'openapi.yaml');
    console.log(`Fetching OpenAPI schema from: ${apiUrl}`);
    const api = await SwaggerParser.validate(apiUrl);

    // Always output to frontend/src/api/schema/openapi.json
    const outputPath = path.resolve(process.cwd(), 'src/api/schema/openapi.json');
    await fs.writeFile(outputPath, JSON.stringify(api, null, 2));

    console.log(`✅ OpenAPI schema validated and saved to ${outputPath}`);
    return api;
  } catch (error) {
    console.error('❌ Error fetching or validating OpenAPI schema:', error);
    throw error;
  }
}

fetchAndValidateSchema();
