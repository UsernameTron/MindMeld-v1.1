MindMeld Claude Context Management System
This system automatically keeps Claude informed about critical changes to your repository, ensuring it always has the most up-to-date understanding of your codebase without requiring manual file uploads.
How It Works
When you push changes to critical files in your repository, a GitHub Action automatically:

Extracts the content of the most important files
Formats them into a structured Markdown document
Saves this document in a .claude directory
Commits and pushes the updated context file

This ensures Claude always has access to the latest version of key files when you interact with it.
Installation Instructions
Step 1: Create Required Directories
First, create the necessary directories for our scripts:
bashmkdir -p .github/scripts
mkdir -p .claude
Step 2: Add the GitHub Action Workflow
Copy the claude-context-updater.yml file to .github/workflows/:
bash# Create the workflows directory if it doesn't exist
mkdir -p .github/workflows/

# Copy the workflow file
cp claude-context-updater.yml .github/workflows/
Step 3: Add the Python Script
Copy the generate_claude_context.py script to .github/scripts/:
bash# Copy the script file
cp generate_claude_context.py .github/scripts/

# Make it executable
chmod +x .github/scripts/generate_claude_context.py
Step 4: Create Initial Context File
Generate the initial context file manually:
bashpython .github/scripts/generate_claude_context.py
Step 5: Commit and Push
Add everything to Git and push:
bashgit add .github/workflows/claude-context-updater.yml
git add .github/scripts/generate_claude_context.py
git add .claude/context.md
git commit -m "Add Claude context management system"
git push
Customization
You can customize which files are monitored by editing:

The paths section in .github/workflows/claude-context-updater.yml
The CRITICAL_FILES list in .github/scripts/generate_claude_context.py

The script automatically detects file types based on extensions and formats them appropriately.
Working with Claude
When working with Claude, you can refer to the context file to ensure it has access to the latest codebase information:
Please refer to the context file in the .claude directory for information about the current state of the repository.
Claude will have access to this file and can use it to provide more accurate and contextually relevant assistance.
Troubleshooting
If the context file isn't updating:

Check the GitHub Actions tab to see if the workflow is running successfully
Ensure the files you modified are in the monitored list
Verify permissions for the GitHub Action to push changes

Limitations

The context file has a size limit (token limit for Claude)
Binary files and large files may need to be excluded
The system only updates when changes are pushed to the main branch
