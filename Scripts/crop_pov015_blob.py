# -*- coding: utf-8 -*-
"""STOPGAP: remove the flesh-toned foreground artifact from the rabbit POV clip.

The artifact occupies the bottom ~17% of the 720x1280 render (skin-tone fraction rises
from 0.02 at row 1040 to 0.90 at row 1280). Crop it off, keep 9:16, and bias the
horizontal window right so the rabbit survives.

720x1280  ->  crop y 0..1060, x 110..706 (596x1060, 9:16)  ->  1080x1920 lanczos.
"""
import json
import os
import subprocess
import sys

CAND = r"E:\APEX\POV\TestVideos\candidates\rabbit015"
RAW = os.path.join(CAND, "pov015_RAW.mp4")
OUT_DIR = r"E:\APEX\POV\Videos"
FINAL = os.path.join(OUT_DIR, "pov_rabbit_kit_clover_dawn_VERT.mp4")
AMB = r"E:\APEX\Tools\assets\english_meadow.mp3"
OFFSET = 2340.0

CW, CH = 596, 1060      # crop size (keeps 9:16)
CX, CY = 110, 0         # crop origin


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height",
         "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, timeout=120).stdout
    d = json.loads(out)
    w = h = 0
    has_audio = False
    for s in d["streams"]:
        if s["codec_type"] == "video":
            w, h = s["width"], s["height"]
        if s["codec_type"] == "audio":
            has_audio = True
    return w, h, float(d["format"]["duration"]), has_audio


def main():
    sw, sh, dur, has_a = probe(RAW)
    print(f"source {sw}x{sh} {dur:.2f}s audio={'YES' if has_a else 'NO'}")
    if (CX + CW > sw) or (CY + CH > sh):
        sys.exit("crop window exceeds source")

    amb = os.path.join(CAND, "amb_crop.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(OFFSET), "-t", f"{dur + 0.2:.2f}",
                    "-i", AMB, "-ac", "1", "-ar", "44100", amb], check=True)

    chain = (f"[0:v]crop={CW}:{CH}:{CX}:{CY},scale=1080:1920:flags=lanczos,setsar=1[v];"
             f"[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st={max(dur - 1.8, 0):.2f}:d=1.8,"
             "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", RAW, "-i", amb,
                        "-filter_complex", chain, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
                        FINAL], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed: {r.stderr.strip()[:400]}")

    w2, h2, dur2, has_a2 = probe(FINAL)
    print(f"final  {w2}x{h2} {dur2:.2f}s audio={'YES' if has_a2 else 'NO'}")
    print("UPLOAD-READY" if (h2 > w2 and has_a2) else "NOT READY")


if __name__ == "__main__":
    main()
