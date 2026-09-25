---
name: session-comms
description: Connect two or more of your own Claude Code sessions on this machine so they can exchange messages and files safely. Runs only when the user types /session-comms, for example "/session-comms connect @other".
disable-model-invocation: true
---

> **STATUS: v0.2.** Tested live with 2 sessions and in simulation (see the repo's TESTING.md). Not validated at 3 or more sessions.

**Most rules here are guidance to reduce mistakes. Enforcement comes only from the harness's own controls and the user's approvals.**

## What this is, and what it is not

Claude Code already provides the transport: `ListAgents`, `SendMessage` over per-session owner-only sockets, inbound hold/refuse controls, loop throttling and `notify_when_idle`. This skill adds a connect flow and a rules block. It builds no socket, daemon or server, and never uses SSH or a network port to reach another session.

## Where the rules live (single source)

**All rules for talking to peers live in ONE place: `templates/HELLO.md`.** You send that text to every member, so a peer follows the rules without having this skill. Do not restate or paraphrase the rules anywhere else; copies drift. This file holds only what the **initiator** alone needs. You follow the same rules you send, so read `templates/HELLO.md` before you connect anything. If you cannot read it (it sits next to this file; `${CLAUDE_SKILL_DIR}` is this skill's folder), stop and tell the user. Do not write the rules from memory.

## Arguments

- `connect all` · `connect <k>` · `connect @a @b`: the connect flow below.
- **`@a @b` with no verb** means `connect @a @b`.
- **No arguments:** call `ListAgents` once, show the user a table (name, idle/busy, age, ref), and ask with AskUserQuestion (`multiSelect`, idle first) which sessions to connect. Then continue at step 3 below. Do nothing else.
- Anything else: show these forms and stop.

## Connect flow

1. Call `ListAgents` **once** and keep the result. Keep local interactive rows; drop yourself; ignore cloud and Remote Control rows. Re-list only if a send fails with "not found". If nothing remains, say so and stop.
2. Choose members:
   - **`all`**: every remaining session.
   - **`@a @b`**: the mentioned sessions (the harness's `@` typeahead is the drop-down).
   - **`<k>` with no mentions**: ask with AskUserQuestion, `multiSelect`, label = session name, description = "idle/busy, age, ref", idle first. Limits: 4 options per question, up to 4 questions. It cannot force exactly k, so check the count and re-ask once.
3. **Print the member list before sending anything**, so the user can interrupt. For `all` with up to 3 idle sessions, do not ask a question. With more than 3, or any busy, ask ONE confirmation, because a greeting wakes every idle session and may interrupt unrelated work.
4. **Names** (best-effort): flag a session name that contains the current OS username or the machine's short host name, or that equals the working folder's name. These are usually auto-generated and can embed a personal identifier. Tell the user to rename that session at its own keyboard with `/rename`. You cannot rename another session. Names appear only in the user's own terminal; everything you write uses [ref] ids.
5. **Check for a crossing first.** If a HELLO from one of the chosen members has already arrived, follow rule 9 of the HELLO (the lower ref's HELLO is the thread) instead of sending your own.
6. **Send the HELLO** from `templates/HELLO.md` to each member, with the placeholders filled: your ref, the member refs, a short `[a-z0-9-]` thread id that **you** choose, the root and channel folder, and the README's sha256. Default root: `~/session-comms/`. The README hash is the sha256 of `templates/channel-README.md`, because the folder's copy is identical. With no channel folder, replace rule 12 with "12. No files on this thread." and end the HELLO with: No channel folder; keep everything inline. For a busy peer, subscribe once with `notify_when_idle`; never poll.
7. Wait for the replies, then tell the user which peers joined and which are **held, refused or busy**. Mixed permission modes can hold messages for the peer's user to approve; do not resend around a hold.
8. Default topology is a **mesh**. Above 4 members, warn that this is untested. Refuse more than 6 without an explicit OK.

## Initiator duties

- **Channel folder** (only if long or auditable documents are needed): the HELLO names the path, but **create the folder only when the first file is written**: under the root, one `to-<ref>/` per member, an `archive/` folder, a `ROSTER.md` (refs and neutral aliases only), and an unchanged copy of `templates/channel-README.md` as `README.md`. For a short exchange, use no folder at all.
- **Crossing** is rule 9, **budget** is rule 11, and **closing** is rule 15 of the HELLO. Pointers only; the rules are not restated here.
- **After closing:** if the channel folder holds nothing but what you created (README, ROSTER, empty mail folders), remove it and an empty root. If it holds any mail, deleting it needs the user's OK.

## Build/design coordination (optional, for substantive joint tasks)

Use this in addition to the basic connect flow when the topic is a real design/build decision — new code, an architecture change, a redesign — not a status ping or a quick question. Skip it for anything the basic ASK/ANSWER flow already covers cleanly.

- **Critique before consensus, not rubber-stamping.** When a peer proposes something, check it against real evidence (read the actual code/file, don't just accept an earlier agent's unverified claim) before agreeing. Push back with a specific reason if you have one; say so explicitly if you don't. A caught mistake — yours or theirs — is worth more than a fast agreement; self-correct in the open when you find one, the same skepticism rule 1's identity check already asks for.
- **Verbatim consensus, not independent paraphrases.** Once both sides agree, one side drafts the exact final text and the other adopts it **word for word** — never each writing its own summary of "what we agreed," which drifts. If something in that text turns out wrong after the fact (a stale figure, an unverified claim), correct the record in the open rather than letting it quietly stand.
- **Division of work, review status and a sign-off log belong in a channel-folder file** (e.g. `STATUS.md`), not scattered across messages — a table of who owns what, what's done/in-progress/pending, and a running sign-off log. Pick ONE session to own writing that file, the same way this skill has you own `SKILL.md` changes solo; everyone else sends status as messages, never edits it directly, so two sessions never race on one file.
- **Mutual review before either side's work goes anywhere it can't be undone** (a push, a merge, a delete): each session looks at the other's actual diff or output before either one finalizes, and posts an explicit sign-off — not a silent assumption that "no news is fine."
- **Isolate shared state before you divide work.** If the work touches one shared resource both sessions can write to at once — most commonly a single git working directory — check for that before assuming "split it in two" gives real isolation. A same-directory `git checkout -b` from two sessions is not isolation; `git worktree add` (or two separate clones) is. The same logic applies to any other shared mutable resource — one running dev server on one port, one database file — check who's using it before you touch it, the same caution rule 2 already asks for.
- **The 3-message budget (rule 11) is a floor for a task like this, not a hard stop.** A real critique-and-consensus round routinely needs more exchanges than a simple ping. When you hit the limit and the topic is still open, tell your user and ask, exactly as rule 11 already says — don't just quietly keep going. If the user grants an exception (for example, no cap while still deciding, cap back on once execution starts), say so back to the peer explicitly so both sides know why message counts don't match the written rule, and revert to the normal budget once the task moves from deciding to doing.

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
2. Whether a user-invocable skill runs when started as `claude "/session-comms ..."`.
3. Behavior at 4 or more sessions.
4. The build/design coordination pattern above has run live exactly once, on one real multi-file task (2026-09-25). Not yet stress-tested the way the rest of v0.2 was (canary, simulation) — treat it as a documented starting point, not a validated protocol.
