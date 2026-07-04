from __future__ import annotations

import sys
from argparse import Namespace

from .listing import run_list
from .tree import run_tree


def command_stub(args: Namespace) -> int:
    if args.okf_command == "tree":
        return run_tree(args)
    if args.okf_command == "list":
        return run_list(args)
    print(f"tooling okf {args.okf_command} is not implemented yet.", file=sys.stderr)
    return 1
