// app/services/promptService.js

// In-memory prompt registry (replace with DB logic as needed)
const promptDB = new Map()

/**
 * Registers a single prompt template into the service registry.
 * @param {Object} promptJson - JSON object representing the prompt template
 * @returns {Promise<void>}
 */
async function registerPrompt(promptJson) {
  const { title: name, description: template, ...metadata } = promptJson
  if (!name || !template) {
    throw new Error("Prompt must include at least a 'title' and 'description' field.")
  }
  // Store in in-memory registry; replace with DB insert if needed
  promptDB.set(name, { template, metadata })
  return true
}

module.exports = { registerPrompt }
