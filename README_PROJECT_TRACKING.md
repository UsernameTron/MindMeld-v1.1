# Project Tracking CLI Commands

## report-failures

```bash
projectctl report-failures \
  --workflow <workflow.yml> \
  --branch <branch> \
  [--status <state>] \
  [--since <period>] \
  [--format text|json]
```

Lists GitHub Actions failures for the specified workflow and branch.
Exit codes: 0 = no failures, 1 = failures found, 2 = CLI error.

## verify-sprint

```bash
projectctl verify-sprint \
  [--sprint-file <path>] \
  [--status-file <path>] \
  [--format text|json]
```

Checks that all items in the sprint file are marked complete in the status file.
Exit codes: 0 = all complete, 1 = missing items, 2 = error.

## next-action

```bash
projectctl next-action \
  [--status-file <path>] \
  [--format text|json]
```

Shows the next high-priority incomplete item from your status file.
Exit codes: 0 = all complete, 1 = next action found, 2 = error.

## status

```bash
projectctl status [--status-file <path>] [--format text|json]
```

Shows overall completion: number done, total, and percentage.
Exit codes: 0 = success, 1 = parse error, 2 = file error.

## update-status

```bash
projectctl update-status \
  [--status-file <path>] \
  [--criteria-file <path>] \
  [--commit]
```

Recalculates the project completion header in PROJECT_STATUS.md.
If --commit is passed, stages and commits the change.
Exit codes: 0 = success, 1 = parse error, 2 = file not found.

## Projectctl Command Checklist

- [ ] report-failures
- [ ] verify-sprint
- [ ] next-action
- [ ] status
- [ ] update-status

