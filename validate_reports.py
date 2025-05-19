import json
import os
import sys

import jsonschema


def validate_reports(reports_dir):
    with open("agent_report_schema.json") as f:
        schema = json.load(f)

    errors = []
    for root, _, files in os.walk(reports_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path) as f:
                        report = json.load(f)
                    jsonschema.validate(instance=report, schema=schema)

                    # Check for error key in report
                    if "error" in report and report["error"]:
                        errors.append(f"Error in {path}: {report['error']}")
                except Exception as e:
                    errors.append(f"Invalid report {path}: {str(e)}")

    if errors:
        for err in errors:
            print(err)
        return False
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_reports.py <reports_dir>")
        sys.exit(1)

    valid = validate_reports(sys.argv[1])
    sys.exit(0 if valid else 1)
