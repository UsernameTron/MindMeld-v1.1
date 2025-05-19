#!/usr/bin/env python3
import json
from pathlib import Path

import jsonschema

# Load our schema
schema_path = Path(__file__).parent / "agent_report_schema.json"
with open(schema_path) as f:
    REPORT_SCHEMA = json.load(f)

print(f"Schema loaded from {schema_path}")

# Test with valid examples
valid_examples = [
    {"analysis": "This is a valid object report"},
    [{"result": "item1"}, {"result": "item2"}],
    {"results": [1, 2, 3], "metadata": {"agent": "test"}}
]

for i, example in enumerate(valid_examples):
    try:
        jsonschema.validate(instance=example, schema=REPORT_SCHEMA)
        print(f"✅ Valid example {i+1} passed validation")
    except Exception as e:
        print(f"❌ Valid example {i+1} failed validation: {e}")

# Test with invalid examples
invalid_examples = [
    "Not a JSON object or array, just a string",
    42,
    True
]

for i, example in enumerate(invalid_examples):
    try:
        jsonschema.validate(instance=example, schema=REPORT_SCHEMA)
        print(f"❌ Invalid example {i+1} passed validation unexpectedly")
    except Exception as e:
        print(f"✅ Invalid example {i+1} correctly failed: {e}")

# Now try to validate a few existing reports
reports_dir = Path(__file__).parent / "reports"
if reports_dir.exists():
    print("\nValidating existing reports:")
    for agent_dir in reports_dir.iterdir():
        if not agent_dir.is_dir() or agent_dir.name == "__pycache__":
            continue
            
        for report_file in agent_dir.glob("*.json"):
            try:
                with open(report_file) as f:
                    try:
                        data = json.load(f)
                        jsonschema.validate(instance=data, schema=REPORT_SCHEMA)
                        print(f"✅ {report_file.relative_to(Path(__file__).parent)} is valid")
                    except json.JSONDecodeError:
                        print(f"❌ {report_file.relative_to(Path(__file__).parent)} is not valid JSON")
                    except jsonschema.exceptions.ValidationError as e:
                        print(f"❌ {report_file.relative_to(Path(__file__).parent)} failed validation: {e}")
            except Exception as e:
                print(f"❌ Error reading {report_file.relative_to(Path(__file__).parent)}: {e}")
