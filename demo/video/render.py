"""Record the animated demo page frame by frame with headless Chromium and encode MP4 + GIF.

Usage: uv run --with playwright python demo/video/render.py [--fps 30] [--scale 2] [--gif ""]
"""
import argparse
import functools
import glob
import http.server
import subprocess
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = Path.home() / "Library/Caches/ms-playwright"
W, H = 720, 900
GIF_WARN_MB = 8


def find_chromium() -> str:
    """Newest cached Playwright Chromium executable (macOS app bundle)."""
    dirs = sorted(glob.glob(str(CACHE / "chromium-*")), key=lambda d: int(d.rsplit("-", 1)[1]), reverse=True)
    for d in dirs:
        for exe in glob.glob(f"{d}/chrome-*/*.app/Contents/MacOS/*"):
            if Path(exe).is_file():
                return exe
    sys.exit(f"No Chromium found under {CACHE}/chromium-*; install one with `playwright install chromium`.")


def serve(directory: Path) -> http.server.ThreadingHTTPServer:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        log_message = lambda *a, **k: None  # noqa: E731

    handler = functools.partial(Quiet, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def render_mp4(args, out: Path) -> float:
    """Screenshot every frame and pipe the PNGs straight into ffmpeg; returns the duration."""
    server = serve(ROOT / args.dir)
    ffmpeg = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(args.fps), "-i", "-",
              "-vf", f"scale={W}:{H}:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
              "-preset", "slow", "-movflags", "+faststart", str(out)]
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=find_chromium())
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=args.scale)
        page.goto(f"http://127.0.0.1:{server.server_port}/{args.page}")
        page.evaluate("window.ready")
        duration = page.evaluate("window.DURATION")
        n = round(duration * args.fps)
        proc = subprocess.Popen(ffmpeg, stdin=subprocess.PIPE)
        for i in range(n):
            page.evaluate("t => window.seek(t)", i / args.fps)
            proc.stdin.write(page.screenshot(type="png"))
            if (i + 1) % 100 == 0:
                print(f"frame {i + 1}/{n}", flush=True)
        proc.stdin.close()
        if proc.wait():
            sys.exit("ffmpeg failed while encoding the MP4")
        browser.close()
    server.shutdown()
    return duration


def render_gif(mp4: Path, gif: Path) -> None:
    # full width: at 480 px the 11 px text is barely readable
    vf = ("fps=8,scale=720:-1:flags=lanczos,split[a][b];"
          "[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=diff_mode=rectangle")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", vf, "-loop", "0", str(gif)],
                   check=True)
    mb = gif.stat().st_size / 1e6
    if mb > GIF_WARN_MB:
        print(f"WARNING: {gif} is {mb:.1f} MB (> {GIF_WARN_MB} MB)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", default="demo/demo.mp4")
    ap.add_argument("--gif", default="demo/demo-video.gif", help='"" to skip')
    ap.add_argument("--scale", type=float, default=1, help="device_scale_factor; ffmpeg scales back to 720x900")
    ap.add_argument("--page", default="index.html")
    ap.add_argument("--dir", default="demo/video", help="directory served over http")
    args = ap.parse_args()
    out = ROOT / args.out
    duration = render_mp4(args, out)
    print(f"{out}  {out.stat().st_size / 1e6:.2f} MB  {duration:.1f}s")
    if args.gif:
        gif = ROOT / args.gif
        render_gif(out, gif)
        print(f"{gif}  {gif.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
