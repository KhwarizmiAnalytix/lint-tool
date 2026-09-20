from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from lint_tool.adapters._linter.host import compile_commands_dir


LINTER_CODE = "CPPCHECK"

TEMPLATE = "{file}:{line}:{column}: {severity}: {message} [{id}]"

DEFAULT_CHECKS = "warning,style,performance,portability"


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


# Library/Core/Foo.cpp:42:5: warning: Variable 'x' is unused. [unreadVariable]
RESULTS_RE: re.Pattern[str] = re.compile(
    r"""(?mx)
    ^
    (?P<file>.*?):
    (?P<line>\d+):
    (?P<column>\d+):
    \s(?P<severity>\S+?):
    \s(?P<message>.*)
    \s(?P<code>\[.*\])
    $
    """
)

# cppcheck-native severities; anything else (style/performance/portability/
# information) is a suggestion rather than a hard failure.
severities = {
    "error": LintSeverity.ERROR,
    "warning": LintSeverity.WARNING,
}


def run_command(
    args: list[str],
) -> subprocess.CompletedProcess[bytes]:
    logging.debug("$ %s", " ".join(args))
    start_time = time.monotonic()
    try:
        return subprocess.run(
            args,
            capture_output=True,
            check=False,
        )
    finally:
        end_time = time.monotonic()
        logging.debug("took %dms", (end_time - start_time) * 1000)


def build_command(
    binary: str,
    filenames: list[str],
    build_dir: Path | None,
    checks: str,
) -> list[str]:
    cmd = [
        binary,
        "--quiet",
        "--inline-suppr",
        f"--template={TEMPLATE}",
    ]
    # cppcheck refuses --project together with explicit source files, so a
    # compilation database means analyzing the whole project and filtering
    # the report down to the requested paths afterward (same trick already
    # used by clangtidy_linter.py for headers).
    if build_dir is not None:
        cmd.append(f"--project={build_dir / 'compile_commands.json'}")
    else:
        cmd += [f"--enable={checks}", "--language=c++", *filenames]
    return cmd


def parse_results(stdout_text: str, wanted: set[str] | None) -> list[LintMessage]:
    lint_messages = []
    for match in RESULTS_RE.finditer(stdout_text):
        file = match["file"]
        if file in ("nofile", "-"):
            continue
        if wanted is not None and str(Path(file).resolve()) not in wanted:
            continue
        lint_messages.append(
            LintMessage(
                path=file,
                name=match["code"],
                description=match["message"],
                line=int(match["line"]),
                char=int(match["column"]) or None,
                code=LINTER_CODE,
                severity=severities.get(match["severity"], LintSeverity.ADVICE),
                original=None,
                replacement=None,
            )
        )
    return lint_messages


def check_files(
    filenames: list[str],
    binary: str,
    build_dir: Path | None,
    checks: str,
) -> list[LintMessage]:
    try:
        proc = run_command(build_command(binary, filenames, build_dir, checks))
    except OSError as err:
        return [
            LintMessage(
                path=None,
                line=None,
                char=None,
                code=LINTER_CODE,
                severity=LintSeverity.ERROR,
                name="command-failed",
                original=None,
                replacement=None,
                description=(f"Failed due to {err.__class__.__name__}:\n{err}"),
            )
        ]
    wanted = (
        {str(Path(f).resolve()) for f in filenames} if build_dir is not None else None
    )
    return parse_results(proc.stdout.decode(errors="replace"), wanted)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="cppcheck wrapper linter.",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "--binary",
        default="cppcheck",
        help="cppcheck binary path",
    )
    parser.add_argument(
        "--build-dir",
        "--build_dir",
        default=None,
        help=(
            "Directory with a compile_commands.json. Optional: when given (or "
            "auto-detected), cppcheck analyzes the whole compilation database "
            "and results are filtered down to the requested files for more "
            "accurate include/macro resolution. Without one, files are "
            "checked directly."
        ),
    )
    parser.add_argument(
        "--checks",
        default=DEFAULT_CHECKS,
        help="comma-separated cppcheck --enable checks (ignored with --build-dir)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="verbose logging",
    )
    parser.add_argument(
        "filenames",
        nargs="+",
        help="paths to lint",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="<%(threadName)s:%(levelname)s> %(message)s",
        level=logging.NOTSET
        if args.verbose
        else logging.DEBUG
        if len(args.filenames) < 1000
        else logging.INFO,
        stream=sys.stderr,
    )

    resolved_binary = shutil.which(args.binary)
    if resolved_binary is None:
        err_msg = LintMessage(
            path="<none>",
            line=None,
            char=None,
            code=LINTER_CODE,
            severity=LintSeverity.ERROR,
            name="command-failed",
            original=None,
            replacement=None,
            description=(
                f"Could not find cppcheck binary '{args.binary}' on PATH "
                "(or as a literal file path). Install cppcheck, or pass "
                "--binary pointing at a specific executable."
            ),
        )
        print(json.dumps(err_msg._asdict()), flush=True)
        sys.exit(0)

    build_dir = compile_commands_dir(args.build_dir)
    if build_dir is not None:
        logging.info("Using build directory: %s", build_dir)

    for lint_message in check_files(
        args.filenames, resolved_binary, build_dir, args.checks
    ):
        print(json.dumps(lint_message._asdict()), flush=True)


if __name__ == "__main__":
    main()
