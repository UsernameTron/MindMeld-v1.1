# MindMeld Agent Report Schema Fixes

This document summarizes the fixes made to ensure proper validation and standardization of agent reports across the MindMeld platform.

## Overview of Fixes

The following issues were identified and fixed in the agent reports:

1. **Missing Required Fields**: Some reports were missing the required `agent` field.
2. **Non-Standard Status Values**: Reports used custom status strings like "AgentName executed (stub)" instead of the standard values ("success", "error", "partial_success").
3. **Data Structure Inconsistency**: Success reports lacked the required `data` field.
4. **Error Structure Inconsistency**: Error reports lacked the required `error` field with a `message` property.
5. **Fallback Model Inconsistency**: Reports with `fallback_used: true` missing the required `initial_model` field.

## Legacy Report Conversion

A special script (`fix_legacy_reports.py`) was created to fix non-conforming legacy reports. The script:

1. Adds missing `agent` fields by extracting them from metadata or report filenames.
2. Converts non-standard status values to standard ones.
3. Ensures required fields are present based on status.
4. Adds placeholders for any missing required data.

To run this script and fix any additional legacy reports:

```bash
python fix_legacy_reports.py --reports-dir reports
```

Use the `--dry-run` flag to preview changes without applying them:

```bash
python fix_legacy_reports.py --reports-dir reports --dry-run
```

## Schema Requirements

All agent reports must conform to these key requirements:

1. **Basic Fields**: Each report must have:
   - `agent` (string): Name of the agent
   - `status` (string): One of "success", "error", or "partial_success"
   - `timestamp` (integer): Unix timestamp

2. **Status-Specific Requirements**:
   - Reports with `status: "success"` must have a `data` object.
   - Reports with `status: "error"` must have an `error` object with a `message` property.

3. **Fallback Requirements**:
   - Reports with `metadata.fallback_used: true` must have `metadata.model_info.initial_model`.

## Backward Compatibility

For backward compatibility with older reports:

1. **Schema Validation**: All existing reports have been validated and fixed to conform to the schema.
2. **Versioning Strategy**: Consider adding a `schema_version` field to allow for future schema changes.
3. **Normalization**: The `normalize_agent_output` function in `schema_validator.py` converts any valid agent output to a schema-conforming format.

## Validation Process

Agent reports can be validated using:

```bash
python validate_schema_ci.py
```

For continuous integration validation, a GitHub Actions workflow is available in `.github/workflows/validate-agent-reports.yml`. The workflow:

1. Validates all agent reports against the schema
2. Runs the agent pipeline validation tests
3. Executes schema validation unit tests
4. Generates a validation summary report

```bash
# Run the validation workflow manually
gh workflow run validate-agent-reports.yml
```

## Future Considerations

1. **Schema Evolution**: As agent capabilities grow, we may need to evolve the schema. Use semantic versioning for changes.
2. **Report Converter**: Maintain and enhance the `fix_legacy_reports.py` script to handle future schema changes.
3. **Deprecation Strategy**: When making breaking changes, implement a deprecation cycle with ample warning.
4. **Documentation**: Keep this document up-to-date with any schema changes.

## References

- `agent_report_schema.json`: The canonical schema definition
- `schema_validator.py`: Utilities for validating and normalizing agent outputs
- `fix_legacy_reports.py`: Tool for fixing non-conforming reports
- `validate_schema_ci.py`: CI-friendly validation script
