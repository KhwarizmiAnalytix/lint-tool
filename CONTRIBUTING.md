# Contributing to lint-tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the lint-tool project.

## Code of Conduct

We are committed to providing a welcoming and inspiring community. Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please file an issue on [GitHub Issues](https://github.com/KhwarizmiAnalytix/lint-tool/issues).

**Include:**
- Python version (`python3 --version`)
- Operating system
- Adapter being used
- Minimal reproducible example
- Expected vs. actual behavior

### 2. Suggest Features

Have an idea for a new adapter or improvement? [Start a discussion](https://github.com/KhwarizmiAnalytix/lint-tool/discussions).

**Include:**
- Use case and motivation
- Proposed solution
- Alternative approaches considered
- Potential impact

### 3. Write Code

### 4. Improve Documentation

Typos, unclear explanations, or missing examples? Documentation improvements are always welcome.

## Development Setup

```bash
git clone https://github.com/KhwarizmiAnalytix/lint-tool.git
cd lint-tool
pip install -e ".[test]"
```

## Development Workflow

### 1. Create a branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

### 2. Make your changes

Follow the code style and conventions in the existing code.

### 3. Run tests

```bash
pytest tests/
pytest tests/ -k specific_test  # Run specific test
pytest --cov=lint_tool tests/   # With coverage
```

### 4. Run linters

```bash
lintrunner lint   # All linters
ruff check .      # Python linting
mypy src/         # Type checking
```

### 5. Commit

```bash
git add <files>
git commit -m "Descriptive commit message"
```

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` testing
- `refactor:` code restructuring
- `perf:` performance improvement
- `chore:` maintenance

### 6. Push and create PR

```bash
git push origin feature/your-feature-name
```

Then [create a Pull Request](https://github.com/KhwarizmiAnalytix/lint-tool/pulls) on GitHub.

## Code Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where applicable
- Keep functions focused and single-purpose
- Write docstrings for public functions

### Naming Conventions

- `CamelCase` for classes
- `snake_case` for functions and variables
- `UPPER_CASE` for constants

## Adding a New Adapter

### 1. Create adapter module

```python
# src/lint_tool/adapters/my_linter.py

import json
import subprocess
from typing import List


class MyLinterConfig:
    def __init__(self, binary: str = "my-linter"):
        self.binary = binary


def run_linter(
    config: MyLinterConfig,
    file_paths: List[str],
    **kwargs
) -> int:
    """Run my-linter on files."""
    if not file_paths:
        return 0
    
    try:
        result = subprocess.run(
            [config.binary, *file_paths],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, end="")
        return result.returncode
    except FileNotFoundError:
        print(f"Error: {config.binary} not found")
        return 1
    except Exception as e:
        print(f"Error running {config.binary}: {e}")
        return 1
```

### 2. Create adapter entry point

```python
# src/lint_tool/adapters/my_linter_linter.py

import argparse
from . import my_linter


def main() -> int:
    parser = argparse.ArgumentParser(description="my-linter adapter")
    parser.add_argument("--binary", default="my-linter", help="Path to linter binary")
    parser.add_argument("files", nargs="*", help="Files to lint")
    
    args = parser.parse_args()
    config = my_linter.MyLinterConfig(binary=args.binary)
    return my_linter.run_linter(config, args.files)


if __name__ == "__main__":
    exit(main())
```

### 3. Add tests

```python
# tests/test_my_linter.py

import pytest
from lint_tool.adapters import my_linter


def test_basic_linting(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")
    
    config = my_linter.MyLinterConfig()
    result = my_linter.run_linter(config, [str(test_file)])
    
    assert isinstance(result, int)
    assert result in (0, 1)  # Success or failure
```

### 4. Update documentation

Add your adapter to [ADAPTERS.md](./docs/ADAPTERS.md) and README.md.

## Testing Guidelines

- Write tests for all new functionality
- Aim for >80% code coverage
- Test both success and failure cases
- Use fixtures for shared setup

```bash
# Check coverage
pytest --cov=lint_tool tests/
```

## Documentation Guidelines

- Write clear, concise documentation
- Include examples for all features
- Keep README.md updated
- Document breaking changes

## Pull Request Guidelines

### Before submitting:
- [ ] Tests pass locally (`pytest tests/`)
- [ ] Code is formatted (`ruff format .`)
- [ ] No type errors (`mypy src/`)
- [ ] Linters pass (`lintrunner lint`)
- [ ] Commit messages are clear
- [ ] Documentation is updated

### PR Title Format

Use clear, descriptive titles following Conventional Commits:
- `feat: add RUFF adapter`
- `fix: handle missing binary gracefully`
- `docs: update configuration guide`

### PR Description

Include:
- What problem does this solve?
- How does your solution work?
- What testing was done?
- Any breaking changes?

## Review Process

- All PRs require at least one approval
- Maintainers will provide feedback within 48 hours
- Be responsive to requested changes
- Tests must pass before merge

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release notes
4. Tag release in Git
5. Publish to PyPI

## License

By contributing, you agree that your code will be licensed under [GPL-3.0-or-later](LICENSE).

## Questions?

- 💬 [GitHub Discussions](https://github.com/KhwarizmiAnalytix/lint-tool/discussions)
- 🐛 [GitHub Issues](https://github.com/KhwarizmiAnalytix/lint-tool/issues)
- 📧 Email: contact@khwarizmianalytix.dev

## Acknowledgments

Thank you for contributing to lint-tool! 🎉
