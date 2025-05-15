# Temporary GitHub Actions Workflow Simplification (May 2025)

Due to GitHub's IAP runner restrictions and the lack of IAP-compliant artifact upload actions, all workflows have been simplified:

- **No artifact upload or download steps** (all softprops/action-gh-release and similar steps removed)
- **Direct build, test, and deploy** in single jobs
- **Deployments use direct SSH or similar methods** (no artifact transfer)
- Only essential checks and deployment steps are included

This is a temporary measure until GitHub resolves the IAP artifact issue. See previous workflow history for full artifact-based logic.

_Last updated: May 14, 2025_
