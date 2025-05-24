#!/usr/bin/env python3
"""
Automated linting error fixer for MindMeld v1.1
Fixes common flake8 issues to allow successful git commit.
"""
import re
import subprocess
from pathlib import Path


def remove_unused_imports(file_path):
    """Remove unused imports from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get unused imports from flake8
        result = subprocess.run(
            ["python", "-m", "flake8", "--select=F401", file_path],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return content  # No unused imports

        lines = content.split("\n")
        lines_to_remove = set()

        for error_line in result.stdout.strip().split("\n"):
            if error_line and "F401" in error_line:
                # Extract line number
                match = re.search(r":(\d+):", error_line)
                if match:
                    line_num = int(match.group(1)) - 1  # Convert to 0-based
                    if 0 <= line_num < len(lines):
                        line = lines[line_num].strip()
                        # Only remove if it's clearly an import line
                        if (
                            line.startswith("import ")
                            or line.startswith("from ")
                            or (line and not line.startswith("#"))
                        ):
                            lines_to_remove.add(line_num)

        # Remove the lines (in reverse order to maintain indices)
        for line_num in sorted(lines_to_remove, reverse=True):
            del lines[line_num]

        # Clean up consecutive empty lines
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if line.strip() == "":
                if not prev_empty:
                    cleaned_lines.append(line)
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        return "\n".join(cleaned_lines)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def fix_whitespace_issues(content):
    """Fix common whitespace issues."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Remove trailing whitespace (W291, W293)
        line = line.rstrip()

        # Fix missing whitespace around operators (E226, E231)
        line = re.sub(r"([a-zA-Z0-9_])([+\-*/=<>!])([a-zA-Z0-9_])", r"\1 \2 \3", line)
        line = re.sub(r',([a-zA-Z0-9_"\'{\[])', r", \1", line)

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_blank_lines(content):
    """Fix blank line issues (E302, E305)."""
    lines = content.split("\n")
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a function/class definition
        if (
            re.match(r"^(def |class |async def )", line.strip())
            and i > 0
            and lines[i - 1].strip() != ""
        ):
            # Need 2 blank lines before top-level functions/classes
            if i >= 2 and not (
                lines[i - 1].strip() == "" and lines[i - 2].strip() == ""
            ):
                # Add blank lines if not already there
                if lines[i - 1].strip() != "":
                    fixed_lines.append("")
                    fixed_lines.append("")
                elif i >= 2 and lines[i - 2].strip() != "":
                    fixed_lines.append("")

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)


def fix_comparison_issues(content):
    """Fix comparison to True/False issues (E712)."""
    # Fix == True to is True
    content = re.sub(r"== True\b", "is True", content)
    content = re.sub(r"== False\b", "is False", content)
    # Better: remove entirely where possible
    content = re.sub(r"if (.+?) is True:", r"if \1:", content)
    content = re.sub(r"if (.+?) == True:", r"if \1:", content)
    return content


def fix_f_string_issues(content):
    """Fix f-string without placeholders (F541)."""
    # Find f-strings without placeholders and convert to regular strings
    content = re.sub(r'f"([^{}"]*)"', r'"\1"', content)
    content = re.sub(r"f'([^{}']*)'", r"'\1'", content)
    return content


def fix_file(file_path):
    """Fix a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        content = original_content

        # Apply fixes
        content = remove_unused_imports(file_path) or content
        content = fix_whitespace_issues(content)
        content = fix_blank_lines(content)
        content = fix_comparison_issues(content)
        content = fix_f_string_issues(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix linting errors."""
    project_root = Path(__file__).parent
    python_files = []

    # Find all Python files
    for pattern in ["**/*.py"]:
        python_files.extend(project_root.glob(pattern))

    # Exclude certain directories
    exclude_dirs = {".git", "__pycache__", "venv", "node_modules", ".pytest_cache"}
    python_files = [
        f for f in python_files if not any(part in exclude_dirs for part in f.parts)
    ]

    print(f"Found {len(python_files)} Python files to check")

    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1

    print(f"Fixed {fixed_count} files")

    # Run autoflake to remove more unused imports
    print("Running autoflake to remove unused imports...")
    subprocess.run(
        [
            "python",
            "-m",
            "autoflake",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--in-place",
            "--recursive",
            ".",
        ],
        cwd=project_root,
    )

    # Run black for consistent formatting
    print("Running black for formatting...")
    subprocess.run(
        ["python", "-m", "black", "--line-length", "88", "."], cwd=project_root
    )


if __name__ == "__main__":
    main()
