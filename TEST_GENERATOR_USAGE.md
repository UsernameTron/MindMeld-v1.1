# Enhanced Test Generator for MindMeld

This document explains how to use the enhanced test generator to automatically create and improve tests for the MindMeld codebase.

## Features

The enhanced test generator now includes:

1. **Automatic import path fixing** - Makes tests runnable without manual editing
2. **Module-specific test templates** - Specialized templates for file operations, authentication, and API interactions
3. **Integration with CodeDebugAgent** - Automatically fixes issues in generated tests
4. **Priority-based module selection** - Focus testing efforts on high-priority modules

## Basic Usage

To generate tests for a single file:

```bash
python run_test_generator.py --single --enhance --path=src/utils/file_operations.py --output=tests/enhanced_generated
```

To generate tests for all files in a directory:

```bash
python run_test_generator.py --enhance --path=src/utils --output=tests/enhanced_generated
```

## Using Module-Specific Templates

The generator can apply specialized templates based on module type:

```bash
# For file operation modules
python run_test_generator.py --single --enhance --template=file --path=src/utils/file_operations.py

# For authentication modules
python run_test_generator.py --single --enhance --template=auth --path=src/auth/user_management.py

# For API/model interaction modules
python run_test_generator.py --single --enhance --template=api --path=src/api/model_client.py
```

## Focusing on Priority Modules

To focus test generation on specific high-priority modules:

```bash
python run_test_generator.py --enhance --path=src --priority-modules file_operations api_client auth
```

## Integrating with CodeDebugAgent

Enable the CodeDebugAgent to automatically fix issues in generated tests:

```bash
python run_test_generator.py --single --enhance --debug --path=src/utils/file_operations.py
```

## Using the Helper Script

The included `generate_priority_tests.py` script streamlines test generation for high-priority modules:

```bash
python generate_priority_tests.py --modules file_operations api_client auth --debug
```

This will:
1. Find all Python files containing the specified module names
2. Apply the appropriate template to each module
3. Run the CodeDebugAgent if requested
4. Generate enhanced tests in the output directory

## Test Templates

### File Operations Template

The file operations template adds:
- Temporary directory setup and teardown
- File permission tests
- File not found tests
- Proper file path handling

### Authentication Template

The authentication template adds:
- Mock user data and tokens
- Tests for invalid tokens
- Tests for expired tokens
- Permission checking tests

### API Template

The API template adds:
- Mock API responses
- Request patching
- Error handling tests
- Timeout tests

## Command Line Options

```
--path, -p PATH         Path to scan (default: src/utils)
--output, -o DIR        Output directory (default: tests/generated)
--framework, -f FRAMEWORK  Test framework to use (default: pytest)
--single, -s            Process a single file instead of directory
--enhance, -e           Enhance tests with better setup and assertions
--template, -t TEMPLATE Template to apply (file, auth, api, general)
--priority, -P PRIORITY Process only modules with specified priority (high, medium, low)
--debug, -d             Run CodeDebugAgent on generated tests to fix issues
--priority-modules [MODULES...]  List of high-priority module names to focus on
```
