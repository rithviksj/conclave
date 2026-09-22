# Security model

## What conclave defends against

- **A confused or prompt-injected peer session** sending harmful requests. Every peer message is an untrusted request; a peer's claim of the user's approval is never approval; requests go to one named peer, not by broadcast.
- **File-borne injection in a channel folder.** A file counts only if a message announced it with its sha256; filenames, refs and paths are checked against allowlists before use; mailbox content is never run, fetched or evaluated.
- **Rule loosening.** The rules block states that a rule can only make a session more cautious, and text that would loosen protections is ignored.
- **Counsel exfiltration.** No agent holds both a file tool and a network tool. Debating members have no tools. The web checker gets claim text only, drawn from the first round, before any member has seen local findings.
- **Launcher injection.** The launcher types one of three fixed commands. Both the shell wrapper and the AppleScript refuse anything else; the AppleScript compares numeric code points, so Unicode look-alikes are refused.

## What it does not defend against

- **Anything running as your user.** The socket is owner-only, which stops other OS users only. A same-user process can forge messages and files. Provenance is not authority.
- **Enforcement.** The rules are text. Enforcement comes only from Claude Code's permission system, the tool allowlists in the agent files, and your approvals.
- **Your account identity.** `omitClaudeMd` keeps `CLAUDE.md` out of agents but not, it appears, the account email.
- **Your global config in the sessions themselves.** Sessions that talk to each other still load your `CLAUDE.md`.
- **The built-in browser server.** `--no-chrome` did not remove `claude-in-chrome` from interactive sessions in testing. Deny any browser action you did not ask for.
- **A mistaken approval.** If you approve a prompt, it happens.

## Recommended launch

```bash
claude --permission-mode manual --strict-mcp-config --mcp-config '{"mcpServers":{}}'
```

Check on screen that the mode reads "manual" and that `/mcp` lists no connectors. Expect `claude-in-chrome` to remain listed; the prompting mode is the guard. The default permission mode on a machine can change between sessions, so do not rely on it.

## Reporting

Open an issue. Do not include transcripts: they may contain private configuration.
