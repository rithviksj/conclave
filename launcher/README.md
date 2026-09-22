# Counsel launcher

> **STATUS: DRAFT (untested). This is a plan in file form, not a result.** Nothing here is installed, and no alias has been added to any shell config.

One command opens one new iTerm tab and starts a Claude Code session in it. You type the topic in that session, never on the command line.

## Files

- `launch-counsel.sh`: a bash wrapper that picks a command from a fixed list and calls the AppleScript.
- `counsel-tab.applescript`: opens the tab (or a window if none is open) and types the command.

## Modes (the only three)

| Mode | Types into the new tab |
|---|---|
| `lite` (default) | `claude "/counsel"` |
| `full` | `claude "/counsel full"` |
| `plain` | `claude` (you type `/counsel` yourself) |

Any other argument is rejected with exit code 2. `--print` shows the command and opens nothing.

## Suggested aliases (NOT installed; adding them to a shell config is a separate approval)

```
alias cn='<path to this folder>/launch-counsel.sh lite'
alias cnf='<path to this folder>/launch-counsel.sh full'
```

If the shell config is synced to another machine, the aliases would travel with it and point at a path that may not exist there.

## What this does NOT do

- It does not pass any user text to the shell or to AppleScript. The two `claude "/counsel..."` strings and the bare `claude` are constants in the script, and the AppleScript **also** refuses anything that is not printable ASCII and then compares the **numeric code points** of the command against those three constants (case-sensitive, and immune to Unicode look-alikes such as fullwidth letters or zero-width characters), so calling it directly cannot type arbitrary text into a terminal.
- **One operating-system quirk, tested:** macOS removes a single leading byte-order mark (U+FEFF) from an argument before the script runs, so the script receives, checks and types the plain constant. The same character anywhere else in the argument survives and is refused.
- It has not been tried. Whether `claude "/counsel"` actually runs a skill you can invoke is **untested**: only a built-in command (`/status`) and a Claude-only skill were tried as an initial prompt. If it does not run the skill, use `plain`.
- It has not been run against iTerm, so the tab behaviour, and whether macOS asks for automation permission on first use, are unverified.
- It does not start any agent, spend anything, or run counsel by itself. It only opens a session.

## Known unknowns

1. Whether `claude "/counsel"` runs the skill.
2. Whether the tab opens correctly when iTerm has no window, or a window in another Space.
3. Whether macOS shows a permission prompt the first time the AppleScript controls iTerm. If it blocks, the wrapper prints a line saying so.
4. Whether the new tab is the one written to when iTerm has a hotkey window, a full-screen window or a slow tab creation. The script now writes to the object `create tab` returns instead of "the current window", but that has not been run.
