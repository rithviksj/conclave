#!/usr/bin/env python3
"""counsel quote check.  Usage: quotecheck.py DRAFT TAG=MEMBER_FILE [TAG=MEMBER_FILE ...]

A quote is a draft line of the form  > [TAG] quoted text  (for example  > [A] the cost is too high).
Each quote must appear verbatim, after collapsing whitespace and straightening curly quotes, in the
file of THAT member only, so a quote stitched from two members fails. Every TAG given must have at
least one quote (the chair must quote each member). Other text in the draft is ignored, so stray
quote marks cannot cause false failures. Prints PASS/FAIL per quote; exit 1 on any failure.
Reads files only; never executes or evaluates their content."""
import re
import sys

QUOTE = re.compile(r"^>\s*\[([A-Za-z0-9]+)\]\s*(.+?)\s*$")


def norm(s):
    s = s.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))
    return re.sub(r"\s+", " ", s).strip()


def check(draft_text, members):
    """members: {TAG: text}. Returns (lines, failures)."""
    srcs = {t: norm(x) for t, x in members.items()}
    quotes = [(m.group(1), norm(m.group(2)).strip('"')) for m in map(QUOTE.match, draft_text.splitlines()) if m]
    out, bad = [], 0
    if not quotes:
        return ["FAIL  no '> [TAG] ...' quotes found in draft"], 1
    for tag, q in quotes:
        if tag not in srcs:
            ok, why = False, f"unknown member tag [{tag}]"
        elif len(q) < 12:
            ok, why = False, "quote shorter than 12 characters"
        else:
            ok, why = q in srcs[tag], "not found verbatim in that member's text"
        bad += not ok
        out.append(("PASS  " if ok else "FAIL  ") + f"[{tag}] {q[:80]}" + ("" if ok else f"  ({why})"))
    for tag in srcs:
        if not any(t == tag for t, _ in quotes):
            bad += 1
            out.append(f"FAIL  member [{tag}] is never quoted")
    return out, bad


def main(argv):
    if len(argv) < 3 or not all("=" in a for a in argv[2:]):
        sys.exit("usage: quotecheck.py DRAFT TAG=MEMBER_FILE [TAG=MEMBER_FILE ...]")
    draft = open(argv[1], encoding="utf-8").read()
    members = {}
    for a in argv[2:]:
        tag, path = a.split("=", 1)
        members[tag] = open(path, encoding="utf-8").read()
    lines, bad = check(draft, members)
    print("\n".join(lines))
    print(f"{bad} failure(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
