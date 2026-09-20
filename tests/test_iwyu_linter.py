from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from lint_tool.adapters import iwyu_linter as iwyu


def _proc(
    stdout: bytes = b"", stderr: bytes = b"", returncode: int = 0
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


SAMPLE_REPORT = """\
foo.cpp should add these lines:
#include <string>  // for std::string

foo.cpp should remove these lines:
- #include <map>  // lines 10-10
- #include <vector>

The full include-list for foo.cpp:
#include <string>  // for std::string
#include "foo.h"  // for Foo
---
"""


def test_parse_report_extracts_add_and_remove() -> None:
    messages = iwyu.parse_report(SAMPLE_REPORT, "foo.cpp")
    adds = [m for m in messages if m.name == "missing-include"]
    removes = [m for m in messages if m.name == "extra-include"]
    assert len(adds) == 1
    assert "string" in adds[0].description
    assert adds[0].line is None
    assert len(removes) == 2
    assert removes[0].line == 10
    assert "map" in removes[0].description
    assert removes[1].line is None  # no "// lines" comment present


def test_parse_report_skips_full_include_list_section() -> None:
    messages = iwyu.parse_report(SAMPLE_REPORT, "foo.cpp")
    assert not any("foo.h" in (m.description or "") for m in messages)


def test_parse_report_empty_when_nothing_reported() -> None:
    assert iwyu.parse_report("", "foo.cpp") == []


def test_check_file_reports_oserror(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def boom(args: list[str]) -> subprocess.CompletedProcess[bytes]:
        raise OSError("not found")

    monkeypatch.setattr(iwyu, "run_command", boom)
    messages = iwyu.check_file("foo.cpp", "include-what-you-use", tmp_path, [])
    assert len(messages) == 1
    assert messages[0].name == "command-failed"


def test_check_file_parses_successful_report(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        iwyu,
        "run_command",
        lambda args: _proc(stderr=SAMPLE_REPORT.encode(), returncode=0),
    )
    messages = iwyu.check_file("foo.cpp", "include-what-you-use", tmp_path, [])
    assert len(messages) == 3  # 1 add + 2 remove


def test_check_file_surfaces_compile_error_when_nothing_parsed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        iwyu,
        "run_command",
        lambda args: _proc(stderr=b"clang: error: file not found\n", returncode=1),
    )
    messages = iwyu.check_file("foo.cpp", "include-what-you-use", tmp_path, [])
    assert len(messages) == 1
    assert messages[0].name == "compile-error"
    assert messages[0].severity is iwyu.LintSeverity.ERROR


def test_check_file_clean_result_when_zero_exit_and_no_report(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(iwyu, "run_command", lambda args: _proc(returncode=0))
    messages = iwyu.check_file("foo.cpp", "include-what-you-use", tmp_path, [])
    assert messages == []
