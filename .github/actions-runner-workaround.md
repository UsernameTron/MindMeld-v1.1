# GitHub Actions Artifact Workaround (May 2025)

## Problem
GitHub Actions runners (ubuntu-22.04, ubuntu-24.04) now require Immutable Action Packages (IAPs). The official `actions/upload-artifact` is not available as an IAP, breaking artifact upload/download in all workflows.

## Solution: Use GitHub Releases as Temporary Artifact Storage

All workflows now use [softprops/action-gh-release](https://github.com/softprops/action-gh-release) to upload artifacts as draft release assets. This works with the new IAP requirements and is compatible with all Ubuntu runners.

### Uploading Artifacts
- Each workflow generates a unique release tag using the run ID and timestamp.
- Artifacts are zipped and uploaded as release assets to a draft release.
- Example:
  ```yaml
  - name: Generate unique release tag
    id: tag
    run: |
      echo "tag=artifact-${{ github.run_id }}-$(date +%s)" >> $GITHUB_OUTPUT

  - name: Package artifact
    run: zip my-artifact.zip my-artifact.file

  - name: Upload artifact as release asset
    uses: softprops/action-gh-release@v2
    with:
      files: my-artifact.zip
      tag_name: ${{ steps.tag.outputs.tag }}
      draft: true
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```

### Downloading Artifacts
- Use the GitHub API to fetch the asset URL from the draft release, then download and unzip.
- Example:
  ```yaml
  - name: Download artifact
    run: |
      TAG="${{ needs.build.outputs.artifact_tag }}"
      ASSET_URL=$(curl -s -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
        "https://api.github.com/repos/${{ github.repository }}/releases/tags/$TAG" | \
        jq -r '.assets[0].url')
      curl -L -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
        -H "Accept: application/octet-stream" \
        -o artifact.zip "$ASSET_URL"
      unzip artifact.zip -d ./output
  ```

### Cleanup
- After workflow completion, the draft release is deleted to avoid clutter.
- Example:
  ```yaml
  - name: Cleanup temporary release
    if: always()
    run: |
      TAG="${{ steps.tag.outputs.tag }}"
      RELEASE_ID=$(curl -s -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
        "https://api.github.com/repos/${{ github.repository }}/releases/tags/$TAG" | \
        jq -r '.id')
      if [ "$RELEASE_ID" != "null" ]; then
        curl -X DELETE -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
          "https://api.github.com/repos/${{ github.repository }}/releases/$RELEASE_ID"
      fi
  ```

## Artifact upload Personal Access Token (PAT) requirements

### Why a PAT is needed
- GitHub Actions' default `GITHUB_TOKEN` does not have `release:write` permissions in `pull_request` workflows, which breaks release-based artifact uploads (e.g., with softprops/action-gh-release).
- To enable artifact uploads for both push and PR events, a Personal Access Token (PAT) with `repo` and `release:write` scopes is required.

### Setup instructions
1. Create a new GitHub PAT with the following scopes:
   - `repo`
   - `release:write`
2. Add the PAT as a repository secret named `GH_PAT`.
3. The workflows are configured to use `GH_PAT` for release creation and artifact upload steps only on `push` and `workflow_dispatch` events (not on forked PRs).
4. The PAT is never exposed to steps that do not require it (principle of least privilege).

### Security notes
- Never use a PAT with excessive permissions.
- Never print the PAT or expose it in logs.
- If the PAT is compromised, revoke it immediately and update the secret.

### Example usage in workflow:
```yaml
- name: Upload artifact as release asset
  uses: softprops/action-gh-release@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GH_PAT }}
  if: ${{ secrets.GH_PAT != '' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch') }}
  # ...other config...
```

### Troubleshooting
- If artifact upload fails with a 403, check that the PAT is valid and has the correct scopes.
- If the secret is missing, the step will be skipped (see workflow `if` condition).

## Notes
- Artifact naming and retention behavior are preserved.
- All changes are documented inline in workflow files.
- This is a temporary workaround until `actions/upload-artifact` is IAP-compliant.

_Last updated: May 14, 2025_
