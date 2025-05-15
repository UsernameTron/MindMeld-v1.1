#!/bin/zsh
# extract_github_workflow_failures.sh
# Extract and summarize recent GitHub Actions workflow failures

# List the 20 most recent workflow runs with failure conclusion
GH_REPO="UsernameTron/MindMeld"  # Set your repo here

gh run list -L 20 --json databaseId,name,status,conclusion,url --jq '.[] | select(.conclusion=="failure")' > failed_runs.json

# Extract error messages from logs for each failed run
rm -f error_logs.txt
for run_id in $(cat failed_runs.json | jq -r '.databaseId'); do
  echo "Extracting errors from run $run_id"
  gh run view $run_id --log | grep -Ei -A 5 -B 2 'error|failed|exception|fatal' >> error_logs.txt
  echo "----------------------------------------" >> error_logs.txt
done

# Group and count unique error messages
awk '/error|failed|exception|fatal/ {print tolower($0)}' error_logs.txt | sort | uniq -c | sort -nr > error_summary.txt

# Output summary report
cat <<EOF > github_workflow_failure_report.txt
GitHub Actions Workflow Failure Summary (last 20 runs)
Date: $(date)

Failure Patterns (grouped, with counts):
----------------------------------------
$(cat error_summary.txt)

Recommendations:
----------------
- Review the most frequent error types above.
- For dependency or permission errors, check token scopes and runner environment.
- For syntax or YAML errors, validate workflow files with 'act' or the GitHub Actions linter.
- For network or API failures, retry or check service status.
- For persistent issues, consult the GitHub Actions documentation or open an issue with logs.

EOF

echo "Summary report written to github_workflow_failure_report.txt"
