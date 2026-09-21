# -*- coding: utf-8 -*-
"""Finish POV #011 — baby beaver kit gnawing a branch at golden hour.

Andrew approved this subject from the 540p test render; the 1080p final uses the EXACT
prompt that produced the version he liked — deliberately not "improved".

Also archives the seal pup clip: it was liked but not chosen, and per the channel rule an
unapproved clip must not sit in Videos/ (Andrew uploads by browsing that folder).
"""
import json, os, shutil, subprocess

SRC = r"E:\APEX\POV\TestVideos\candidates\beaver_RAW.mp4"          # 6s test (already liked)
FINAL_RAW = r"E:\APEX\POV\TestVideos\beaver\beaver_FINAL_1080p_RAW.mp4"
DST = r"E:\APEX\POV\Videos\pov_beaver_kit_goldenhour_VERT.mp4"
AMB = r"E:\APEX\Tools\assets\english_meadow.mp3"
OFFSET = 1200.0   # 2100 used by otter, 600 by seal — keep every clip's window distinct
ARCHIVE = r"E:\APEX\POV\Archive"


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height", "-show_entries", "format=duration",
                          "-of", "json", p], capture_output=True, text=True).stdout
    d = json.loads(out)
    w = h = 0
    has_a = False
    for s in d["streams"]:
        if s["codec_type"] == "video":
            w, h = s["width"], s["height"]
        if s["codec_type"] == "audio":
            has_a = True
    return w, h, float(d["format"]["duration"]), has_a


# --- archive the seal (liked, not chosen) so Videos/ holds only approved finals ---
seal = os.path.join(r"E:\APEX\POV\Videos", "pov_seal_pup_goldenhour_VERT.mp4")
if os.path.exists(seal):
    os.makedirs(ARCHIVE, exist_ok=True)
    dest = os.path.join(ARCHIVE, "pov_seal_pup_goldenhour_VERT_NOT-CHOSEN.mp4")
    try:
        shutil.move(seal, dest)
        print("  archived seal pup out of Videos/ (not chosen)")
    except OSError:
        shutil.copy(seal, dest)
        print("  copied seal pup to Archive (file was locked; delete original later)")

# --- finish the beaver ---
if not os.path.exists(FINAL_RAW):
    print(f"  MISSING final render: {FINAL_RAW}")
    raise SystemExit(1)

w, h, dur, has_a = probe(FINAL_RAW)
print(f"  source: {w}x{h}  {dur:.2f}s  audio={has_a}")
assert h < w, "expected landscape from pixverse"

tmp = os.path.join(os.path.dirname(FINAL_RAW), "_amb_beaver.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(OFFSET), "-t", f"{dur + 0.2:.2f}",
                "-i", AMB, "-ac", "1", "-ar", "44100", tmp], check=True)
print(f"  ambience pulled at {OFFSET}s")

chain = ("[0:v]split[bg][fg];[bg]scale=1080:1920,boxblur=18:2[b];"
         "[fg]scale=-1:1080[f];[b][f]overlay=(W-w)/2:(H-h)/2[v];"
         f"[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st={max(dur-1.8,0):.2f}:d=1.8,volume=0.9[a]")

if os.path.exists(DST):
    os.remove(DST)
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", FINAL_RAW, "-i", tmp,
                    "-filter_complex", chain, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", DST], capture_output=True, text=True)
os.remove(tmp)

if r.returncode != 0:
    print("  FAILED:", r.stderr.strip()[:400])
else:
    w2, h2, d2, a2 = probe(DST)
    print(f"  -> {os.path.basename(DST)}")
    print(f"     {w2}x{h2}  {d2:.2f}s  audio={'YES' if a2 else 'NO'}  "
          f"{'✓ UPLOAD-READY' if (h2 > w2 and a2) else '✗ NOT READY'}")
