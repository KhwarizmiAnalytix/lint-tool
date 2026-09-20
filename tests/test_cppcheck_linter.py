from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from lint_tool.adapters import cppcheck_linter as cc


def _proc(
    stdout: bytes = b"", returncode: int = 0
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=b""
    )


def test_build_command_without_build_dir_passes_files_directly() -> None:
    cmd = cc.build_command("cppcheck", ["a.cpp", "b.cpp"], None, cc.DEFAULT_CHECKS)
    assert cmd[0] == "cppcheck"
    assert f"--enable={cc.DEFAULT_CHECKS}" in cmd
    assert cmd[-2:] == ["a.cpp", "b.cpp"]
    assert not any(arg.startswith("--project=") for arg in cmd)


def test_build_command_with_build_dir_uses_project_mode(tmp_path: Path) -> None:
    (tmp_path / "compile_commands.json").write_text("[]")
    cmd = cc.build_command("cppcheck", ["a.cpp"], tmp_path, cc.DEFAULT_CHECKS)
    assert f"--project={tmp_path / 'compile_commands.json'}" in cmd
    assert "a.cpp" not in cmd
    assert not any(arg.startswith("--enable=") for arg in cmd)


def test_parse_results_maps_severities() -> None:
    output = (
        "foo.cpp:10:5: error: crash [nullPointer]\n"
        "foo.cpp:20:0: style: unused var [unusedVariable]\n"
        "nofile:0:0: information: something [checkersReport]\n"
    )
    messages = cc.parse_results(output, wanted=None)
    assert len(messages) == 2
    assert messages[0].severity is cc.LintSeverity.ERROR
    assert messages[0].line == 10
    assert messages[0].char == 5
    assert messages[0].name == "[nullPointer]"
    assert messages[1].severity is cc.LintSeverity.ADVICE
    assert messages[1].char is None  # column 0 means "unknown"


def test_parse_results_filters_to_wanted_files(tmp_path: Path) -> None:
    target = tmp_path / "foo.cpp"
    target.write_text("")
    other = tmp_path / "bar.cpp"
    other.write_text("")
    output = f"{target}:1:1: warning: msg [x]\n{other}:2:2: warning: msg [y]\n"
    messages = cc.parse_results(output, wanted={str(target.resolve())})
    assert len(messages) == 1
    assert messages[0].path == str(target)


def test_check_files_reports_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(args: list[str]) -> subprocess.CompletedProcess[bytes]:
        raise OSError("no such file")

    monkeypatch.setattr(cc, "run_command", boom)
    messages = cc.check_files(["a.cpp"], "cppcheck", None, cc.DEFAULT_CHECKS)
    assert len(messages) == 1
    assert messages[0].name == "command-failed"
    assert messages[0].severity is cc.LintSeverity.ERROR


def test_check_files_parses_successful_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cc, "run_command", lambda args: _proc(stdout=b"a.cpp:1:1: warning: msg [x]\n")
    )
    messages = cc.check_files(["a.cpp"], "cppcheck", None, cc.DEFAULT_CHECKS)
    assert len(messages) == 1
    assert messages[0].severity is cc.LintSeverity.WARNING
    assert messages[0].path == "a.cpp"
