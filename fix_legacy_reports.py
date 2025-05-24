#!/usr/bin/env python3
"""
Script to fix legacy agent reports to conform to the new schema.
This script handles two main issues:
1. Missing 'agent' field in reports
2. Non-standard status values

Usage:
    python fix_legacy_reports.py [--reports-dir reports] [--dry-run]
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import jsonschema


def find_legacy_reports(reports_dir: str = "reports") -> List[Path]:
    """Find all agent reports with schema validation issues."""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        print(f"Reports directory not found: {reports_dir}")
        return []

    all_files = []

    # Search through all subdirectories
    for agent_dir in [d for d in reports_path.iterdir() if d.is_dir()]:
        json_files = list(agent_dir.glob("*.json"))
        all_files.extend(json_files)

    return all_files


def load_schema(schema_path: str = "agent_report_schema.json") -> Dict[str, Any]:
    """Load the schema definition."""
    with open(schema_path) as f:
        return json.load(f)


def is_valid_report(report: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if a report is valid according to the schema."""
    try:
        jsonschema.validate(report, schema)
        return True, ""
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)


def fix_report_status(status_text: str) -> str:
    """
    Normalize non-standard status values to standard ones.
    Maps text like "AgentName executed (stub)" to "success".
    """
    if isinstance(status_text, str):
        if "executed" in status_text or "completed" in status_text:
            return "success"
        elif "error" in status_text or "failed" in status_text:
            return "error"
        elif "partial" in status_text:
            return "partial_success"

    # Default to success if we can't determine
    return "success"


def fix_legacy_report(report_path: Path, dry_run: bool = False) -> bool:
    """Fix a legacy report to conform to the schema."""
    try:
        with open(report_path) as f:
            report = json.load(f)

        original_report = report.copy()
        modified = False

        # Fix 1: Add missing 'agent' field
        if (
            "agent" not in report
            and "metadata" in report
            and "agent" in report["metadata"]
        ):
            report["agent"] = report["metadata"]["agent"]
            modified = True
        elif "agent" not in report:
            # Extract from file path if not available in metadata
            report["agent"] = report_path.parent.name
            modified = True

        # Fix 2: Fix non-standard status values
        if "status" in report and report["status"] not in [
            "success",
            "error",
            "partial_success",
        ]:
            report["status"] = fix_report_status(report["status"])
            modified = True

        # Fix 3: Ensure timestamp is present
        if (
            "timestamp" not in report
            and "metadata" in report
            and "timestamp" in report["metadata"]
        ):
            report["timestamp"] = report["metadata"]["timestamp"]
            modified = True
        elif "timestamp" not in report:
            # Use file timestamp or current time
            report["timestamp"] = int(os.path.getmtime(report_path)) or int(time.time())
            modified = True

        # Fix 4: Ensure data field exists for success status
        if report.get("status") == "success" and "data" not in report:
            # Extract agent-specific fields as data
            standard_fields = {
                "agent",
                "status",
                "timestamp",
                "payload",
                "runtime_seconds",
                "metadata",
                "error",
            }
            data_fields = {k: v for k, v in report.items() if k not in standard_fields}

            if data_fields:
                report["data"] = data_fields
                # Remove duplicates from report root
                for k in data_fields.keys():
                    if k in report:
                        del report[k]
            else:
                # If no agent-specific data, add a placeholder
                report["data"] = {
                    "message": "Agent executed successfully (legacy report)"
                }

            modified = True

        # Fix 5: Ensure error field exists for error status
        if report.get("status") == "error" and "error" not in report:
            report["error"] = {"message": "Unknown error (legacy report)"}
            modified = True

        # Fix 6: Ensure model_info has initial_model when fallback_used is true
        if "metadata" in report and report["metadata"].get("fallback_used") == True:
            if "model_info" not in report["metadata"]:
                report["metadata"]["model_info"] = {}

            if "initial_model" not in report["metadata"]["model_info"]:
                report["metadata"]["model_info"][
                    "initial_model"
                ] = "unknown (legacy report)"
                modified = True

        # Check if the modified report is valid
        schema = load_schema()
        valid, error = is_valid_report(report, schema)

        if not valid:
            print(f"❌ Couldn't fix {report_path}: {error}")
            return False

        if modified:
            if dry_run:
                print(f"Would fix: {report_path}")
                print(f"  Before: {original_report}")
                print(f"  After: {report}")
            else:
                # Make a backup of the original file
                backup_path = report_path.with_suffix(f".bak-{int(time.time())}")
                os.rename(report_path, backup_path)

                # Write the fixed report
                with open(report_path, "w") as f:
                    json.dump(report, f, indent=2)

                print(f"✅ Fixed: {report_path} (backup at {backup_path})")

            return True
        else:
            print(f"⚠️ No changes needed for {report_path}")
            return False

    except Exception as e:
        print(f"❌ Error processing {report_path}: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fix legacy agent reports to conform to the schema"
    )
    parser.add_argument(
        "--reports-dir", default="reports", help="Directory containing agent reports"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    reports = find_legacy_reports(args.reports_dir)
    print(f"Found {len(reports)} agent reports to check")

    fixed_count = 0
    schema = load_schema()

    for report_path in reports:
        # Check if the report is valid first
        try:
            with open(report_path) as f:
                report = json.load(f)

            valid, _ = is_valid_report(report, schema)

            if not valid:
                if fix_legacy_report(report_path, args.dry_run):
                    fixed_count += 1
        except Exception as e:
            print(f"❌ Error checking {report_path}: {str(e)}")

    if args.dry_run:
        print(f"\nWould fix {fixed_count} reports (dry run)")
    else:
        print(f"\nFixed {fixed_count} reports")


if __name__ == "__main__":
    main()
