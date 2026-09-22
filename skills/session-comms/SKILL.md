---
name: session-comms
description: Connect two or more of your own Claude Code sessions on this machine so they can exchange messages and files safely. Runs only when the user types /session-comms, for example "/session-comms connect all".
disable-model-invocation: true
---

> **STATUS: DRAFT v3 (trimmed to a single source of rules). Untested. This is a plan in file form, not a result.**

**Most rules here are guidance to reduce mistakes. Enforcement comes only from the harness's own controls and the user's approvals.**

## What this is, and what it is not

Claude Code already provides the transport: `ListAgents`, `SendMessage` over per-session owner-only sockets, inbound hold/refuse controls, loop throttling and `notify_when_idle`. This skill adds a connect flow and a rules block. It builds no socket, daemon or server, and never uses SSH or a network port to reach another session.

## Where the rules live (single source)

**All rules for talking to peers live in ONE place: `templates/HELLO.md`.** You send that text to every member, so a peer follows the rules without having this skill. Do not restate or paraphrase the rules anywhere else; copies drift. This file holds only what the **initiator** alone needs. You follow the same rules you send, so read `templates/HELLO.md` before you connect anything. If you cannot read it (it sits next to this file; `${CLAUDE_SKILL_DIR}` is this skill's folder), stop and tell the user. Do not write the rules from memory.

## `/session-comms connect all | <k> | @a @b`

1. Call `ListAgents` **once** and keep the result. Keep local interactive rows; drop yourself; ignore cloud and Remote Control rows. Re-list only if a send fails with "not found". If nothing remains, say so and stop.
2. Choose members:
   - **`all`**: every remaining session.
   - **`@a @b`**: the mentioned sessions (the harness's `@` typeahead is the drop-down).
   - **`<k>` with no mentions**: ask with AskUserQuestion, `multiSelect`, label = session name, description = "idle/busy, age, ref", idle first. Limits: 4 options per question, up to 4 questions. It cannot force exactly k, so check the count and re-ask once.
3. **Print the member list before sending anything**, so the user can interrupt. For `all` with up to 3 idle sessions, do not ask a question. With more than 3, or any busy, ask ONE confirmation, because a greeting wakes every idle session and may interrupt unrelated work.
4. **Names** (best-effort): a name that starts with the current OS username is probably auto-generated and embeds a personal identifier. Tell the user to rename that session at its own keyboard with `/rename`. You cannot rename another session. Names appear only in the user's own terminal; everything you write uses [ref] ids.
5. **Send the HELLO** from `templates/HELLO.md` to each member, with the placeholders filled: your ref, the member refs, a short `[a-z0-9-]` thread id that **you** choose, the root and channel folder, and the README's sha256. Default root: `~/session-comms/`. With no channel folder, drop the file part of rule 12 and end the HELLO with: No channel folder; keep everything inline. For a busy peer, subscribe once with `notify_when_idle`; never poll.
6. Wait for the replies, then tell the user which peers joined and which are **held, refused or busy**. Mixed permission modes can hold messages for the peer's user to approve; do not resend around a hold.
7. Default topology is a **mesh**. Above 4 members, warn that this is untested. Refuse more than 6 without an explicit OK.

## Initiator duties

- **Channel folder** (only if long or auditable documents are needed): create it under the root with one `to-<ref>/` per member, an `archive/` folder and a `ROSTER.md`, and copy in `templates/channel-README.md`. For a short exchange, use no folder at all.
- **Crossing** is rule 9 and **budget** is rule 11 of the HELLO. Pointers only; the rules are not restated here.
- **Closing:** send `DONE` (broadcast allowed). Give the user a **5-line summary**: what was agreed, open items, where any files are, and the **message and character counts you sent on the thread**. Deleting channel files needs the user's OK.

## What this does NOT do

- It does not authenticate a peer, enforce any rule, guarantee delivery, or make peers agree.
- A sender's identity is matched by its session name, which the user can rename and which is not proof of who sent it. Renaming a session mid-channel means every open channel needs a new HELLO; that is by design and fails closed.
- It does **not** stop a peer from being prompt-injected, and does **not** stop a same-user process from forging messages or files.
- For a peer **without** this skill, the root and folder come from the HELLO, which a forger controls, so the receiver's one-line notice to its user is the only guard.
- It is single-machine, needs sessions that have an inbox (sessions started in bare mode do not appear), and cannot rename another session or bypass a peer's hold.
- It has no scan script, so "no personal information" is **unchecked**, and it cannot detect names or inference in files.
- It is not validated at more than 3 sessions. Consensus between sessions of one model is not verification.

## Known unknowns

1. Whether these instructions survive context compaction in a long thread. The HELLO block restates every rule as a hedge.
2. Whether a user-invocable skill runs when started as `claude "/session-comms ..."`. Only built-ins and a Claude-only skill have been tried.
3. Behavior at 4 or more sessions.
4. Whether the rules block does better than a bare 15-line doc: a controlled test (16 runs, small model, simulated scenarios) was **inconclusive** and showed no advantage for longer rules text. The rules block is therefore deliberately doc-length. The v3 wording itself was not tested.
5. Whether the skill can locate `templates/HELLO.md` relative to itself.

## Feature status

| Feature | Status |
|---|---|
| `connect all`, `@` mentions, picker | untested |
| HELLO rules block as the single source | untested. The v3 wording was NOT tested; only an earlier doc-length version was (U11, inconclusive) |
| Crossing merge, HALT with nonce | untested live |
| File exchange with sha256 announcement and receiver validation | untested |
| Mesh of 4 or more | untested, not validated |
