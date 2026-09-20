from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from lint_tool.adapters._linter.host import compile_commands_dir


LINTER_CODE = "IWYU"

ADD_HEADER_RE = re.compile(r"^(?P<file>.+?) should add these lines:$")
REMOVE_HEADER_RE = re.compile(r"^(?P<file>.+?) should remove these lines:$")
FULL_LIST_RE = re.compile(r"^The full include-list for (?P<file>.+?):$")
REMOVE_LINE_RE = re.compile(
    r"""(?x)
    ^-\s*
    (?P<include>\#include\s*[<"][^>"]+[>"])
    (?:\s*//\s*lines\s+(?P<start>\d+)-(?P<end>\d+))?
    \s*$
    """
)


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


def parse_report(report_text: str, filename: str) -> list[LintMessage]:
    """Parse IWYU's "should add"/"should remove" report for one file.

    The "full include-list" section is informational (it repeats every
    include the file would end up with) and is intentionally skipped.
    """
    lint_messages: list[LintMessage] = []
    mode: str | None = None
    for raw_line in report_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.strip() == "---":
            mode = None
            continue
        if ADD_HEADER_RE.match(line):
            mode = "add"
            continue
        if REMOVE_HEADER_RE.match(line):
            mode = "remove"
            continue
        if FULL_LIST_RE.match(line):
            mode = "full"
            continue
        if mode == "add":
            lint_messages.append(
                LintMessage(
                    path=filename,
                    line=None,
                    char=None,
                    code=LINTER_CODE,
                    severity=LintSeverity.WARNING,
                    name="missing-include",
                    original=None,
                    replacement=None,
                    description=f"Should add: {line.strip()}",
                )
            )
        elif mode == "remove":
            match = REMOVE_LINE_RE.match(line)
            if match is None:
                continue
            lint_messages.append(
                LintMessage(
                    path=filename,
                    line=int(match["start"]) if match["start"] else None,
                    char=None,
                    code=LINTER_CODE,
                    severity=LintSeverity.WARNING,
                    name="extra-include",
                    original=None,
                    replacement=None,
                    description=f"Should remove: {match['include']}",
                )
            )
        # mode == "full" (or None): nothing to report.
    return lint_messages


def check_file(
    filename: str,
    binary: str,
    build_dir: Path,
    extra_args: list[str],
) -> list[LintMessage]:
    try:
        proc = run_command(
            [binary, f"-p={build_dir}", *extra_args, filename],
        )
    except OSError as err:
        return [
            LintMessage(
                path=filename,
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

    # include-what-you-use writes its report to stderr.
    report_text = proc.stderr.decode(errors="replace")
    lint_messages = parse_report(report_text, filename)

    # A nonzero exit with no recognizable report section means IWYU could
    # not actually analyze the file (e.g. a real compile error from a stale
    # or narrow compile_commands.json), not that it found nothing to change.
    if not lint_messages and proc.returncode != 0:
        lint_messages.append(
            LintMessage(
                path=filename,
                line=None,
                char=None,
                code=LINTER_CODE,
                severity=LintSeverity.ERROR,
                name="compile-error",
                original=None,
                replacement=None,
                description=(
                    f"include-what-you-use exited {proc.returncode} analyzing "
                    f"this file using {build_dir}/compile_commands.json, with "
                    "no add/remove suggestions parsed -- results are not "
                    "trustworthy. This usually means the compilation database "
                    "is stale or missing an entry for this file. Raw output:\n\n"
                    + (
                        report_text.strip()
                        + "\n"
                        + proc.stdout.decode(errors="replace").strip()
                    ).strip()
                ),
            )
        )
    return lint_messages


def main() -> None:
    parser = argparse.ArgumentParser(
        description="include-what-you-use wrapper linter.",
        fromfile_prefix_chars="@",
    )
    parser.add_argument(
        "--binary",
        default="include-what-you-use",
        help="include-what-you-use binary path",
    )
    parser.add_argument(
        "--build-dir",
        "--build_dir",
        default=None,
        help=(
            "Where the compile_commands.json file is located. Gets passed to "
            "include-what-you-use -p. Optional: if omitted, auto-detects the "
            "newest top-level build directory under the host root that has "
            "one."
        ),
    )
    parser.add_argument(
        "--mapping-file",
        "--mapping_file",
        default=None,
        help="optional IWYU mapping file (forwarded as -Xiwyu --mapping_file=...)",
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

    # Resolved via PATH for the same reason as clang-tidy: IWYU is a
    # clang-based tool whose builtin headers must match the toolchain that
    # actually produced compile_commands.json.
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
                f"Could not find include-what-you-use binary '{args.binary}' "
                "on PATH (or as a literal file path). Install IWYU from the "
                "same LLVM/Clang toolchain used to build this repo, or pass "
                "--binary pointing at a specific executable."
            ),
        )
        print(json.dumps(err_msg._asdict()), flush=True)
        sys.exit(0)

    build_dir = compile_commands_dir(args.build_dir)
    if build_dir is None:
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
                "No directory with a compile_commands.json was found"
                + (
                    f" (and '{args.build_dir}' has none either)"
                    if args.build_dir
                    else ""
                )
                + ". Configure/build first so a compilation database exists."
            ),
        )
        print(json.dumps(err_msg._asdict()), flush=True)
        sys.exit(0)

    logging.info("Using build directory: %s", build_dir)
    extra_args = []
    if args.mapping_file:
        extra_args += ["-Xiwyu", f"--mapping_file={args.mapping_file}"]

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=os.cpu_count(),
        thread_name_prefix="Thread",
    ) as executor:
        futures = {
            executor.submit(
                check_file,
                filename,
                os.path.abspath(resolved_binary),
                build_dir.resolve(),
                extra_args,
            ): filename
            for filename in args.filenames
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                for lint_message in future.result():
                    print(json.dumps(lint_message._asdict()), flush=True)
            except Exception:
                logging.critical('Failed at "%s".', futures[future])
                raise


if __name__ == "__main__":
    main()
