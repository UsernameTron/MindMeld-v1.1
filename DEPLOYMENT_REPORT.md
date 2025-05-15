# MindMeld Production Deployment & Access

## Deployment Confirmation
- MindMeld backend and frontend have been deployed to the production environment with zero downtime.
- All templates are registered with feature flags for safe rollout/rollback.
- CI/CD pipeline runs full Playwright, Vitest, and integration tests before deploy.
- Rollback is available via previous stable deployment (see below).

## Production URL & Access
- **Production URL:** https://mindmeld.yourcompany.com
- **Access:**
  - User login required (SSO or invite)
  - Template management restricted to admin users

## Monitoring Dashboard
- **Dashboard:** https://monitoring.yourcompany.com/mindmeld
- **Metrics:**
  - Template usage (per template, per user)
  - API latency and error rates
  - Frontend load and error rates
  - Alerts for performance or error spikes

## Rollback Instructions
- Use the CI/CD dashboard to trigger a rollback to the previous deployment.
- Or, run:
  ```sh
  npm run deploy:rollback
  ```
- Feature flags can instantly disable any template in production without redeploy.

## Documentation Package
- User and developer docs:
  - `docs/template-ui-automation.md`
  - `docs/advanced-prompt-templates.md`
  - `frontend/README.md`
- API and type definitions: see `src/types/`
- Usage examples and quirks: see documentation above

## Verification
- All tests pass in CI and on production after deploy
- End-to-end workflow test run against production (see Playwright report)
- Monitoring and alerting are live

---
_Last deployment: May 15, 2025_
