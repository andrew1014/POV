# -*- coding: utf-8 -*-
"""Finish POV #010 — sea otter... no: harbour seal pup at golden hour.

Reuses the proven finishing method from build_pov_finals.py (blur-pad landscape ->
1080x1920, ambience bed with fades, no burned text) rather than editing the shared
JOBS list, so the already-published clips are not rebuilt.

Audio offset 600s — deliberately distinct from the 2100s used by the otter clam, so no
two clips share the same ambience window.
"""
import json, os, subprocess

SRC = r"E:\APEX\POV\TestVideos\seal-pup\seal_FINAL_1080p_RAW.mp4"
DST = r"E:\APEX\POV\Videos\pov_seal_pup_goldenhour_VERT.mp4"
AMB = r"E:\APEX\Tools\assets\english_meadow.mp3"
OFFSET = 600.0


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height", "-show_entries", "format=duration",
                          "-of", "json", p], capture_output=True, text=True, timeout=60).stdout
    d = json.loads(out)
    w = h = 0
    has_a = False
    for s in d["streams"]:
        if s["codec_type"] == "video":
            w, h = s["width"], s["height"]
        if s["codec_type"] == "audio":
            has_a = True
    return w, h, float(d["format"]["duration"]), has_a


w, h, dur, has_a = probe(SRC)
print(f"  source: {w}x{h}  {dur:.2f}s  audio={has_a}")
assert h < w, "source is not landscape — blur-pad path not applicable"

tmp = os.path.join(os.path.dirname(SRC), "_amb_seal.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(OFFSET), "-t", f"{dur + 0.2:.2f}",
                "-i", AMB, "-ac", "1", "-ar", "44100", tmp], check=True)
print(f"  ambience pulled at {OFFSET}s offset")

chain = ("[0:v]split[bg][fg];[bg]scale=1080:1920,boxblur=18:2[b];"
         "[fg]scale=-1:1080[f];[b][f]overlay=(W-w)/2:(H-h)/2[v];"
         f"[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st={max(dur-1.8,0):.2f}:d=1.8,volume=0.9[a]")

if os.path.exists(DST):
    os.remove(DST)
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-i", tmp,
                    "-filter_complex", chain, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", DST], capture_output=True, text=True)
os.remove(tmp)

if r.returncode != 0:
    print("  FAILED:", r.stderr.strip()[:400])
else:
    w2, h2, dur2, has_a2 = probe(DST)
    ok = h2 > w2 and has_a2
    print(f"  -> {os.path.basename(DST)}")
    print(f"     {w2}x{h2}  {dur2:.2f}s  audio={'YES' if has_a2 else 'NO'}  "
          f"{'✓ UPLOAD-READY' if ok else '✗ NOT READY'}")
