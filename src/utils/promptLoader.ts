import fs from 'fs';
import path from 'path';
import { PromptTemplate, isAdvancedTemplate } from '../../types/promptTypes';
import { promptService } from '../services/promptService';
import { markdownToTemplate } from './templateConverter';

// Default paths to template directories
const PROMPTS_DIR = path.resolve(process.cwd(), 'src/prompts');
const MD_DIR = path.join(PROMPTS_DIR, 'markdown');
const JSON_DIR = path.join(PROMPTS_DIR, 'json');

/**
 * Load all prompt templates from the filesystem
 */
export async function loadPrompts(basePath?: string): Promise<void> {
  const baseDir = basePath || PROMPTS_DIR;
  const mdDir = path.join(baseDir, 'markdown');
  const jsonDir = path.join(baseDir, 'json');

  try {
    // Create directories if they don't exist
    ensureDirectories([baseDir, mdDir, jsonDir]);

    // Load JSON templates (including basic templates)
    const jsonFiles = fs.readdirSync(jsonDir).filter(file => file.endsWith('.json'));
    for (const file of jsonFiles) {
      try {
        const filePath = path.join(jsonDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        const template = JSON.parse(content) as PromptTemplate;
        validateAndRegisterTemplate(template, file);
      } catch (error) {
        console.error(`Error loading template file ${file}:`, error);
      }
    }

    // Load Markdown templates
    const mdFiles = fs.readdirSync(mdDir).filter(file => file.endsWith('.md'));
    for (const file of mdFiles) {
      try {
        const filePath = path.join(mdDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        const template = markdownToTemplate(content);
        validateAndRegisterTemplate(template, file);
      } catch (error) {
        console.error(`Error loading markdown template file ${file}:`, error);
      }
    }

    console.log(`Loaded ${promptService.getAllTemplates().length} templates in total`);
  } catch (error) {
    console.error('Error loading prompts:', error);
  }
}

/**
 * Helper to ensure directories exist
 */
function ensureDirectories(dirs: string[]): void {
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }
}

/**
 * Validate and register a template
 */
function validateAndRegisterTemplate(template: PromptTemplate, filename: string): void {
  // Validate basic template
  if (!isAdvancedTemplate(template)) {
    if (!template.id || !template.title) {
      console.warn(`Skipping invalid template in ${filename}: missing required fields`);
      return;
    }
  }
  // Validate advanced template
  if (isAdvancedTemplate(template)) {
    if (!template.parameters || !template.formatFnTemplate) {
      console.warn(`Skipping invalid advanced template in ${filename}: missing required fields`);
      return;
    }
  }
  // Feature flag respected in registerTemplate
  promptService.registerTemplate(template);
  console.log(`Loaded template: ${template.title}`);
}
