# Adapter Development Guide

Complete guide to creating custom linting adapters for lint-tool.

## Table of Contents

1. [Adapter Architecture](#adapter-architecture)
2. [Required Files](#required-files)
3. [Step-by-Step Tutorial](#step-by-step-tutorial)
4. [API Reference](#api-reference)
5. [File Structure](#file-structure)
6. [Testing](#testing)
7. [Integration with lintrunner](#integration-with-lintrunner)
8. [Examples](#examples)

---

## Adapter Architecture

An adapter is a Python module that:
1. **Detects** problems in files
2. **Reports** findings via stdout/stderr
3. **Returns** exit code (0 = success, non-zero = issues found)
4. Optionally **fixes** issues (if `is_formatter = true`)

### Adapter Types

| Type | Purpose | Example |
|------|---------|---------|
| **Checker** | Reports issues only | CLANGTIDY, FLAKE8 |
| **Formatter** | Fixes issues | CLANGFORMAT, PYFMT |
| **Validator** | Validates configuration | EDITORCONFIG, PYPROJECT |
| **Custom** | Project-specific rules | ROOT_LOGGING, COPYRIGHT |

---

## Required Files

Creating a complete adapter requires these files:

### Minimum Files

```
src/lint_tool/adapters/
├── my_linter.py              # Core implementation
├── my_linter_linter.py       # lintrunner entry point
└── tests/
    └── test_my_linter.py     # Unit tests
```

### Complete Files

```
src/lint_tool/adapters/
├── my_linter.py              # Core implementation
├── my_linter_linter.py       # lintrunner entry point
├── __init__.py               # Package exports (if needed)
└── tests/
    ├── __init__.py
    ├── test_my_linter.py     # Unit tests
    ├── fixtures/
    │   ├── valid.py          # Valid file example
    │   ├── invalid.py        # Invalid file example
    │   └── config.json       # Config file example
    └── test_integration.py   # Integration tests
```

---

## Step-by-Step Tutorial

### Step 1: Create Core Implementation

**File:** `src/lint_tool/adapters/my_linter.py`

```python
"""Custom linter adapter implementation."""

import subprocess
from typing import List, Optional


class MyLinterConfig:
    """Configuration for my-linter."""

    def __init__(
        self,
        binary: str = "my-linter",
        config: Optional[str] = None,
        fix: bool = False,
    ):
        """Initialize configuration.
        
        Args:
            binary: Path to linter binary
            config: Path to config file
            fix: Whether to apply fixes
        """
        self.binary = binary
        self.config = config
        self.fix = fix


def run_linter(
    config: MyLinterConfig,
    file_paths: List[str],
    **kwargs,
) -> int:
    """Run my-linter on files.
    
    Args:
        config: Linter configuration
        file_paths: Files to lint
        **kwargs: Additional arguments (environment, etc.)
    
    Returns:
        Exit code (0 = success, 1 = issues found, 2 = error)
    """
    if not file_paths:
        return 0

    try:
        cmd = [config.binary]

        # Add config file if specified
        if config.config:
            cmd.extend(["--config", config.config])

        # Add fix flag if enabled
        if config.fix:
            cmd.append("--fix")

        # Add files to lint
        cmd.extend(file_paths)

        # Run linter
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Print output
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")

        # Return exit code
        return result.returncode

    except FileNotFoundError:
        print(f"Error: {config.binary} not found in PATH")
        print("Install with: pip install my-linter")
        return 2

    except subprocess.TimeoutExpired:
        print("Error: my-linter timed out")
        return 2

    except Exception as e:
        print(f"Error running {config.binary}: {e}")
        return 2
```

### Step 2: Create lintrunner Entry Point

**File:** `src/lint_tool/adapters/my_linter_linter.py`

```python
"""lintrunner entry point for my-linter adapter."""

import argparse
import sys

from . import my_linter


def main() -> int:
    """Main entry point for lintrunner."""
    parser = argparse.ArgumentParser(
        description="my-linter adapter for lintrunner",
        prog="lint_tool.adapters.my_linter_linter",
    )

    parser.add_argument(
        "--binary",
        default="my-linter",
        help="Path to my-linter binary (default: my-linter)",
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes to files",
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Files to lint",
    )

    args = parser.parse_args()

    # Create config
    config = my_linter.MyLinterConfig(
        binary=args.binary,
        config=args.config,
        fix=args.fix,
    )

    # Run linter
    return my_linter.run_linter(config, args.files)


if __name__ == "__main__":
    sys.exit(main())
```

### Step 3: Create Unit Tests

**File:** `tests/test_my_linter.py`

```python
"""Unit tests for my-linter adapter."""

import pytest
from lint_tool.adapters import my_linter


class TestMyLinterConfig:
    """Test configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = my_linter.MyLinterConfig()
        assert config.binary == "my-linter"
        assert config.config is None
        assert config.fix is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = my_linter.MyLinterConfig(
            binary="/usr/bin/my-linter",
            config="my-linter.json",
            fix=True,
        )
        assert config.binary == "/usr/bin/my-linter"
        assert config.config == "my-linter.json"
        assert config.fix is True


class TestRunLinter:
    """Test linter execution."""

    def test_no_files(self):
        """Test with no files."""
        config = my_linter.MyLinterConfig()
        result = my_linter.run_linter(config, [])
        assert result == 0

    def test_missing_binary(self):
        """Test when binary is not found."""
        config = my_linter.MyLinterConfig(binary="/nonexistent/my-linter")
        result = my_linter.run_linter(config, ["test.py"])
        assert result == 2

    def test_valid_file(self, tmp_path):
        """Test with valid file."""
        test_file = tmp_path / "valid.py"
        test_file.write_text("print('hello')")

        config = my_linter.MyLinterConfig()
        result = my_linter.run_linter(config, [str(test_file)])
        assert isinstance(result, int)


class TestIntegration:
    """Integration tests."""

    def test_multiple_files(self, tmp_path):
        """Test with multiple files."""
        files = []
        for i in range(3):
            f = tmp_path / f"file_{i}.py"
            f.write_text(f"# File {i}")
            files.append(str(f))

        config = my_linter.MyLinterConfig()
        result = my_linter.run_linter(config, files)
        assert isinstance(result, int)
```

### Step 4: Create .lintrunner.toml Configuration

```toml
[[linter]]
code = 'MY_LINTER'
include_patterns = ['**/*.py']
exclude_patterns = ['ThirdParty/**', 'build/**']
init_command = [
    'python3',
    '-m',
    'lint_tool.adapters.pip_init',
    '--dry-run={{DRYRUN}}',
    'my-linter==1.0.0',
]
command = [
    'python3',
    '-m',
    'lint_tool.adapters.my_linter_linter',
    '--binary=.lintbin/my-linter',
    '--',
    '@{{PATHSFILE}}',
]
is_formatter = false  # Set true if adapter fixes files
```

---

## API Reference

### MyLinterConfig Class

```python
class MyLinterConfig:
    """Configuration object for the linter."""

    def __init__(
        self,
        binary: str = "my-linter",
        config: Optional[str] = None,
        fix: bool = False,
    ):
        """Initialize configuration.

        Args:
            binary: Path to linter binary or name
            config: Path to configuration file
            fix: Whether to apply automatic fixes
        """
```

### run_linter Function

```python
def run_linter(
    config: MyLinterConfig,
    file_paths: List[str],
    **kwargs,
) -> int:
    """Run linter on files.

    Args:
        config: Linter configuration object
        file_paths: List of file paths to lint
        **kwargs: Additional arguments (unused in basic adapters)

    Returns:
        Exit code:
            0 = All files passed
            1 = Linting issues found
            2 = Error (tool not found, timeout, etc.)

    Raises:
        subprocess.TimeoutExpired: If linter takes >5 minutes
    """
```

### Return Codes

| Code | Meaning | When to Use |
|------|---------|------------|
| 0 | Success | No issues found, or fixes applied successfully |
| 1 | Issues found | Linting problems detected (but linter ran) |
| 2 | Error | Tool not found, timeout, or runtime error |

---

## File Structure

### Source Directory Structure

```
src/lint_tool/adapters/
├── __init__.py                    # Exports available adapters
├── my_linter.py                   # Core implementation
├── my_linter_linter.py            # lintrunner entry point
├── pip_init.py                    # Package installation adapter
├── s3_init.py                     # S3 binary download adapter
└── update_s3.py                   # S3 cache update utility
```

### Test Directory Structure

```
tests/
├── __init__.py
├── test_my_linter.py              # Unit and integration tests
├── fixtures/                       # Test files and configs
│   ├── valid.py
│   ├── invalid.py
│   └── config.json
└── test_integration.py            # End-to-end tests
```

### Package Exports

**File:** `src/lint_tool/adapters/__init__.py`

```python
"""Adapters package."""

from . import my_linter

__all__ = ["my_linter"]
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_my_linter.py

# Run specific test
pytest tests/test_my_linter.py::TestMyLinterConfig::test_default_config

# With coverage
pytest --cov=lint_tool tests/
pytest --cov=lint_tool --cov-report=html tests/
```

### Test Template

```python
"""Tests for my_linter adapter."""

import pytest
from pathlib import Path
from lint_tool.adapters import my_linter


@pytest.fixture
def tmp_file(tmp_path):
    """Create temporary test file."""
    f = tmp_path / "test.py"
    f.write_text("test content")
    return f


class TestMyLinter:
    """Test suite for my_linter."""

    def test_feature_description(self, tmp_file):
        """Test specific feature.
        
        Given: A file with [specific content]
        When: We run the linter
        Then: We expect [specific behavior]
        """
        config = my_linter.MyLinterConfig()
        result = my_linter.run_linter(config, [str(tmp_file)])
        assert result in (0, 1)  # Success or issues found
```

### Coverage Requirements

- **Minimum:** 80% code coverage
- **Target:** 90%+ code coverage
- All public functions must be tested
- Happy path and error paths

---

## Integration with lintrunner

### Configuration Options

```toml
[[linter]]
# Required
code = 'MY_LINTER'                    # Uppercase identifier
include_patterns = ['**/*.py']        # Files to lint
command = ['python3', '-m', '...']   # Command to run

# Optional
exclude_patterns = ['build/**']       # Files to skip
init_command = ['python3', '-m', ...]  # Setup command
is_formatter = false                   # true if auto-fixes
run_on_init = false                    # Run during init
timeout = 300                          # Timeout in seconds
```

### init_command vs command

**init_command** runs once to set up:
- Install packages: `pip install`
- Download binaries: `s3_init`
- Generate config: custom setup

**command** runs for every lint operation:
- Actual linting
- File checking
- Issue reporting

### Special Variables

| Variable | Meaning | Example |
|----------|---------|---------|
| `{{DRYRUN}}` | Dry run mode flag | `--dry-run=1` |
| `{{PATHSFILE}}` | File list location | `@paths.txt` |
| `{{SEVERITY}}` | Issue severity level | Set by lintrunner |

---

## Examples

### Example 1: Simple Python Linter

```python
# my_linter.py
import subprocess
from typing import List


class MyLinterConfig:
    def __init__(self, binary: str = "pylint"):
        self.binary = binary


def run_linter(config: MyLinterConfig, file_paths: List[str], **kwargs) -> int:
    if not file_paths:
        return 0

    try:
        result = subprocess.run(
            [config.binary, *file_paths],
            capture_output=True,
            text=True,
        )
        print(result.stdout, end="")
        return result.returncode
    except FileNotFoundError:
        print(f"Error: {config.binary} not found")
        return 2
```

### Example 2: Formatter Adapter

```python
# my_formatter.py
import subprocess
from typing import List


class MyFormatterConfig:
    def __init__(self, binary: str = "black"):
        self.binary = binary


def run_linter(config: MyFormatterConfig, file_paths: List[str], **kwargs) -> int:
    if not file_paths:
        return 0

    try:
        result = subprocess.run(
            [config.binary, *file_paths],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout, end="")
        return result.returncode
    except FileNotFoundError:
        print(f"Error: {config.binary} not found")
        return 2
```

### Example 3: Custom Rule Checker

```python
# copyright_checker.py
from typing import List
from pathlib import Path


class CopyrightConfig:
    def __init__(self, expected_year: str = "2026"):
        self.expected_year = expected_year


def run_linter(config: CopyrightConfig, file_paths: List[str], **kwargs) -> int:
    issues_found = False

    for file_path in file_paths:
        path = Path(file_path)
        content = path.read_text()

        if f"Copyright {config.expected_year}" not in content:
            print(f"{file_path}: Missing copyright notice")
            issues_found = True

    return 1 if issues_found else 0
```

---

## Checklist

When creating a new adapter, verify:

- [ ] Core implementation (`my_linter.py`)
  - [ ] Config class created
  - [ ] `run_linter()` function implemented
  - [ ] Proper error handling (FileNotFoundError, Timeout)
  - [ ] Return codes: 0 (success), 1 (issues), 2 (error)

- [ ] Entry point (`my_linter_linter.py`)
  - [ ] Argument parser created
  - [ ] All config options exposed
  - [ ] `main()` function returns exit code

- [ ] Tests (`tests/test_my_linter.py`)
  - [ ] Config tests
  - [ ] Success path tests
  - [ ] Error handling tests
  - [ ] 80%+ coverage

- [ ] Integration
  - [ ] `.lintrunner.toml` configuration
  - [ ] Documented in README.md
  - [ ] Added to adapter reference table

- [ ] Documentation
  - [ ] Adapter description in README
  - [ ] Configuration examples
  - [ ] Troubleshooting guide (if needed)

---

## Next Steps

1. Copy this template and customize for your linter
2. Implement core logic in `run_linter()`
3. Write comprehensive tests
4. Add to `.lintrunner.toml`
5. Submit PR with documentation

---

## Support

- 💬 [GitHub Discussions](https://github.com/KhwarizmiAnalytix/lint-tool/discussions)
- 🐛 [GitHub Issues](https://github.com/KhwarizmiAnalytix/lint-tool/issues)
- 📧 Email: contact@khwarizmianalytix.dev

---

**Happy adapter development! 🛠️**
