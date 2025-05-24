#!/usr/bin/env python3
"""
CI Pipeline validator for agent reports.
This script checks all report files against the schema and fails if any are invalid.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Try to import our schema validator
try:
    from utils.error_handling import SchemaValidationError
    from utils.file_operations import safe_file_write
    from utils.schema_validator import load_schema, validate_agent_output

    USE_SCHEMA_VALIDATOR = True
except ImportError:
    import jsonschema

    USE_SCHEMA_VALIDATOR = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_report_files(reports_dir: str = "reports") -> List[Path]:
    """Find all agent report JSON files in the reports directory."""
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


def validate_report(report_path: Path, schema_path: Path) -> Tuple[bool, str]:
    """
    Validate a single report against the schema.

    Args:
        report_path: Path to the report file
        schema_path: Path to the schema file

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Load report
        with open(report_path) as rf:
            report = json.load(rf)

        if USE_SCHEMA_VALIDATOR:
            # Use our dedicated schema validator
            schema = load_schema(schema_path)
            is_valid, error = validate_agent_output(report, schema)
            return is_valid, error or ""
        else:
            # Fall back to direct jsonschema validation
            with open(schema_path) as sf:
                schema = json.load(sf)
            jsonschema.validate(instance=report, schema=schema)
            return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except jsonschema.exceptions.ValidationError as e:
        return False, f"Schema validation failed: {str(e)}"
    except SchemaValidationError as e:
        return False, f"Schema validation failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def main():
    """Main validation function with improved error handling and reporting."""
    parser = argparse.ArgumentParser(
        description="Validate agent reports against schema"
    )
    parser.add_argument(
        "--reports-dir", default="reports", help="Directory containing agent reports"
    )
    parser.add_argument(
        "--schema", default="agent_report_schema.json", help="Path to schema file"
    )
    parser.add_argument("--fix", action="store_true", help="Try to fix invalid reports")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Find schema file
    schema_path = Path(args.schema)
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return 1

    # Find report files
    start_time = time.time()
    report_files = find_report_files(args.reports_dir)

    if not report_files:
        logger.warning(f"No report files found in {args.reports_dir}")
        return 0

    logger.info(f"Found {len(report_files)} report files to validate")

    # Validate each report
    results = []
    for report_file in report_files:
        agent_name = report_file.parent.name
        is_valid, error = validate_report(report_file, schema_path)

        results.append(
            {
                "file": str(report_file.relative_to(Path.cwd())),
                "agent": agent_name,
                "valid": is_valid,
                "error": error if not is_valid else None,
            }
        )

        if is_valid:
            logger.debug(f"✅ Valid: {report_file}")
        else:
            logger.error(f"❌ Invalid: {report_file} - {error}")

            # Try to fix if requested
            if args.fix and USE_SCHEMA_VALIDATOR:
                try:
                    from utils.schema_validator import fix_agent_report

                    with open(report_file) as f:
                        report_data = json.load(f)

                    fixed_report = fix_agent_report(report_data)

                    # Write the fixed report
                    if "safe_file_write" in globals():
                        safe_file_write(report_file, json.dumps(fixed_report, indent=2))
                    else:
                        with open(report_file, "w") as f:
                            json.dump(fixed_report, f, indent=2)
                    logger.info(f"🔧 Fixed report: {report_file}")
                except Exception as e:
                    logger.error(f"Failed to fix report {report_file}: {str(e)}")

    # Write validation summary
    summary_file = Path(args.reports_dir) / "validation_summary.json"
    summary = {
        "timestamp": int(time.time()),
        "schema": str(schema_path),
        "total_reports": len(report_files),
        "valid_reports": sum(1 for r in results if r["valid"]),
        "invalid_reports": sum(1 for r in results if not r["valid"]),
        "runtime_seconds": time.time() - start_time,
        "results": results,
    }

    if "safe_file_write" in globals():
        safe_file_write(summary_file, json.dumps(summary, indent=2))
    else:
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

    logger.info(f"Validation summary written to {summary_file}")

    # Return success if all reports are valid
    if summary["invalid_reports"] > 0:
        logger.error(f"Found {summary['invalid_reports']} invalid reports")
        return 1
    else:
        logger.info(f"All {summary['total_reports']} reports are valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
