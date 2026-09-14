"""Discover the consumer repository root without assuming an XSigma layout.

Adapters used to compute the repo as ``Path(__file__).parents[3]``, which is
only true while they live at ``<repo>/Tools/linter/adapters``. Walk from cwd
(or ``LINTRUNNER_HOST_ROOT``) instead so the same scripts work from a pip
install later.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path


HOST_ROOT_ENV = "LINTRUNNER_HOST_ROOT"
COMPILE_COMMANDS_DIR_ENV = "COMPILE_COMMANDS_DIR"
_WALK_LIMIT = 16
_ROOT_MARKERS = (".lintrunner.toml", ".git")
_BUILD_GLOBS = ("build_ninja*", "build", "build_*", "out", "cmake-build-*")
_HEADER_SOURCE_DIRS = (
    "Library",
    "Cmake",
    "Tools",
    "Examples",
    "src",
    "include",
    "lib",
)


def _walk_for(start: Path, name: str) -> Path | None:
    current = start
    for _ in range(_WALK_LIMIT):
        if (current / name).exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


@lru_cache(maxsize=1)
def host_root() -> Path:
    """Return the host repository root.

    Order: ``LINTRUNNER_HOST_ROOT`` if it names an existing directory, else
    the nearest ancestor of cwd that contains ``.lintrunner.toml``, else the
    nearest ancestor with ``.git``, else cwd.
    """
    env = os.environ.get(HOST_ROOT_ENV)
    if env:
        env_path = Path(env).expanduser().resolve()
        if env_path.is_dir():
            return env_path

    start = Path.cwd().resolve()
    for marker in _ROOT_MARKERS:
        found = _walk_for(start, marker)
        if found is not None:
            return found
    return start


def compile_commands_dir(preferred: str | None = None) -> Path | None:
    """Directory that contains ``compile_commands.json``, or None.

    Honors an explicit ``preferred`` path, then ``COMPILE_COMMANDS_DIR``, then
    the newest matching top-level build directory under the host root.
    """
    root = host_root()

    def _if_has_db(path: Path) -> Path | None:
        if (path / "compile_commands.json").is_file():
            return path
        if path.name == "compile_commands.json" and path.is_file():
            return path.parent
        return None

    if preferred:
        preferred_path = Path(preferred)
        if not preferred_path.is_absolute():
            preferred_path = root / preferred_path
        found = _if_has_db(preferred_path)
        if found is not None:
            return found

    env = os.environ.get(COMPILE_COMMANDS_DIR_ENV)
    if env:
        found = _if_has_db(Path(env).expanduser().resolve())
        if found is not None:
            return found

    candidates: list[Path] = []
    seen: set[Path] = set()
    for pattern in _BUILD_GLOBS:
        for entry in root.glob(pattern):
            resolved = entry.resolve()
            if resolved in seen or not entry.is_dir():
                continue
            seen.add(resolved)
            if (entry / "compile_commands.json").is_file():
                candidates.append(entry)
    if candidates:
        return max(
            candidates,
            key=lambda p: (p / "compile_commands.json").stat().st_mtime,
        )

    return _if_has_db(root)


def header_filter_regex() -> str:
    """clang-tidy ``--header-filter`` covering host source trees that exist."""
    root = host_root()
    existing = [
        name for name in _HEADER_SOURCE_DIRS if (root / name).is_dir()
    ]
    escaped_root = re.escape(str(root))
    if not existing:
        return f"^{escaped_root}/.*"
    joined = "|".join(re.escape(name) for name in existing)
    return f"^{escaped_root}/({joined})/.*"
