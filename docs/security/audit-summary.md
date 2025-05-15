# Audit Summary (2025-05-13)

## Audit Diff Before and After Upgrades

### Before
- Frontend: `next` vulnerable ([GHSA-fr5h-rqp8-mj6g], [GHSA-7gfc-8cq8-jh5f])
- Backend: `setuptools` vulnerable ([CVE-2022-40897])

### After
- Frontend: No vulnerabilities found (`npm audit` clean)
- Backend: `setuptools` upgraded to >=65.5.1 (no longer outdated)

---

## Actions Taken
- Upgraded Next.js to 15.3.2
- Upgraded setuptools to 80.4.0

All critical advisories resolved as of this audit.
