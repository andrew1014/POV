# -*- coding: utf-8 -*-
"""Generate a multi-segment Wan clip and stitch it into one continuous video.

Wan 2.2 5B drifts if you ask for much beyond ~5 seconds in a single pass, so a longer clip is
built as a chain: each segment starts from the LAST FRAME of the one before it (image-to-video),
which keeps the animal, the lighting and the camera continuous instead of hard-cutting.

    python gen_wan_sequence.py --out NAME "segment 1 prompt" "segment 2 prompt" "segment 3 prompt"

Default 3 x 121 frames at 24 fps = ~15 s. Segments are stitched losslessly-ish with ffmpeg.

Progress prints per segment so a long unattended run is legible in the log.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import gen_wan_clip as G

OUT_DIR = r"E:\APEX\POV\TestVideos\wan"
WORK = os.path.join(OUT_DIR, "_sequence")


def download(images, dest_dir):
    paths = []
    for img in images:
        q = urllib.parse.urlencode({"filename": img["filename"],
                                    "subfolder": img.get("subfolder", ""),
                                    "type": img.get("type", "output")})
        data = urllib.request.urlopen(f"{G.HOST}/view?{q}", timeout=600).read()
        p = os.path.join(dest_dir, img["filename"])
        with open(p, "wb") as f:
            f.write(data)
        paths.append(p)
    return paths


def to_mp4(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", dst], check=True)
    return dst


def last_frame(mp4, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.2", "-i", mp4,
                    "-frames:v", "1", dst], check=True)
    return dst


def main() -> None:
    FLAGS = {"--out", "--w", "--h", "--length", "--steps", "--seed", "--gguf", "--fps"}
    prompts, i = [], 1
    while i < len(sys.argv):
        if sys.argv[i] in FLAGS:
            i += 2
            continue
        prompts.append(sys.argv[i])
        i += 1
    if not prompts:
        print(__doc__)
        sys.exit(1)

    def opt(name, default):
        return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

    name = opt("--out", "wan_sequence")
    w = int(opt("--w", "704"))
    h = int(opt("--h", "1280"))
    length = int(opt("--length", "121"))
    steps = int(opt("--steps", "30"))
    fps = int(opt("--fps", "24"))
    gguf = opt("--gguf", "Wan2.2-TI2V-5B-Q8_0.gguf")
    base_seed = int(opt("--seed", "-1"))
    if base_seed < 0:
        base_seed = int.from_bytes(os.urandom(4), "big") % 2**31

    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"{len(prompts)} segments x {length} frames @ {steps} steps -> "
          f"{len(prompts) * length / fps:.1f}s total", flush=True)

    pieces = []
    start_image = None
    t_start = time.time()

    for idx, prompt in enumerate(prompts, 1):
        seed = base_seed + idx - 1
        seg_t0 = time.time()
        print(f"\n--- segment {idx}/{len(prompts)}  seed {seed}", flush=True)
        print(f"    prompt: {prompt[:90]}...", flush=True)

        wf = G.build(prompt, seed, w, h, length, steps, fps, start_image, gguf)
        pid = G.post("/prompt", {"prompt": wf})["prompt_id"]

        info = None
        while time.time() - seg_t0 < 3600:
            try:
                hist = G.get(f"/history/{pid}")
            except Exception as e:
                raise SystemExit(f"ComfyUI died during segment {idx} ({type(e).__name__}).")
            if pid in hist:
                info = hist[pid]
                break
            time.sleep(5)
        if info is None:
            raise SystemExit(f"segment {idx} timed out")

        files = []
        for node in info.get("outputs", {}).values():
            files.extend(node.get("images", []) + node.get("gifs", []))
        if not files:
            raise SystemExit(f"segment {idx} produced nothing: {json.dumps(info)[:300]}")

        got = download(files, WORK)
        webm = got[0]
        mp4 = to_mp4(webm, os.path.join(WORK, f"seg{idx:02d}.mp4"))
        pieces.append(mp4)
        print(f"    {time.time() - seg_t0:.0f}s  -> {mp4}", flush=True)

        # chain: next segment starts from this one's final frame
        frame = last_frame(mp4, os.path.join(WORK, f"seg{idx:02d}_last.png"))
        start_image = f"wan_seq_{idx:02d}.png"
        os.makedirs(G.INPUT_DIR, exist_ok=True)
        shutil.copyfile(frame, os.path.join(G.INPUT_DIR, start_image))
        print(f"    chained start frame -> {start_image}", flush=True)

    listing = os.path.join(WORK, "concat.txt")
    with open(listing, "w") as f:
        for p in pieces:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")
    final = os.path.join(OUT_DIR, f"{name}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", listing, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", final], check=True)

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", final],
                         capture_output=True, text=True).stdout.strip()
    print(f"\nFINAL {final}  {float(dur):.2f}s  "
          f"total render {time.time() - t_start:.0f}s", flush=True)


if __name__ == "__main__":
    main()
