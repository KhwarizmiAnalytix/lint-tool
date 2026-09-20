"""
Checks files to make sure there are no imports from disallowed third party
libraries.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import token
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple


_PARENT = Path(__file__).parent.absolute()
_PATH = [Path(p).absolute() for p in sys.path]

if TYPE_CHECKING or _PARENT not in _PATH:
    from . import _linter
else:
    import _linter


class LintSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    ADVICE = "advice"
    DISABLED = "disabled"


class LintMessage(NamedTuple):
    path: str | None
    line: int | None
    char: int | None
    code: str
    severity: LintSeverity
    name: str
    original: str | None
    replacement: str | None
    description: str | None


LINTER_CODE = "IMPORT_LINTER"
CURRENT_FILE_NAME = os.path.basename(__file__)
_MODULE_NAME_ALLOW_LIST: set[str] = set()


def _stdlib_module_names() -> frozenset[str]:
    """Names of every standard-library module.

    ``sys.stdlib_module_names`` only exists on 3.10+; on 3.9 approximate it
    by listing modules found in the interpreter's stdlib directory, which
    covers the same ground without adding a runtime dependency.
    """
    if hasattr(sys, "stdlib_module_names"):
        return frozenset(sys.stdlib_module_names)
    import pkgutil
    import sysconfig

    names = set(sys.builtin_module_names)
    stdlib_dir = sysconfig.get_paths().get("stdlib")
    if stdlib_dir:
        names.update(info.name for info in pkgutil.iter_modules([stdlib_dir]))
    return frozenset(names)


# Add builtin modules of python.
_MODULE_NAME_ALLOW_LIST.update(_stdlib_module_names())


def _load_pyproject() -> dict:
    pyproject = _linter.host_root() / "pyproject.toml"
    if not pyproject.is_file():
        return {}
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib  # type: ignore[import-not-found]
    try:
        loaded = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _host_import_allowlist() -> list[str]:
    extra = _load_pyproject().get("tool", {}).get("lint-tool", {}).get(
        "import-allowlist"
    )
    if isinstance(extra, list):
        return [name for name in extra if isinstance(name, str)]
    return []


# Host-owned third-party allowlist (see [tool.lint-tool] in pyproject.toml).
_MODULE_NAME_ALLOW_LIST.update(_host_import_allowlist())

_ERROR_MESSAGE = """
Please do not import third-party modules unless they are explicit requirements
of this project. Imports of a third-party library may have side effects and
other unintentional behavior. If you're just checking if a module exists, use
sys.modules.get("name") or the like.
"""


def check_file(filepath: str) -> list[LintMessage]:
    path = Path(filepath)
    file = _linter.PythonFile("import_linter", path)
    lint_messages = []
    for line_number, line_of_tokens in enumerate(file.token_lines):
        # Skip indents
        idx = 0
        for tok in line_of_tokens:
            if tok.type == token.INDENT:
                idx += 1
            else:
                break

        # Look for either "import foo..." or "from foo..."
        if idx + 1 < len(line_of_tokens):
            tok0 = line_of_tokens[idx]
            tok1 = line_of_tokens[idx + 1]
            if tok0.type == token.NAME and tok0.string in {"import", "from"}:
                if tok1.type == token.NAME:
                    module_name = tok1.string
                    if module_name not in _MODULE_NAME_ALLOW_LIST:
                        msg = LintMessage(
                            path=filepath,
                            line=line_number,
                            char=None,
                            code="IMPORT",
                            severity=LintSeverity.ERROR,
                            name="Disallowed import",
                            original=None,
                            replacement=None,
                            description=_ERROR_MESSAGE,
                        )
                        lint_messages.append(msg)
    return lint_messages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="native functions linter",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "filepaths",
        nargs="+",
        help="paths of files to lint",
    )
    args = parser.parse_args()

    # Check all files.
    all_lint_messages = []
    for filepath in args.filepaths:
        lint_messages = check_file(filepath)
        all_lint_messages.extend(lint_messages)

    # Print out lint messages.
    for lint_message in all_lint_messages:
        print(json.dumps(lint_message._asdict()), flush=True)
