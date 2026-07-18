from __future__ import annotations

import argparse
import contextlib
import io
import unittest
from unittest import mock

from mira_okf.cli import build_parser, main
from mira_okf.okf.commands import command_stub


class CliBootstrapTest(unittest.TestCase):
    commands = ("tree", "list", "show", "links", "backlinks", "props", "validate", "health")

    def test_root_subcommands_are_the_eight_direct_commands(self) -> None:
        parser = build_parser()
        root_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
        self.assertEqual(sorted(root_actions[0].choices), sorted(self.commands))

    def test_command_stub_dispatches_every_direct_command(self) -> None:
        runners = {
            "tree": "mira_okf.okf.commands.run_tree",
            "list": "mira_okf.okf.commands.run_list",
            "show": "mira_okf.okf.commands.run_show",
            "links": "mira_okf.okf.commands.run_links",
            "backlinks": "mira_okf.okf.commands.run_backlinks",
            "props": "mira_okf.okf.props.run_props",
            "validate": "mira_okf.okf.commands.run_validate",
            "health": "mira_okf.okf.commands.run_health",
        }

        for status, (command, runner) in enumerate(runners.items(), start=1):
            with self.subTest(command=command), mock.patch(runner, return_value=status) as run_command:
                args = argparse.Namespace(command=command)
                self.assertEqual(command_stub(args), status)
            run_command.assert_called_once_with(args)

    def test_version_remains_available(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            build_parser().parse_args(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertTrue(output.getvalue().startswith("mira-okf "))

    def test_show_without_a_concept_is_a_parser_error(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            main(["show"])

        self.assertNotEqual(raised.exception.code, 0)

    def test_grouped_form_is_rejected_without_dispatching(self) -> None:
        with mock.patch("mira_okf.cli.command_stub") as handler:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main(["okf", "tree", "bundle"])

        self.assertNotEqual(raised.exception.code, 0)
        handler.assert_not_called()


if __name__ == "__main__":
    unittest.main()
