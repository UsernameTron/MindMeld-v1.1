# Claude 3.7 API Tool Compatibility Update

This document summarizes the changes made to update tool definitions for compatibility with the Claude 3.7 API.

## Issues Fixed

The Claude 3.7 API requires specific tool types rather than the generic `"type": "function"` used in earlier versions:
- Tools should use `"type": "custom"` for general purpose tools
- Special tools should use their specific types:
  - `execute_bash` → `"type": "bash_20250124"`
  - `search_web` → `"type": "web_search_20250305"`
  - `edit_text` → `"type": "text_editor_20250429"`
  - `browse_web` → `"type": "web_browser_20250428"`
  - `retrieve_content` → `"type": "retrieval_20250301"`

## Files Created

1. **scripts/update_agent_tools.py**
   - Automatically updates tool definitions in agent files
   - Converts `"type": "function"` to appropriate types based on tool name
   - Creates backups of files before updating them
   - Handles both double and single quote styles
   - Recursively discovers all agent directories

2. **scripts/verify_api_tools.py**
   - Verifies API tool compatibility
   - Checks for API health and configuration
   - Tests a simple agent call
   - Verifies no outdated tool definitions remain in the codebase
   - Supports `--skip-api-check` option for offline validation

## Files Updated

1. **packages/agents/claude_agents/agents/planner.py**
   - Updated tool definitions with correct type values
   - Backup created at `planner.py.bak`

2. **packages/agents/claude_agents/agents/critic.py**
   - Updated tool definitions with correct type values
   - Backup created at `critic.py.bak`

## Build System Integration

- Added `update-tools` and `verify-api` targets to the Makefile
- Updated documentation in `SCRIPTS_OVERVIEW.md`

## Testing

- Created a test agent with outdated tool definitions
- Verified the scripts correctly identify and fix the issues
- Confirmed all existing agent files have been properly updated

## Next Steps

1. Deploy the updated agents to production
2. Run comprehensive integration tests with the Claude 3.7 API
3. Consider adding the verification step to CI/CD pipelines
4. Update developer documentation regarding tool definitions
