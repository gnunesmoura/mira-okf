from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__
from .okf.commands import command_stub


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tooling")
    parser.add_argument("--version", action="version", version=f"tooling {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    okf_parser = subparsers.add_parser("okf", help="OKF bundle commands.")
    okf_subparsers = okf_parser.add_subparsers(dest="okf_command", required=True)

    for name, help_text, arguments in (
        ("tree", "Show a summarized bundle tree.", (("--depth", {"type": int, "default": 2}), ("--summary", {"action": "store_true"}), ("--json", {"action": "store_true"}))),
        ("list", "List concepts in a bundle.", (("--type", {}), ("--tag", {}), ("--json", {"action": "store_true"}))),
        ("show", "Show a single concept.", (("--summary", {"action": "store_true"}), ("--json", {"action": "store_true"}))),
    ):
        command_parser = okf_subparsers.add_parser(name, help=help_text)
        command_parser.add_argument("bundle", nargs="?")
        for flag, kwargs in arguments:
            command_parser.add_argument(flag, **kwargs)
        command_parser.set_defaults(handler=command_stub)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        return 0
    return handler(args)
