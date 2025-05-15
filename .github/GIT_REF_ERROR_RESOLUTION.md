# GitHub Actions Git Reference & Artifact Error Resolution (May 2025)

## Problem
- Previous workflows used `origin/main` for git diff, which fails in PRs or shallow clones.
- Artifact upload/download steps caused failures due to IAP and permissions issues.

## Solution
- Use `${{ github.event.before }}` as the base SHA for git diff, falling back to `HEAD~1` if unavailable.
- Set `fetch-depth: 0` in the checkout action to ensure full git history for all comparisons.
- Remove all artifact upload/download steps from workflows (especially tech-debt-check).
- Only essential build, test, and analysis steps remain.

## Example
```yaml
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Run component verification
        run: |
          BASE_SHA="${{ github.event.before }}"
          if [ -z "$BASE_SHA" ] || ! git cat-file -e $BASE_SHA; then
            BASE_SHA=$(git rev-parse HEAD~1)
          fi
          CHANGED_DIRS=$(git diff --name-only $BASE_SHA ${{ github.sha }} | grep -oP 'frontend/src/components/\\K[^/]+' | sort -u)
          for DIR in $CHANGED_DIRS; do
            ./scripts/verify-component.sh $DIR
          done
```

## Notes
- This approach works for both PR and push events.
- No artifacts are uploaded or downloaded; all steps are self-contained.
- See workflow file for full implementation.

_Last updated: May 14, 2025_
