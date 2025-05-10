const fs = require('fs')
const path = require('path')
const { registerPrompt } = require('../app/services/promptService')

async function main() {
  const files = process.argv.slice(2)

  for (const file of files) {
    try {
      const json = JSON.parse(fs.readFileSync(file, 'utf8'))

      if (!json.title || !json.description) {
        console.warn(`⚠ Skipping ${path.basename(file)}: missing 'title' or 'description'`)
        continue
      }

      await registerPrompt(json)
      console.log(`✓ loaded ${path.basename(file)}`)
    } catch (err) {
      console.error(`✗ Failed to load ${file}: ${err.message}`)
    }
  }
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
