"""``python -m lint_tool`` prints how to invoke adapters."""

from __future__ import annotations

from lint_tool import __version__


def main() -> None:
    print(f"lint-tool {__version__}")
    print("Run an adapter with:")
    print("  python3 -m lint_tool.adapters.<name> --help")
    print("Examples: clangformat_linter, ruff_linter, pip_init, s3_init")


if __name__ == "__main__":
    main()
