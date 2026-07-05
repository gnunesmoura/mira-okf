from __future__ import annotations

import sys
from argparse import Namespace

from .links import run_backlinks, run_links
from .listing import run_list
from .tree import run_tree


def command_stub(args: Namespace) -> int:
    if args.okf_command == "tree":
        return run_tree(args)
    if args.okf_command == "list":
        return run_list(args)
    if args.okf_command == "links":
        return run_links(args)
    if args.okf_command == "backlinks":
        return run_backlinks(args)
    print(f"tooling okf {args.okf_command} is not implemented yet.", file=sys.stderr)
    return 1
