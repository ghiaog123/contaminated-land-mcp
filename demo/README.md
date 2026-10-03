# Demo

- `demo.tape` is a [vhs](https://github.com/charmbracelet/vhs) script. It drives `demo_client.py`, which calls the server in memory
  and prints each tool's text result. Render from the repo root with `vhs demo/demo.tape` to produce `demo/demo.gif`.
- The Claude Desktop recording (the user asks, Claude calls the tools, the exceedance table appears) is manual.
  vhs cannot drive Claude Desktop.
- `video/` holds an animated walkthrough: the host model calls the four tools over MCP, and only `draft_section` calls a model
  (names redacted before it, citations and numbers checked after it). `video/index.html` draws every frame from
  `video/data.json`, and each value there names its source (the a09 agent run, the DEMO-03 screening, the 2026-10-03
  evals). Render with `uv run --with playwright python demo/video/render.py` to produce `demo/demo.mp4` (720x900, 40 s)
  and `demo/demo-video.gif`. It uses the Chromium that Playwright already cached and does not download one.
