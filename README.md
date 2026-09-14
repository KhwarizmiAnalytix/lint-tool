# lint-tool

lintrunner adapters for C++/Python/CMake repositories. Host repos own
policy (`.lintrunner.toml`, `.clang-format`, `pyproject.toml`); this
package owns the adapter implementations.

```bash
pip install lint-tool
```

Invoke adapters through lintrunner:

```toml
[[linter]]
code = 'CLANGFORMAT'
include_patterns = ['**/*.cpp', '**/*.h']
exclude_patterns = ['ThirdParty/**']
command = [
    'python3',
    '-m',
    'lint_tool.adapters.clangformat_linter',
    '--binary=clang-format',
    '--',
    '@{{PATHSFILE}}',
]
init_command = [
    'python3',
    '-m',
    'lint_tool.adapters.pip_init',
    '--dry-run={{DRYRUN}}',
    'clang-format==19.1.4',
]
```

Adapters find the consumer root by walking up from cwd for
`.lintrunner.toml` or `.git`, or from `LINTRUNNER_HOST_ROOT`. They do not
assume an XSigma `Tools/linter/adapters` layout.

A Logging/Parallel-sized menu is typically CLANGFORMAT, CMAKE,
CMAKEFORMAT, EDITORCONFIG, NEWLINE, and CODESPELL. Do not copy a full
XSigma `.lintrunner.toml`.

```bash
python3 -m lint_tool                 # list usage
python3 -m lint_tool.adapters.ruff_linter --help
python3 -m pytest tests/             # from a clone, after pip install -e ".[test]"
```

Source: https://github.com/KhwarizmiAnalytix/lint-tool
