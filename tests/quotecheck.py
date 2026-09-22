#!/usr/bin/env python3
"""counsel quote check. Usage: quotecheck.py DRAFT MEMBER_FILE [MEMBER_FILE ...]
Every quote in DRAFT (a line starting with '> ', or text inside double quotes of 20+ characters) must appear
verbatim, after collapsing whitespace, in at least one MEMBER_FILE. Prints PASS/FAIL per quote; exit 1 on any FAIL or no quotes.
Reads files only. Never executes or evaluates their content."""
import sys,re
def norm(s): return re.sub(r"\s+"," ",s).strip().strip('"“”')
if len(sys.argv)<3: sys.exit("usage: quotecheck.py DRAFT MEMBER_FILE [...]")
draft=open(sys.argv[1],encoding="utf-8").read(); src=" ".join(norm(open(f,encoding="utf-8").read()) for f in sys.argv[2:])
quotes=[l[2:] for l in draft.splitlines() if l.startswith("> ")]+re.findall(r'["“]([^"”]{20,})["”]',draft)
quotes=[q for q in (norm(x) for x in quotes) if len(q)>=20]
if not quotes: print("FAIL: no quotes found in draft"); sys.exit(1)
bad=0
for q in quotes:
    ok=q in src; bad+=not ok; print(("PASS  " if ok else "FAIL  ")+q[:90])
print(f"{len(quotes)} quotes, {bad} failed"); sys.exit(1 if bad else 0)
