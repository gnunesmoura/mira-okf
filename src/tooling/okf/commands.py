from __future__ import annotations

import sys
from argparse import Namespace


def command_stub(args: Namespace) -> int:
    print(f"tooling okf {args.okf_command} is not implemented yet.", file=sys.stderr)
    return 1

