#!/usr/bin/env python3
"""Exercise HornSignal's distance math and reference text outside Sublime Text.

A minimal sublime / sublime_plugin stub is injected before the plugin is
imported, so the command classes can be defined without the ST host.
"""

from __future__ import annotations

import json
import sys
import types
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


class Region(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class FakeView(object):
    def __init__(self):
        self._text = ""
        self._name = ""
        self._scratch = False
        self._read_only = False
        self._syntax = None
        self.commands = []

    def size(self):
        return len(self._text)

    def replace(self, edit, region, text):
        self._text = self._text[: region.a] + text + self._text[region.b :]

    def set_name(self, name):
        self._name = name

    def set_scratch(self, value):
        self._scratch = value

    def set_syntax_file(self, path):
        self._syntax = path

    def set_read_only(self, value):
        self._read_only = value

    def run_command(self, name, args=None):
        self.commands.append((name, args or {}))
        if name == "horn_signal_replace":
            self._text = (args or {}).get("text", "")


class FakeWindow(object):
    def __init__(self):
        self.views = []
        self.panels = {}
        self.shown_panels = []
        self.input_caption = None
        self.input_on_done = None

    def new_file(self):
        view = FakeView()
        self.views.append(view)
        return view

    def show_input_panel(self, caption, initial, on_done, on_change, on_cancel):
        self.input_caption = caption
        self.input_on_done = on_done
        return FakeView()

    def create_output_panel(self, name):
        view = FakeView()
        self.panels[name] = view
        return view

    def run_command(self, name, args=None):
        self.shown_panels.append((name, args or {}))


class FakeSublime(types.ModuleType):
    def __init__(self):
        super(FakeSublime, self).__init__("sublime")
        self.Region = Region
        self.errors = []

    def error_message(self, message):
        self.errors.append(message)


class FakeCommand(object):
    def __init__(self, target=None):
        if hasattr(target, "new_file"):
            self.window = target
            self.view = None
        else:
            self.view = target
            self.window = None


sublime = FakeSublime()
sublime_plugin = types.ModuleType("sublime_plugin")
sublime_plugin.WindowCommand = FakeCommand
sublime_plugin.TextCommand = FakeCommand

sys.modules["sublime"] = sublime
sys.modules["sublime_plugin"] = sublime_plugin

import hornsignal  # noqa: E402


class DistanceTests(unittest.TestCase):
    def test_sixty_mph_fifteen_seconds_is_quarter_mile(self):
        feet, metres = hornsignal.distance(60.0, 15.0)
        self.assertAlmostEqual(feet, 1320.0)
        self.assertAlmostEqual(metres, 1320.0 * 0.3048)
        self.assertEqual(hornsignal.fmt_feet(feet), "1320 ft")
        self.assertEqual(hornsignal.fmt_metres(metres), "402.3 m")

    def test_sixty_mph_twenty_and_twenty_five(self):
        feet20, metres20 = hornsignal.distance(60.0, 20.0)
        feet25, metres25 = hornsignal.distance(60.0, 25.0)
        self.assertAlmostEqual(feet20, 1760.0)
        self.assertAlmostEqual(metres20, 536.448)
        self.assertAlmostEqual(feet25, 2200.0)
        self.assertEqual(hornsignal.fmt_feet(feet20), "1760 ft")
        self.assertEqual(hornsignal.fmt_metres(metres20), "536.4 m")
        self.assertEqual(hornsignal.fmt_feet(feet25), "2200 ft")
        self.assertEqual(hornsignal.fmt_metres(metres25), "670.6 m")

    def test_forty_five_mph_matches_gcor_split(self):
        feet15, metres15 = hornsignal.distance(45.0, 15.0)
        feet20, metres20 = hornsignal.distance(45.0, 20.0)
        self.assertAlmostEqual(feet15, 990.0)
        self.assertAlmostEqual(metres15, 301.752)
        self.assertAlmostEqual(feet20, 1320.0)
        self.assertEqual(hornsignal.fmt_feet(feet15), "990 ft")
        self.assertEqual(hornsignal.fmt_metres(metres15), "301.8 m")
        self.assertEqual(hornsignal.fmt_feet(feet20), "1320 ft")

    def test_time_for_quarter_mile_at_eighty_mph(self):
        seconds = hornsignal.time_for_feet(80.0, 1320.0)
        self.assertAlmostEqual(seconds, 11.25)
        self.assertEqual(hornsignal.fmt_seconds(seconds), "11.2 s")


class ParseAndFormatTests(unittest.TestCase):
    def test_parse_accepts_integer_and_decimal(self):
        self.assertEqual(hornsignal.parse_mph("60"), 60.0)
        self.assertEqual(hornsignal.parse_mph("  12.5\n"), 12.5)

    def test_parse_rejects_junk(self):
        with self.assertRaises(ValueError) as ctx:
            hornsignal.parse_mph("fast")
        self.assertIn("positive number", str(ctx.exception))
        with self.assertRaises(ValueError):
            hornsignal.parse_mph("0")
        with self.assertRaises(ValueError):
            hornsignal.parse_mph("-10")
        with self.assertRaises(ValueError):
            hornsignal.parse_mph("")

    def test_format_lead_at_sixty_includes_15_20_25(self):
        text = hornsignal.format_lead(60.0)
        self.assertIn("Horn lead at 60 mph:", text)
        self.assertIn("15 s:", text)
        self.assertIn("1320 ft", text)
        self.assertIn("402.3 m", text)
        self.assertIn("20 s:", text)
        self.assertIn("1760 ft", text)
        self.assertIn("25 s:", text)
        self.assertIn("2200 ft", text)
        self.assertIn("good-faith maximum", text)
        self.assertIn("15-20 s lead", text)
        self.assertNotIn("must not begin", text)

    def test_format_lead_above_sixty_shows_quarter_mile_cap(self):
        text = hornsignal.format_lead(80.0)
        self.assertIn("Horn lead at 80 mph:", text)
        self.assertIn("15 s:", text)
        self.assertIn("20 s:", text)
        self.assertIn("25 s:", text)
        self.assertIn("49 CFR 222.21(b)(3)", text)
        self.assertIn("1,320 ft", text)
        self.assertIn("11.2 s", text)


class ReferenceTextTests(unittest.TestCase):
    def test_reference_covers_required_sources_and_pattern(self):
        text = hornsignal.REFERENCE_TEXT
        self.assertIn("49 CFR 222.21", text)
        self.assertIn("GCOR", text)
        self.assertIn("5.8.2", text)
        self.assertIn("NORAC", text)
        self.assertIn("Rule 19", text)
        self.assertIn("- - o -", text)
        self.assertIn("train horn", text.lower() or text)
        # The phrase appears in the heading; also accept "locomotive horn".
        self.assertTrue(
            "train horn" in text.lower() or "locomotive horn" in text.lower()
        )
        self.assertIn("15 seconds", text)
        self.assertIn("20 seconds", text)
        self.assertIn("25 seconds", text)
        self.assertIn("1,320 feet", text)
        self.assertIn("45 mph", text)
        self.assertIn("30 September 2026", text)
        self.assertNotIn("hornguns.com", text)
        self.assertNotIn("Horn Guns", text)

    def test_show_reference_fills_scratch_view(self):
        window = FakeWindow()
        cmd = hornsignal.HornSignalShowReferenceCommand(window)
        cmd.run()
        self.assertEqual(len(window.views), 1)
        view = window.views[0]
        self.assertEqual(view._name, "HornSignal Reference")
        self.assertTrue(view._scratch)
        self.assertTrue(view._read_only)
        self.assertEqual(
            view._syntax, "Packages/HornSignal/HornSignal.sublime-syntax"
        )
        self.assertEqual(view._text, hornsignal.REFERENCE_TEXT)
        self.assertIn("49 CFR 222.21", view._text)

    def test_lead_distance_panel_and_bad_input(self):
        sublime.errors = []
        window = FakeWindow()
        cmd = hornsignal.HornSignalLeadDistanceCommand(window)
        cmd.run()
        self.assertEqual(window.input_caption, "HornSignal: speed in mph")
        cmd.on_done("60")
        self.assertIn("hornsignal", window.panels)
        panel = window.panels["hornsignal"]
        self.assertIn("1320 ft", panel._text)
        self.assertIn("15 s:", panel._text)
        self.assertIn("20 s:", panel._text)
        self.assertIn("25 s:", panel._text)
        self.assertTrue(panel._read_only)
        self.assertEqual(
            window.shown_panels[-1],
            ("show_panel", {"panel": "output.hornsignal"}),
        )

        sublime.errors = []
        cmd.on_done("nope")
        self.assertEqual(len(sublime.errors), 1)
        self.assertIn("positive number", sublime.errors[0])


class SyntaxAndManifestTests(unittest.TestCase):
    def test_sublime_syntax_yaml_parses(self):
        try:
            import yaml
        except ImportError:
            self.fail("PyYAML is required to parse HornSignal.sublime-syntax")
        path = PACKAGE_ROOT / "HornSignal.sublime-syntax"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "HornSignal")
        self.assertEqual(data["file_extensions"], ["hornsig"])
        self.assertEqual(data["scope"], "text.hornsignal")
        self.assertIn("main", data["contexts"])
        matches = [item["match"] for item in data["contexts"]["main"]]
        self.assertTrue(any(r"\bo\b" in m for m in matches))
        self.assertTrue(any("-" in m and "15-20" not in m for m in matches))
        # The long-blast rule must not be a bare hyphen that would also
        # match the hyphen in highway-rail; it uses a lookbehind/ahead.
        long_rules = [m for m in matches if m.strip().endswith("(?=\\s|$)") or "-(?=\\s|$)" in m]
        self.assertTrue(long_rules, msg="missing standalone hyphen rule: %r" % matches)

    def test_commands_and_messages_json_parse(self):
        commands = json.loads(
            (PACKAGE_ROOT / "Default.sublime-commands").read_text(encoding="utf-8")
        )
        captions = {item["caption"]: item["command"] for item in commands}
        self.assertEqual(
            captions["HornSignal: Show Reference"], "horn_signal_show_reference"
        )
        self.assertEqual(
            captions["HornSignal: Lead Distance"], "horn_signal_lead_distance"
        )
        messages = json.loads(
            (PACKAGE_ROOT / "messages.json").read_text(encoding="utf-8")
        )
        self.assertEqual(messages["install"], "messages/install.txt")
        install = (PACKAGE_ROOT / "messages" / "install.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("HornSignal: Show Reference", install)
        self.assertIn("train horn" in install.lower() or "horn" in install.lower(), [True])
        self.assertNotIn("hornguns.com", install)

    def test_readme_has_single_hornguns_link_and_mentions_train_horn(self):
        readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("train horn", readme)
        self.assertEqual(readme.count("https://hornguns.com/"), 1)
        self.assertEqual(readme.count("hornguns.com"), 1)
        self.assertNotIn("nofollow", readme)


if __name__ == "__main__":
    unittest.main()
