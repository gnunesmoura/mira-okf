from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__
from .okf.commands import command_stub


def _non_negative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def _field_name(value: str) -> str:
    if not value.strip():
        raise argparse.ArgumentTypeError("field name must not be blank")
    return value


class _UniqueFieldAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        fields = getattr(namespace, self.dest, None) or []
        if values in fields:
            raise argparse.ArgumentError(self, f"field selected more than once: {values}")
        fields.append(values)
        setattr(namespace, self.dest, fields)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mira-okf")
    parser.add_argument("--version", action="version", version=f"mira-okf {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)
    okf_parser = subparsers.add_parser("okf", help="OKF bundle commands.")
    okf_subparsers = okf_parser.add_subparsers(dest="okf_command", required=True)

    for name, help_text, arguments in (
        ("tree", "Show a summarized bundle tree.", (("--depth", {"type": int, "default": 2}), ("--summary", {"action": "store_true"}), ("--json", {"action": "store_true"}))),
        (
            "list",
            "List concepts in a bundle.",
            (
                ("--type", {}),
                ("--tag", {}),
                ("--offset", {"type": _non_negative_int, "default": 0}),
                ("--limit", {"type": _non_negative_int}),
                ("--json", {"action": "store_true"}),
            ),
        ),
        ("show", "Show a single concept.", (("--summary", {"action": "store_true"}), ("--json", {"action": "store_true"}))),
        ("links", "List outbound links in a bundle.", (("--broken", {"action": "store_true"}), ("--external", {"action": "store_true"}), ("--json", {"action": "store_true"}))),
        ("backlinks", "List inbound links for a concept.", (("--json", {"action": "store_true"}),)),
        ("validate", "Validate bundle conformance.", (("--json", {"action": "store_true"}),)),
        ("health", "Report bundle health signals.", (("--profile", {"choices": ("quick", "full"), "default": "quick"}), ("--json", {"action": "store_true"}))),
        ("props", "Export concept properties.", (("--field", {"action": _UniqueFieldAction, "type": _field_name}), ("--json", {"action": "store_true"}))),
    ):
        command_parser = okf_subparsers.add_parser(name, help=help_text)
        command_parser.add_argument("bundle", nargs="?")
        if name == "backlinks":
            command_parser.add_argument("concept")
        elif name == "show":
            command_parser.add_argument("concept", nargs="?")
        for flag, kwargs in arguments:
            command_parser.add_argument(flag, **kwargs)
        command_parser.set_defaults(handler=command_stub)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "okf_command", None) == "show" and args.bundle is None and args.concept is None:
        parser.error("the following arguments are required: concept")
    handler = getattr(args, "handler", None)
    if handler is None:
        return 0
    return handler(args)
