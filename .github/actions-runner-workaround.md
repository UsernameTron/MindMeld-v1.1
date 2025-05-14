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

## Notes
- Artifact naming and retention behavior are preserved.
- All changes are documented inline in workflow files.
- This is a temporary workaround until `actions/upload-artifact` is IAP-compliant.

_Last updated: May 14, 2025_
