from __future__ import annotations

import sys
from argparse import Namespace

from .tree import run_tree


def command_stub(args: Namespace) -> int:
    if args.okf_command == "tree":
        return run_tree(args)
    print(f"tooling okf {args.okf_command} is not implemented yet.", file=sys.stderr)
    return 1
