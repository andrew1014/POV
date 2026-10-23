# -*- coding: utf-8 -*-
"""Finish POV #015 (baby rabbit in clover, dawn) into an upload-ready final.

Source is a NATIVE-VERTICAL seedance render (720x1280), so there is no blur-pad and no
crop: Lanczos 1.5x upscale straight to 1080x1920, then a dawn birdsong bed at a FRESH
offset (never the same window as a previous clip), then verify both streams.
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
OFFSET = 2340.0          # fresh window — 60/300/900/1500/2100 are already burned by earlier clips


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,codec_name",
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
    if not os.path.exists(RAW):
        sys.exit(f"missing source {RAW}")
    w, h, dur, has_a = probe(RAW)
    print(f"source: {w}x{h} {dur:.2f}s audio={'YES' if has_a else 'NO'}")
    if not (h > w):
        sys.exit(f"source is not vertical ({w}x{h}) — this script expects the native 9:16 render")

    os.makedirs(OUT_DIR, exist_ok=True)
    amb = os.path.join(CAND, "amb.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(OFFSET), "-t", f"{dur + 0.2:.2f}",
                    "-i", AMB, "-ac", "1", "-ar", "44100", amb], check=True)

    chain = ("[0:v]scale=1080:1920:flags=lanczos,setsar=1[v];"
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
    print(f"final:  {w2}x{h2} {dur2:.2f}s audio={'YES' if has_a2 else 'NO'}")
    print("UPLOAD-READY" if (h2 > w2 and has_a2) else "NOT READY — check")


if __name__ == "__main__":
    main()
