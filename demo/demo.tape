# Terminal demo of the server's tools. Render with: vhs demo/demo.tape   (run from the repo root)
# uv stderr is hidden for the recording: lance prints a harmless column-projection deprecation warning on every search.
Output demo/demo.gif

Set FontSize 14
Set Width 1400
Set Height 900
Set TypingSpeed 40ms

Hide
Type `uv() { command uv "$@" 2>/dev/null; } && clear`
Enter
Show

Type "uv run python demo/demo_client.py screen DEMO-03 hil-a-residential"
Enter
Sleep 8s

Type "clear"
Enter
Type 'uv run python demo/demo_client.py search "lead HIL residential"'
Enter
Sleep 8s
