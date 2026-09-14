from __future__ import annotations

from pathlib import Path

import pytest

from lint_tool.adapters._linter.host import (
    compile_commands_dir,
    header_filter_regex,
    host_root,
)
from lint_tool.adapters.s3_init import packaged_s3_config


def test_host_root_prefers_lintrunner_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    host = tmp_path / "repo"
    nested = host / "src"
    nested.mkdir(parents=True)
    (host / ".lintrunner.toml").write_text("[[linter]]\n")
    monkeypatch.chdir(nested)
    host_root.cache_clear()
    assert host_root() == host.resolve()
    host_root.cache_clear()


def test_host_root_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LINTRUNNER_HOST_ROOT", str(tmp_path))
    host_root.cache_clear()
    assert host_root() == tmp_path.resolve()
    monkeypatch.delenv("LINTRUNNER_HOST_ROOT")
    host_root.cache_clear()


def test_compile_commands_dir_explicit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LINTRUNNER_HOST_ROOT", str(tmp_path))
    host_root.cache_clear()
    build = tmp_path / "build"
    build.mkdir()
    (build / "compile_commands.json").write_text("[]")
    assert compile_commands_dir(str(build)) == build
    host_root.cache_clear()


def test_header_filter_uses_existing_source_dirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LINTRUNNER_HOST_ROOT", str(tmp_path))
    (tmp_path / "src").mkdir()
    (tmp_path / "include").mkdir()
    host_root.cache_clear()
    pattern = header_filter_regex()
    assert "src" in pattern
    assert "include" in pattern
    assert "Library" not in pattern
    host_root.cache_clear()


def test_packaged_s3_config_has_clang_format() -> None:
    config = packaged_s3_config()
    assert "clang-format" in config
    assert "download_url" in next(iter(config["clang-format"].values()))


def test_import_allowlist_adapter_imports() -> None:
    from lint_tool.adapters import import_linter
    from lint_tool.adapters import pip_init

    assert callable(pip_init.main)
    assert hasattr(import_linter, "check_file")
