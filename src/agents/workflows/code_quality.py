# src/agents/workflows/code_quality.py

# Code Quality Workflow
CODE_QUALITY_WORKFLOW = {
    "name": "code_quality",
    "description": "Analyze and improve code quality in a file or directory",
    "version": "1.0",
    "steps": [
        {
            "id": "debug",
            "type": "agent",
            "agent": "code_debug",
            "description": "Detect bugs and issues in the code",
            "input": {},  # Will be filled from workflow input
        },
        {
            "id": "dependency",
            "type": "agent",
            "agent": "dependency_management",
            "description": "Analyze and manage dependencies",
            "input": {},  # Will be filled from workflow input
        },
        {
            "id": "test_gen",
            "type": "agent",
            "agent": "test_generator",
            "description": "Generate tests for the code",
            "input": {},  # Will be filled from workflow input
        },
        {
            "id": "results_aggregation",
            "type": "transform",
            "transform_type": "merge",
            "description": "Aggregate results from all agents",
            "input": ["results.debug", "results.dependency", "results.test_gen"],
        },
    ],
}

# Test Coverage Workflow
TEST_COVERAGE_WORKFLOW = {
    "name": "test_coverage",
    "description": "Generate comprehensive tests for the codebase",
    "version": "1.0",
    "steps": [
        {
            "id": "test_gen",
            "type": "agent",
            "agent": "test_generator",
            "description": "Generate tests for the code",
            "input": {},  # Will be filled from workflow input
        },
        {
            "id": "debug_tests",
            "type": "agent",
            "agent": "code_debug",
            "description": "Check generated tests for issues",
            "dynamic_input": {
                "code": "results.test_gen.test_code",
                "file_path": "input.test_file_path",
            },
        },
        {
            "id": "results_aggregation",
            "type": "transform",
            "transform_type": "merge",
            "description": "Aggregate results from all agents",
            "input": ["results.test_gen", "results.debug_tests"],
        },
    ],
}

# Dependency Analysis Workflow
DEPENDENCY_WORKFLOW = {
    "name": "dependency_analysis",
    "description": "Analyze dependencies and fix issues",
    "version": "1.0",
    "steps": [
        {
            "id": "dependency",
            "type": "agent",
            "agent": "dependency_management",
            "description": "Analyze and manage dependencies",
            "input": {},  # Will be filled from workflow input
        },
        {
            "id": "check_security",
            "type": "condition",
            "description": "Check for security vulnerabilities",
            "condition": {
                "type": "not_empty",
                "path": "results.dependency.vulnerabilities",
            },
            "then": {
                "id": "security_report",
                "type": "transform",
                "transform_type": "map",
                "description": "Create security vulnerability report",
                "input": "results.dependency.vulnerabilities",
                "options": {"fields": ["package", "version", "cve_ids"]},
            },
        },
        {
            "id": "check_missing_deps",
            "type": "condition",
            "description": "Check for missing dependencies",
            "condition": {
                "type": "not_empty",
                "path": "results.dependency.missing_dependencies",
            },
            "then": {
                "id": "install_command",
                "type": "transform",
                "transform_type": "map",
                "description": "Generate installation commands",
                "input": "results.dependency.installation_commands",
            },
        },
    ],
}

# All workflows
WORKFLOWS = {
    "code_quality": CODE_QUALITY_WORKFLOW,
    "test_coverage": TEST_COVERAGE_WORKFLOW,
    "dependency_analysis": DEPENDENCY_WORKFLOW,
}
