# HornSignal - railroad train horn signal reference and lead calculator
# Version: 1.0.0
# License: MIT
#
# This is a study aid. It is not a substitute for 49 CFR Part 222
# or for a railroad operating rulebook.
#
# Python 3.8 plugin host (Sublime Text 4, build 4000 or later).

from __future__ import annotations

import re

import sublime
import sublime_plugin


FT_PER_MILE = 5280.0
SEC_PER_HOUR = 3600.0
M_PER_FT = 0.3048
QUARTER_MILE_FT = 1320.0

_POSITIVE_NUMBER = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")


def distance(mph, seconds):
    """Return (feet, metres) covered at mph in the given number of seconds."""
    feet = mph * FT_PER_MILE * seconds / SEC_PER_HOUR
    metres = feet * M_PER_FT
    return (feet, metres)


def time_for_feet(mph, feet):
    """Return seconds needed to cover feet at mph."""
    return feet * SEC_PER_HOUR / (mph * FT_PER_MILE)


def _round_near(x):
    if x >= 0.0:
        return int(x + 0.5)
    return int(x - 0.5)


def fmt_feet(ft):
    n = _round_near(ft)
    if abs(ft - n) < 0.05:
        return "%d ft" % n
    return "%.1f ft" % ft


def fmt_metres(m):
    return "%.1f m" % m


def fmt_seconds(sec):
    n = _round_near(sec * 10.0)
    if abs(sec * 10.0 - n) < 0.05 and n % 10 == 0:
        return "%d s" % (n // 10)
    return "%.1f s" % sec


def fmt_mph(mph):
    n = _round_near(mph * 10.0)
    if abs(mph * 10.0 - n) < 0.05 and n % 10 == 0:
        return "%d mph" % (n // 10)
    return "%g mph" % mph


def parse_mph(raw):
    """Parse a positive miles-per-hour value from an input-panel string.

    Raises ValueError with a user-facing message on bad input.
    """
    s = raw.strip()
    if not _POSITIVE_NUMBER.match(s):
        raise ValueError(
            "HornSignal: speed must be a positive number of miles per hour "
            "(example: 60)"
        )
    mph = float(s)
    if mph <= 0.0:
        raise ValueError("HornSignal: speed must be greater than zero")
    return mph


def format_lead(mph):
    """Build the Lead Distance report for a verified speed."""
    d15 = distance(mph, 15.0)
    d20 = distance(mph, 20.0)
    d25 = distance(mph, 25.0)
    lines = [
        "Horn lead at %s:" % fmt_mph(mph),
        "  15 s:  %s  (%s)" % (fmt_feet(d15[0]), fmt_metres(d15[1])),
        "  20 s:  %s  (%s)" % (fmt_feet(d20[0]), fmt_metres(d20[1])),
        "  25 s:  %s  (%s)  [49 CFR 222.21 good-faith maximum]"
        % (fmt_feet(d25[0]), fmt_metres(d25[1])),
    ]
    if mph > 60.0:
        t1320 = time_for_feet(mph, QUARTER_MILE_FT)
        lines.append(
            "  49 CFR 222.21(b)(3): trains traveling in excess of 60 mph "
            "must not begin"
        )
        lines.append(
            "  sounding more than one-quarter mile (1,320 ft / %s) in advance,"
            % fmt_metres(QUARTER_MILE_FT * M_PER_FT)
        )
        lines.append(
            "  even if that warning is less than 15 s.  Time to cover "
            "1,320 ft at %s: %s."
            % (fmt_mph(mph), fmt_seconds(t1320))
        )
    else:
        lines.append(
            "  At or below 60 mph, 49 CFR 222.21(b)(2) requires a 15-20 s lead"
        )
        lines.append(
            "  (good-faith start not more than 25 s).  At 60 mph, 15 s is "
            "exactly 1,320 ft."
        )
    return "\n".join(lines) + "\n"


REFERENCE_TEXT = """HornSignal - railroad train horn signals (study aid)
====================================================

This view is a study aid.  It is not a substitute for the current text of
49 CFR Part 222, the General Code of Operating Rules (GCOR), or the NORAC
Operating Rules.  Railroad employees must follow their railroad's current
rules.  Do not imitate these patterns near a railway.

Notation:  o  = short sound     -  = long sound


1. 49 CFR 222.21  When must a locomotive horn be used?
-------------------------------------------------------
Source: Electronic Code of Federal Regulations, title 49, section 222.21,
current as of 13 November 2026 (including the 30 September 2026 amendment
to paragraph (d)).  Public domain U.S. government work.

Crossing pattern (paragraph (a)):

    - - o -

  two long blasts, one short blast, and one long blast

Timing (paragraph (b)):

  * Start at least 15 seconds, but no more than 20 seconds, before the
    locomotive enters a public highway-rail grade crossing.
  * Repeat or prolong the pattern until the locomotive occupies the crossing.
  * Good faith: it is not a violation if the engineer begins sounding not
    more than 25 seconds before entering, when arrival time cannot be
    estimated precisely.
  * Trains traveling at speeds in excess of 60 mph shall not begin sounding
    the horn more than one-quarter mile (1,320 feet) in advance of the
    nearest public highway-rail grade crossing, even if that warning is
    less than 15 seconds.
  * The pattern may be varied as necessary where crossings are spaced
    closely together.

Stopped close to a crossing (paragraph (d)):

  An engineer who has stopped in close proximity to a public crossing may
  sound the horn for less than 15 seconds, and may vary the pattern, if
  the crossing is not obstructed and, in the engineer's sole judgment,
  either (1) the crossing has flashing lights and gates and the gates are
  fully lowered, or (2) there is no conflicting motorist or pedestrian
  traffic approaching the crossing.

Paragraph (c) excludes certain Chicago Region crossings described in
section 222.3(c).  Paragraph (e) applies the same timing when state law
requires an audible warning device other than the locomotive horn.


2. Common GCOR whistle signals  (rule 5.8.2)
--------------------------------------------
Study summary of the General Code of Operating Rules, 9th edition,
23 September 2025, rule 5.8.2.  Consult that book for the full text.
Notation in the book: "o" for short sounds and "-" for longer sounds.
The whistle may be used at any time as a warning, regardless of whistle
prohibitions.  Other communication may replace these signals except (1),
(7), and (8).

  (1)  (succession of short sounds)
       Persons or livestock on the track at other than a road crossing at
       grade; also to warn employees when an emergency exists (for
       example, a derailment).  Crews on other trains who hear this signal
       must stop until it is safe to proceed.

  (2)  -          When stopped: air brakes are applied, pressure equalized.

  (3)  - -        Release brakes. Proceed.

  (4)  o o        Acknowledgment of any signal not otherwise provided for.

  (5)  o o o      When stopped: back up.  Acknowledgment of a hand signal
                  to back up.

  (6)  o o o o    Request for a signal to be given or repeated if not
                  understood.

  (7)  - - o -    Approaching public crossings at grade with the engine in
                  front.  Prolong or repeat until the engine completely
                  occupies the crossing(s).

                  GCOR timing (distinct from 49 CFR 222.21's 60 mph rule):
                  A. At speeds in excess of 45 mph, start at or about the
                     crossing sign, but not more than 1/4 mile before the
                     crossing.
                  B. At 45 mph or less, start at least 15 seconds, but not
                     more than 20 seconds, before entering the crossing.
                  C. If there is no crossing sign, start at least 15
                     seconds but not more than 20 seconds before entering,
                     and not more than 1/4 mile before the crossing.
                  D. If movement starts less than 1/4 mile from a crossing,
                     the signal may be sounded for less than 15 seconds
                     when traffic is clearly not approaching, is not
                     stopped at the crossing, or the gates are fully
                     lowered.

  (8)  - o        Approaching men or equipment on or near the track,
                  regardless of any whistle prohibitions.  After this
                  initial warning, sound signal (4) (o o) intermittently
                  until the head end has passed.

Quiet zones and other GCOR exceptions (rules 5.8.4 and 5.8.5) are in the
rulebook and are not repeated here.


3. Common NORAC whistle or horn signals  (Rule 19)
--------------------------------------------------
Study summary of NORAC Operating Rules, 12th edition, effective
1 January 2024, Rule 19.  Consult that book for the full text.
Notation in the book: "o" for short sounds and "-" for long sounds.
Unnecessary use of the engine whistle or horn is prohibited.

  (a)  -          Crew members apply brakes.

  (b)  - - o -    1. Approaching a public highway-rail crossing at grade
                     and at a whistle sign displaying "W", "W/MX", or
                     another specified aspect, with the engine in front:
                     start at least 15 seconds but not more than 20
                     seconds before occupying the crossing; prolong or
                     repeat until the engine occupies the crossing (for
                     multiple crossings, until the last crossing is
                     occupied).  For trains and engines exceeding 60 mph,
                     do not start more than 1/4 mile in advance, even if
                     the warning is then less than 15 seconds.  A movement
                     starting so close that it will take less than 15
                     seconds to occupy the crossing may sound a shorter
                     warning if (a) lights and gates are present and the
                     gates are fully lowered, or (b) there are no
                     conflicting highway movements approaching the
                     crossing.
                  2. Approaching and passing standing trains.

  (c)  (succession of sounds)
       Alarm when persons or livestock are on the track at other than a
       highway crossing at grade; also to warn employees when an
       emergency exists (for example, a derailment).  Crews on other
       trains who hear this signal must stop until it is safe to proceed.

  (d)  - o        Approaching roadway workers or their equipment on or
                  near the track, regardless of any whistle prohibitions.
                  After this initial warning, sound two short signals
                  (o o) intermittently until the head end has passed.

  (e)  o o o      When stopped, back up.  Acknowledgment of a hand signal
                  to back up.

  (f)  o o        Acknowledgment of a stop signal other than a fixed
                  signal, or of any other signal not otherwise provided
                  for.

  (g)  o o o o    Call for signals.

NORAC Rule 19 also covers quiet zones (do not sound 19(b) at a "W/R"
sign or in a designated quiet zone, except in an emergency), cases where
19(b) is permitted but not required, and whistle failure.  See the book.


4. Lead distance  (HornSignal: Lead Distance)
---------------------------------------------
Use HornSignal: Lead Distance to compute how far a train travels in 15 s,
20 s, and 25 s at a given speed, in feet and metres (international foot,
0.3048 m).  At 60 mph, 15 seconds is exactly 1,320 feet (one-quarter
mile), which is why 49 CFR 222.21(b)(3) caps the start of the horn at
that distance for trains traveling in excess of 60 mph.

This is a scratch view; close the tab when you are finished.
"""


class HornSignalReplaceCommand(sublime_plugin.TextCommand):
    """Replace the entire contents of a view. Used to fill the output panel."""

    def run(self, edit, text):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)


class HornSignalShowReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.new_file()
        view.set_name("HornSignal Reference")
        view.set_scratch(True)
        view.set_syntax_file("Packages/HornSignal/HornSignal.sublime-syntax")
        view.run_command("horn_signal_replace", {"text": REFERENCE_TEXT})
        view.set_read_only(True)


class HornSignalLeadDistanceCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel(
            "HornSignal: speed in mph",
            "",
            self.on_done,
            None,
            None,
        )

    def on_done(self, raw):
        try:
            mph = parse_mph(raw)
        except ValueError as exc:
            sublime.error_message(str(exc))
            return
        panel = self.window.create_output_panel("hornsignal")
        panel.set_read_only(False)
        panel.run_command("horn_signal_replace", {"text": format_lead(mph)})
        panel.set_read_only(True)
        self.window.run_command("show_panel", {"panel": "output.hornsignal"})
