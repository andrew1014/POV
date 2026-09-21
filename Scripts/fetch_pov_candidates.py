# -*- coding: utf-8 -*-
"""Fetch the two candidate test renders, finish them to vertical, and measure them.

Tests only — no ambience bed needed for a look/taste check; the approved one gets the
full finishing pass afterwards. blur-pad matches the published channel look.
"""
import json, os, subprocess, urllib.request

D = r"E:\APEX\POV\TestVideos\candidates"
os.makedirs(D, exist_ok=True)

CANDIDATES = [
    ("duckling", "https://v3b.fal.media/files/b/0aab4001/yuY3czHSoG0hlQ_BtF9Kc_output.mp4"),
    ("beaver",   "https://v3b.fal.media/files/b/0aab4007/cgvP5AzGvOSfnkS9CvZQY_output.mp4"),
]


def fetch(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as f:
        f.write(r.read())


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height", "-show_entries", "format=duration",
                          "-of", "json", p], capture_output=True, text=True).stdout
    d = json.loads(out)
    w = h = 0
    for s in d["streams"]:
        if s["codec_type"] == "video":
            w, h = s["width"], s["height"]
    return w, h, float(d["format"]["duration"])


for name, url in CANDIDATES:
    raw = os.path.join(D, f"{name}_RAW.mp4")
    if not os.path.exists(raw) or os.path.getsize(raw) < 10000:
        fetch(url, raw)
        print(f"  downloaded {name}")
    w, h, dur = probe(raw)
    vert = os.path.join(D, f"{name}_VERT_TEST.mp4")
    chain = ("[0:v]split[bg][fg];[bg]scale=1080:1920,boxblur=18:2[b];"
             "[fg]scale=-1:1080[f];[b][f]overlay=(W-w)/2:(H-h)/2[v]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-filter_complex", chain,
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-an", vert], capture_output=True)
    w2, h2, d2 = probe(vert)
    print(f"  {name:<9} raw {w}x{h} {dur:.2f}s  ->  vertical {w2}x{h2} {d2:.2f}s")
    # frames for the contact sheet
    for i, t in enumerate((1, 3, 5)):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", vert,
                        "-frames:v", "1", "-update", "1",
                        os.path.join(D, f"{name}_f{i}.png")], capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-i", os.path.join(D, f"{name}_f0.png"),
                    "-i", os.path.join(D, f"{name}_f1.png"),
                    "-i", os.path.join(D, f"{name}_f2.png"),
                    "-filter_complex",
                    "[0:v]scale=300:-1[a];[1:v]scale=300:-1[b];[2:v]scale=300:-1[c];"
                    "[a][b][c]hstack=inputs=3",
                    os.path.join(D, f"{name}_sheet.png")], capture_output=True)

# motion scores
import cv2
import numpy as np
def motion(p, n=50):
    cap = cv2.VideoCapture(p); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prev, diffs = None, []
    for i in range(n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i * (total - 1) / (n - 1)))
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(cv2.resize(fr, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            diffs.append(float(np.mean(np.abs(g - prev))))
        prev = g
    cap.release()
    return float(np.mean(diffs))

print("\n  motion (otter benchmark = 19.1)")
for name, _ in CANDIDATES:
    print(f"    {name:<9} {motion(os.path.join(D, f'{name}_VERT_TEST.mp4')):5.2f}")