from __future__ import annotations

import sys
from argparse import Namespace

from .health import run_health
from .links import run_backlinks, run_links
from .listing import run_list
from .validate import run_validate
from .show import run_show
from .tree import run_tree


def command_stub(args: Namespace) -> int:
    if args.command == "tree":
        return run_tree(args)
    if args.command == "list":
        return run_list(args)
    if args.command == "show":
        return run_show(args)
    if args.command == "links":
        return run_links(args)
    if args.command == "backlinks":
        return run_backlinks(args)
    if args.command == "validate":
        return run_validate(args)
    if args.command == "health":
        return run_health(args)
    if args.command == "lint":
        from .lint import run_lint

        return run_lint(args)
    if args.command == "props":
        from .props import run_props

        return run_props(args)
    print(f"mira-okf {args.command} is not implemented yet.", file=sys.stderr)
    return 1
