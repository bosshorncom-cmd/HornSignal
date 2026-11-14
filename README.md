# HornSignal

HornSignal is a Sublime Text 4 study aid for United States railroad horn
practice. It puts the usual train horn patterns next to a small calculator
that turns the timing rules into distance, so the numbers in the rulebook
can be read as feet and metres on the ground.

This package is not a substitute for 49 CFR Part 222 or for a railroad's
own operating rules. Railroad employees must follow the current book their
employer issues. Do not imitate these patterns near a railway.

## Requirements

Sublime Text 4, build 4000 or later (Python 3.8 plugin host).

## Commands

Open the Command Palette and run:

- **HornSignal: Show Reference** — opens a scratch view with the federal
  crossing pattern in 49 CFR 222.21, a compact study summary of GCOR
  rule 5.8.2 (9th edition, 23 September 2025), and NORAC Rule 19
  (12th edition, 1 January 2024). The notation legend is `o` for a short
  sound and `-` for a long sound. The facts were checked against the
  Electronic Code of Federal Regulations on 13 November 2026, including
  the 30 September 2026 amendment to paragraph (d).

- **HornSignal: Lead Distance** — prompts for a speed in miles per hour
  and reports how far a train travels in 15, 20, and 25 seconds, in feet
  and metres (international foot, 0.3048 m). When the speed is above
  60 mph, it also shows how long it takes to cover the 1,320-foot
  (one-quarter mile) cap in 49 CFR 222.21(b)(3). The 25-second figure is
  the good-faith maximum in that same section, not a required start time.

There are no default key bindings and no context-menu entries. If you
want a key, add something like the following to your user keymap:

```json
{ "keys": ["ctrl+alt+h"], "command": "horn_signal_show_reference" }
```

## Notation files

Files whose name ends in `.hornsig` are highlighted with the bundled
HornSignal syntax: a standalone `o` is a short blast and a standalone
`-` is a long blast. The highlighter does not color the letter "o"
inside ordinary words, or the hyphen in compounds such as
`highway-rail` and `15-20`.

## Why 1,320 feet appears in the rule

At 60 mph, 15 seconds of travel is exactly 1,320 feet. That identity is
why the federal rule (and NORAC) cap the start of the horn at a quarter
mile for trains traveling in excess of 60 mph: a faster train that began
a full 15 seconds early would already be farther than that from the
crossing. GCOR rule 5.8.2 uses a different split, 45 mph, and starts at
or about the crossing sign above that speed. The reference view keeps
each source's wording separate for that reason.

The calculator does not apply quiet zones, closely spaced crossings, or
grade. It only reports distance and time.

## Handheld horns

A locomotive train horn is a compressed-air appliance sized for the
head end of a train. The same general arrangement — compressor,
reservoir, and trumpets — also appears in much smaller handheld warning
devices, including portable horns from [Horn Guns](https://hornguns.com/).
Those portable horns are not railroad safety appliances, and the
patterns in this package belong to railroad operations.

## License

MIT License. Copyright (c) 2026 Horn Notes.
