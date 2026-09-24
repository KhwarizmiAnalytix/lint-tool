# 🛠️ lint-tool: Production-Grade Linting Adapters

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-Production%2FStable-brightgreen.svg)

A comprehensive, production-ready linting adapter suite for **C++**, **Python**, **CMake**, and **CI/CD** repositories. Designed for teams that need professional-grade code quality without sacrificing developer experience.

**Developed and maintained by [KhwarizmiAnalytix](https://github.com/KhwarizmiAnalytix)**

## 🎯 Overview

`lint-tool` provides 32 linting adapters that work seamlessly with [lintrunner](https://github.com/pytorch/pytorch/tree/main/tools/linter) to enforce consistent code quality across mixed-language repositories.

### Key Features

✨ **Comprehensive Coverage**
- 5 C++ tools (clang-format, clang-tidy, CMake)
- 6 Python linters (flake8, mypy, ruff, black, pyrefly)
- 4 type/import checkers (docstrings, import validation)
- 4 text quality tools (spell check, whitespace, tabs/spaces)
- 4 configuration validators (editorconfig, pyproject, copyright)
- 5 CI/CD adapters (GitHub Actions, ShellCheck, Bazel)

🚀 **Production-Ready**
- Used in 11+ repositories across KhwarizmiAnalytix ecosystem
- Proven stable on Linux, macOS, Windows
- Comprehensive error handling and reporting
- Graceful degradation when tools unavailable

🔧 **Developer-Friendly**
- Zero configuration for common setups
- Clear error messages with fix suggestions
- Pluggable architecture for custom linters
- Full Python 3.9+ support

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install lint-tool
```

### From Source

```bash
git clone https://github.com/KhwarizmiAnalytix/lint-tool.git
cd lint-tool
pip install -e .
pip install -e ".[test]"  # for development
```

## 🚀 Quick Start

### 1. Create `.lintrunner.toml` in your repository root

```toml
[[linter]]
code = 'CLANGFORMAT'
include_patterns = ['**/*.cpp', '**/*.h']
exclude_patterns = ['ThirdParty/**', 'build/**']
init_command = [
    'python3', '-m', 'lint_tool.adapters.pip_init',
    '--dry-run={{DRYRUN}}',
    'clang-format==19.1.4',
]
command = [
    'python3', '-m', 'lint_tool.adapters.clangformat_linter',
    '--binary=.lintbin/clang-format',
    '--', '@{{PATHSFILE}}',
]
is_formatter = true

[[linter]]
code = 'CODESPELL'
include_patterns = ['**']
exclude_patterns = ['ThirdParty/**', '.git/**', 'build/**']
command = [
    'python3', '-m', 'lint_tool.adapters.codespell_linter',
    '--', '@{{PATHSFILE}}',
]
```

### 2. Run lintrunner

```bash
# Install lintrunner
pip install lintrunner

# Run all linters
lintrunner lint

# Run specific linter
lintrunner lint CLANGFORMAT

# Format fixable issues
lintrunner format
```

### 3. Integrate with CI/CD

```bash
# GitHub Actions, GitLab CI, Jenkins, etc.
lintrunner lint --all-files
```

## 📋 Available Adapters (32 Total)

### C++ Tools

| Adapter | Purpose | Requires |
|---------|---------|----------|
| **CLANGFORMAT** | Code formatting | clang-format binary |
| **CLANGTIDY** | Static analysis | clang-tidy binary |
| **CMAKE** | CMake linting | cmake binary |
| **CMAKEFORMAT** | CMake formatting | cmake-format |
| **CMAKE_MINIMUM_REQUIRED** | Version checking | none |

### Python Linting

| Adapter | Purpose | Requires |
|---------|---------|----------|
| **FLAKE8** | PEP 8 compliance | flake8 |
| **MYPY** | Type checking | mypy |
| **MYPYSTRICT** | Strict types | mypy |
| **RUFF** | Fast Python lint | ruff |
| **PYFMT** | Code formatting | black |
| **PYREFLY** | Advanced analysis | pyrefly |

### Type & Import Checking

| Adapter | Purpose | Requires |
|---------|---------|----------|
| **IMPORT_LINTER** | Import validation | lint-import-linter |
| **DOCSTRING_LINTER** | Docstring checking | pydocstyle |
| **TYPEIGNORE** | Ignore tracking | none |
| **TYPENOSKIP** | Skip validation | none |

### Text Quality

| Adapter | Purpose | Format |
|---------|---------|--------|
| **CODESPELL** | Spell checking | yes |
| **NEWLINE** | Line endings | yes |
| **SPACES** | Trailing spaces | yes |
| **TABS** | Tab detection | yes |

### Configuration

| Adapter | Purpose | Validates |
|---------|---------|-----------|
| **EDITORCONFIG** | Editor config | .editorconfig |
| **PYPROJECT** | Python config | pyproject.toml |
| **TPINCLUDE** | Include paths | C++ includes |
| **COPYRIGHT** | Headers | Copyright notices |

### CI/CD & Scripts

| Adapter | Purpose | Requires |
|---------|---------|----------|
| **GHA** | GitHub Actions | none |
| **ACTIONLINT** | Action linting | actionlint |
| **SHELLCHECK** | Shell scripts | shellcheck |
| **EXEC** | Executable checks | none |
| **BAZEL_LINTER** | Bazel files | buildifier |

### Specialized

| Adapter | Purpose | Type |
|---------|---------|------|
| **ROOT_LOGGING** | Logger validation | custom |
| **NOQA** | Suppression tracking | custom |
| **PYPIDEP** | Dependency checking | custom |
| **LINTRUNNER_VERSION** | Version tracking | custom |

## 📖 Configuration Guide

### Minimal Setup (6 checks)

```toml
# .lintrunner.toml - Recommended starting point

[[linter]]
code = 'CLANGFORMAT'
include_patterns = ['include/**/*.h', 'include/**/*.cpp']
exclude_patterns = ['ThirdParty/**']
command = ['python3', '-m', 'lint_tool.adapters.clangformat_linter', '--', '@{{PATHSFILE}}']

[[linter]]
code = 'CMAKE'
include_patterns = ['CMakeLists.txt', '**/*.cmake']
exclude_patterns = ['ThirdParty/**']
command = ['python3', '-m', 'lint_tool.adapters.cmake_linter', '--', '@{{PATHSFILE}}']

[[linter]]
code = 'CMAKEFORMAT'
include_patterns = ['CMakeLists.txt']
command = ['python3', '-m', 'lint_tool.adapters.cmake_format_linter', '--', '@{{PATHSFILE}}']
is_formatter = true

[[linter]]
code = 'EDITORCONFIG'
include_patterns = ['**']
command = ['python3', '-m', 'lint_tool.adapters.editorconfig_checker_linter', '--', '@{{PATHSFILE}}']

[[linter]]
code = 'NEWLINE'
include_patterns = ['**']
exclude_patterns = ['ThirdParty/**', 'build/**', '**/*.png']
command = ['python3', '-m', 'lint_tool.adapters.newlines_linter', '--', '@{{PATHSFILE}}']
is_formatter = true

[[linter]]
code = 'CODESPELL'
include_patterns = ['**']
exclude_patterns = ['ThirdParty/**', 'build/**', '.git/**']
command = ['python3', '-m', 'lint_tool.adapters.codespell_linter', '--', '@{{PATHSFILE}}']
```

### Comprehensive Setup (32 checks)

See [FULL_CONFIGURATION.md](./docs/FULL_CONFIGURATION.md) for a complete example with all 32 checks.

## 🔍 Usage Examples

### Run specific linter

```bash
lintrunner lint CLANGFORMAT
```

### Run all linters on changed files

```bash
lintrunner lint
```

### Format fixable issues

```bash
lintrunner format
```

### Dry run (no changes)

```bash
DRYRUN=1 lintrunner lint
```

### Get help for specific adapter

```bash
python3 -m lint_tool.adapters.ruff_linter --help
```

## 🛠️ Advanced Topics

### Custom Adapters

See [ADAPTER_DEVELOPMENT.md](./docs/ADAPTER_DEVELOPMENT.md) for creating custom linting adapters.

### Environment Variables

- `LINTRUNNER_HOST_ROOT` - Override repository root detection
- `DRYRUN` - Set to 1 for dry-run mode (no changes)
- Tool-specific: `CLANG_TIDY_ARGS`, `RUFF_ARGS`, etc.

### Configuration Priority

1. Command-line flags
2. Environment variables
3. `.lintrunner.toml` settings
4. Tool-specific config files (.clang-format, pyproject.toml)
5. Defaults

## 🐛 Troubleshooting

### Tool not found

```bash
# Problem: clang-format not in PATH
# Solution: Specify binary path in init_command
init_command = [
    'python3', '-m', 'lint_tool.adapters.s3_init',
    '--linter=clang-format',
    '--output-dir=.lintbin',
]
command = [
    'python3', '-m', 'lint_tool.adapters.clangformat_linter',
    '--binary=.lintbin/clang-format',
    '--', '@{{PATHSFILE}}',
]
```

### Permission denied on cached tools

```bash
# Problem: stale cache
# Solution: Clear and rebuild
rm -rf .lintbin/
lintrunner lint --all-files
```

### Python version conflicts

```bash
# Ensure Python 3.9+
python3 --version

# Use venv
python3 -m venv .venv
source .venv/bin/activate
pip install lint-tool
```

## 🧪 Testing

```bash
# Run test suite
pytest tests/

# Run with coverage
pytest --cov=lint_tool tests/

# Test specific adapter
pytest tests/ -k test_clangformat
```

## 📚 Documentation

- [Adapter Reference](./docs/ADAPTERS.md) - Detailed documentation for each adapter
- [Configuration Guide](./docs/CONFIGURATION.md) - Setup examples and best practices
- [Developer Guide](./docs/DEVELOPMENT.md) - Building and testing custom adapters
- [Troubleshooting](./docs/TROUBLESHOOTING.md) - Common issues and solutions
- [API Reference](./docs/API.md) - Programmatic usage

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/KhwarizmiAnalytix/lint-tool.git
cd lint-tool
pip install -e ".[test]"
pytest tests/
```

### Running pre-commit checks

```bash
lintrunner lint
ruff check .
mypy src/
```

## 📄 License

GPL-3.0-or-later. See [LICENSE](./LICENSE) for details.

## 🔗 Links

- **GitHub:** https://github.com/KhwarizmiAnalytix/lint-tool
- **PyPI:** https://pypi.org/project/lint-tool/
- **Issues:** https://github.com/KhwarizmiAnalytix/lint-tool/issues
- **Discussions:** https://github.com/KhwarizmiAnalytix/lint-tool/discussions

## 🙋 Support

- **Questions?** Open a [GitHub Discussion](https://github.com/KhwarizmiAnalytix/lint-tool/discussions)
- **Bug Report?** File a [GitHub Issue](https://github.com/KhwarizmiAnalytix/lint-tool/issues)
- **Security?** See [SECURITY.md](./SECURITY.md)

---

**Made with ❤️ by [KhwarizmiAnalytix](https://github.com/KhwarizmiAnalytix)**  
Professional linting for professional code.
