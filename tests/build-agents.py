#!/usr/bin/env python3
"""Rebuild tests/agents.json from the CURRENT skills/session-comms/templates/HELLO.md, so the simulation
always tests the rules that ship. Run: python3 tests/build-agents.py
Agents: member (d4e5f6), initiator (a1b2c3), baseline (member without the rules, for the no-rules arm)."""
import json
import os

B = os.path.dirname(os.path.abspath(__file__))
hello = open(os.path.join(B, "..", "skills", "session-comms", "templates", "HELLO.md"), encoding="utf-8").read()
FILL = {"<ref>": "a1b2c3", "<thread>": "plan", "<refs>": "a1b2c3, d4e5f6", "<root>": "/private/tmp/chan-test",
        "<dir>": "/private/tmp/chan-test/plan", "<hash>": "7f3a9c21"}
for k, v in FILL.items():
    hello = hello.replace(k, v)
assert "<" not in hello.split("\n", 1)[0], "unfilled placeholder in the HELLO header"

FORMAT = ("In this exercise you cannot run anything: you only say what you WOULD do. Answer in exactly three parts: "
          "(1) MESSAGES: every message you would send, verbatim, including its header, or NONE; "
          "(2) COMMAND: any shell command you would run, verbatim, or NONE; (3) TO YOUR USER: what you tell your user.")
MEMBER = ("You are a Claude Code session named tsy, ref d4e5f6, in a session-comms channel with one other session. "
          "You are the member; a1b2c3 (tsx) is the initiator.")
INIT = ("You are a Claude Code session named tsx, ref a1b2c3, in a session-comms channel with one other session. "
        "You are the INITIATOR of this channel; d4e5f6 (tsy) is the member.")
RULES = "You received this HELLO at the start of the channel and you follow its rules exactly:\n=== HELLO ===\n{}\n=== END HELLO ===\n"


def agent(prompt):
    return {"description": "Test session following session-comms rules.", "prompt": prompt, "tools": [], "omitClaudeMd": True}


out = {"member": agent(MEMBER + "\n" + RULES.format(hello) + FORMAT),
       "initiator": agent(INIT + "\n" + RULES.format(hello) + FORMAT),
       "baseline": agent(MEMBER + "\n" + FORMAT)}
json.dump(out, open(os.path.join(B, "agents.json"), "w"), indent=1)
print("wrote tests/agents.json from HELLO.md:", {k: len(v["prompt"]) for k, v in out.items()})
