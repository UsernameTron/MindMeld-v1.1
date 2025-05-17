#!/usr/bin/env python3
"""
CI Pipeline validator for agent reports.
This script checks all report files against the schema and fails if any are invalid.
"""

import os
import sys
import json
import jsonschema
from pathlib import Path
import argparse
from typing import List, Dict, Any, Tuple
import time

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
    """Validate a single report against the schema."""
    try:
        # Load schema
        with open(schema_path) as sf:
            schema = json.load(sf)
        
        # Load report
        with open(report_path) as rf:
            report = json.load(rf)
        
        # Validate
        jsonschema.validate(instance=report, schema=schema)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except jsonschema.exceptions.ValidationError as e:
        return False, f"Schema validation failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Validate agent reports against schema")
    parser.add_argument("--reports-dir", default="reports", help="Directory containing agent reports")
    parser.add_argument("--schema", default="agent_report_schema.json", help="Path to schema file")
    parser.add_argument("--fix", action="store_true", help="Try to fix invalid reports")
    args = parser.parse_args()
    
    # Find schema file
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema file not found: {args.schema}")
        return 1
    
    # Find report files
    report_files = find_report_files(args.reports_dir)
    if not report_files:
        print(f"No report files found in {args.reports_dir}")
        return 0
    
    print(f"Found {len(report_files)} report files to validate")
    
    # Validate each report
    validation_results = []
    for report_path in report_files:
        valid, error = validate_report(report_path, schema_path)
        validation_results.append((report_path, valid, error))
    
    # Count successes and failures
    successes = [r for r in validation_results if r[1]]
    failures = [r for r in validation_results if not r[1]]
    
    # Print results
    if failures:
        print(f"❌ Found {len(failures)} invalid reports:")
        for path, _, error in failures:
            print(f"  - {path}: {error}")
        
        if args.fix:
            from schema_validator import normalize_agent_output
            
            print("\nAttempting to fix invalid reports...")
            fixed_count = 0
            
            for path, _, _ in failures:
                try:
                    with open(path) as f:
                        report = json.load(f)
                    
                    # Extract basic info from the report
                    if isinstance(report, dict):
                        agent_name = report.get("metadata", {}).get("agent") or path.parent.name
                        timestamp = report.get("metadata", {}).get("timestamp") or int(time.time())
                        payload = report.get("metadata", {}).get("payload", "unknown")
                        runtime = report.get("metadata", {}).get("runtime_seconds", 0.0)
                        job_id = report.get("metadata", {}).get("job_id", "auto-fixed")
                        
                        # Normalize
                        normalized = normalize_agent_output(report, agent_name, payload, timestamp, runtime, job_id)
                        
                        # Validate normalized version
                        with open(schema_path) as sf:
                            schema = json.load(sf)
                        jsonschema.validate(instance=normalized, schema=schema)
                        
                        # Write fixed version
                        backup_path = path.with_suffix(f".bak-{int(time.time())}")
                        os.rename(path, backup_path)
                        with open(path, "w") as f:
                            json.dump(normalized, f, indent=2)
                        
                        fixed_count += 1
                        print(f"  ✅ Fixed: {path} (backup at {backup_path})")
                    else:
                        print(f"  ❌ Cannot fix {path}: not a dictionary")
                
                except Exception as e:
                    print(f"  ❌ Failed to fix {path}: {str(e)}")
            
            print(f"\nFixed {fixed_count} of {len(failures)} reports")
        
        return 1
    else:
        print(f"✅ All {len(successes)} reports are valid")
        return 0

if __name__ == "__main__":
    sys.exit(main())
