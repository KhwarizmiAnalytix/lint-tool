# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2026.9.14] - 2026-09-24

### Added
- Comprehensive production-ready README with usage guide
- 32 linting adapters across C++, Python, CMake, CI/CD categories
- Contributing guidelines and development workflow documentation
- Security policy and responsible disclosure process
- Example `.lintrunner.toml` configurations for minimal and comprehensive setups
- Troubleshooting guide for common issues
- API reference for programmatic usage
- Support for Python 3.9, 3.10, 3.11, 3.12

### Features
- **C++ Tools**: CLANGFORMAT, CLANGTIDY, CMAKE, CMAKEFORMAT, CMAKE_MINIMUM_REQUIRED
- **Python Linting**: FLAKE8, MYPY, MYPYSTRICT, RUFF, PYFMT, PYREFLY
- **Type/Import Checking**: IMPORT_LINTER, DOCSTRING_LINTER, TYPEIGNORE, TYPENOSKIP
- **Text Quality**: CODESPELL, NEWLINE, SPACES, TABS
- **Configuration**: EDITORCONFIG, PYPROJECT, TPINCLUDE, COPYRIGHT
- **CI/CD**: GHA, ACTIONLINT, SHELLCHECK, EXEC, BAZEL_LINTER
- **Specialized**: ROOT_LOGGING, NOQA, PYPIDEP, LINTRUNNER_VERSION

### Changed
- Updated documentation structure for production use
- Enhanced error messages with actionable suggestions
- Improved compatibility matrix for external tools

### Fixed
- Handle missing linter binaries gracefully
- Improved path resolution for repository root detection
- Better handling of DRYRUN mode across all adapters

### Documented
- Production deployment recommendations
- CI/CD integration patterns
- Custom adapter development guide

## [2026.8.x] - Prior Release

See [GitHub Releases](https://github.com/KhwarizmiAnalytix/lint-tool/releases) for earlier versions.

## Future

### Planned
- [ ] WebAssembly support for linters
- [ ] Plugin system for custom rules
- [ ] Distributed linting support
- [ ] Real-time linting in IDEs
- [ ] Performance profiling and optimization
- [ ] Enhanced reporting formats (HTML, JSON, CSV)

### Under Consideration
- Windows PowerShell script adapters
- Docker image with pre-configured tools
- Integration with pre-commit framework
- Machine learning-based anomaly detection

---

## How to Report Issues

- 🐛 **Bug**: [GitHub Issues](https://github.com/KhwarizmiAnalytix/lint-tool/issues)
- 💡 **Feature Request**: [GitHub Discussions](https://github.com/KhwarizmiAnalytix/lint-tool/discussions)
- 🔒 **Security**: security@khwarizmianalytix.dev

## Versioning Scheme

This project uses calendar versioning: `YYYY.M.DD[+patch]`

- `2026.9.14` - September 14, 2026
- `2026.9.14+1` - Patch release

## Compatibility

| Version | Python | Status |
|---------|--------|--------|
| 2026.9+ | 3.9+ | ✅ Supported |
| 2026.8 | 3.9+ | ⚠️ Security updates only |
| <2026.8 | 3.9+ | ❌ Unsupported |

## Migration Guide

### From 2026.8 → 2026.9

No breaking changes. Update with:

```bash
pip install --upgrade lint-tool
```

All existing configurations remain compatible.

### From Earlier Versions

Refer to [MIGRATION.md](./docs/MIGRATION.md) for upgrade paths.

---

**For the latest updates, visit:** https://github.com/KhwarizmiAnalytix/lint-tool/releases
