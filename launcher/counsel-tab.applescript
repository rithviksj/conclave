-- Opens one new iTerm tab (or a window, if none is open) and types the command it is given.
-- Defense in depth: this file refuses any command other than the three constants that
-- launch-counsel.sh can choose, so calling it directly cannot type arbitrary text into a terminal.
on run argv
	set cmd to item 1 of argv
	-- Layer 1: ASCII printable only. AppleScript text comparison treats Unicode look-alikes
	-- (fullwidth letters, zero-width or soft-hyphen characters, no-break space) as equal to ASCII,
	-- so text comparison alone cannot be exact.
	set codes to id of cmd
	if class of codes is integer then set codes to {codes}
	repeat with c in codes
		if c < 32 or c > 126 then error "counsel-tab: refusing a non-ASCII or control character" number 1
	end repeat
	-- Layer 2: compare the numeric code points, not the text, against the three constants.
	set allowed to false
	repeat with okCmd in {"claude \"/counsel\"", "claude \"/counsel full\"", "claude"}
		if codes = (id of (contents of okCmd)) then set allowed to true
	end repeat
	if not allowed then error "counsel-tab: refusing an unexpected command" number 1
	tell application "iTerm"
		activate
		if (count of windows) = 0 then
			set newWindow to (create window with default profile)
			set targetSession to current session of newWindow
		else
			tell current window
				set newTab to (create tab with default profile)
			end tell
			set targetSession to current session of newTab
		end if
		tell targetSession to write text cmd
	end tell
end run
