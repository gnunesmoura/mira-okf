from __future__ import annotations

import argparse
import unittest
from unittest import mock

from tooling.cli import build_parser
from tooling.okf.commands import command_stub


class CliBootstrapTest(unittest.TestCase):
    def test_okf_subcommands_exist(self) -> None:
        parser = build_parser()
        root_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
        okf_parser = root_actions[0].choices["okf"]
        okf_actions = [action for action in okf_parser._actions if isinstance(action, argparse._SubParsersAction)]
        self.assertEqual(sorted(okf_actions[0].choices), ["backlinks", "links", "list", "show", "tree", "validate"])

    def test_okf_command_stub_dispatches_list(self) -> None:
        args = argparse.Namespace(okf_command="list")
        with mock.patch("tooling.okf.commands.run_list", return_value=7) as run_list:
            self.assertEqual(command_stub(args), 7)
        run_list.assert_called_once_with(args)

    def test_okf_command_stub_dispatches_show(self) -> None:
        args = argparse.Namespace(okf_command="show")
        with mock.patch("tooling.okf.commands.run_show", return_value=9) as run_show:
            self.assertEqual(command_stub(args), 9)
        run_show.assert_called_once_with(args)

    def test_okf_command_stub_dispatches_validate(self) -> None:
        args = argparse.Namespace(okf_command="validate")
        with mock.patch("tooling.okf.commands.run_validate", return_value=11) as run_validate:
            self.assertEqual(command_stub(args), 11)
        run_validate.assert_called_once_with(args)


if __name__ == "__main__":
    unittest.main()

