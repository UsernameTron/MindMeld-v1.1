# MindMeld Project Tracking System

This project uses a comprehensive tracking system to ensure all implementation progress is transparent, objective, and up-to-date.

## Key Files

- `PROJECT_STATUS.md`: The single source of truth for implementation status. Updated with every significant change.
- `COMPLETION_CRITERIA.md`: Defines what "complete" means for any component or service.
- `push.sh`: Enhanced commit script that enforces status updates and summarizes project progress.

## Workflow Requirements

1. Update `PROJECT_STATUS.md` whenever a component status changes.
2. Follow the criteria in `COMPLETION_CRITERIA.md` strictly when marking components as complete.
3. Keep the "Last Updated" date current in the status file.
4. Make updating project status a required part of the development workflow.
5. Include status updates in pull request descriptions.

## How to Use

- Before every commit, run `./scripts/push.sh` to:
  - Update the status file's timestamp
  - Warn if the status file is out of date
  - Summarize project completion percentage
- Review the status and criteria files regularly to ensure accuracy.

## Why This Matters

This system prevents confusion, ensures accountability, and provides a clear, objective view of project progress for all stakeholders.
