#!/usr/bin/env python3
"""
v5 meadow ambience — REAL daytime birdsong field recording, distinct per video.
Fixes v4 (mux silently dropped audio) and v2/v3 (synthesized/cricket audio rejected).

Method (the reliable path):
  - Source: real 57-min daytime English-meadow field recording (english_meadow.mp3).
  - Pull a DISTINCT ~15s window per clip at widely-spaced offsets so each video gets
    a different birdsong moment (not identical, not nighttime crickets).
  - Fade in/out, gentle level (~-32 dB mean), aresample to 44.1k, then mux video+audio.
  - VERIFY after mux: output has BOTH a video and an audio stream (v4 failed here silently).
"""
import os, subprocess

BASE   = r"E:\APEX\POV\TestVideos\piglets"
SRC    = os.environ.get("LOCALAPPDATA", r"C:\Users\avega.VEGANATOR\AppData\Local") + r"\Temp\english_meadow.mp3"
OUTSUB = "with_audio_v5"
# 4 base clips -> 4 distinct source offsets (~11 min apart so moments differ)
CLIPS = [
    ("pov_piglet_flowerfield.mp4",            60),
    ("pov_piglet_butterfly.mp4",              700),
    ("pov_piglet_trough.mp4",                1400),
    ("pov_piglet_scene2_companion_butterfly.mp4", 2100),
]

def sh(*a, **k):
    return subprocess.run(a, capture_output=True, text=True, **k)

def main():
    os.makedirs(os.path.join(BASE, OUTSUB), exist_ok=True)
    if not os.path.exists(SRC):
        raise SystemExit(f"SOURCE MISSING: {SRC}")
    for clip, off in CLIPS:
        inp = os.path.join(BASE, clip)
        out = os.path.join(BASE, OUTSUB, clip.replace(".mp4", "_sfx.mp4"))
        # base clip duration
        d = float(sh("ffprobe","-v","error","-show_entries","format=duration",
                     "-of","default=noprint_wrappers=1:nokey=1", inp).stdout.strip())
        # cut a real window from the field recording at <off>, len = clip duration
        audio = os.path.join(BASE, OUTSUB, clip.replace(".mp4","_amb.aac"))
        r = sh("ffmpeg","-y","-ss",str(off),
               "-t",f"{d:.3f}","-i",SRC,
               "-af","afade=t=in:st=0:d=1.0,afade=t=out:st=%.3f:d=1.5,volume=0.9,aresample=44100" % max(0,d-1.5),
               "-ac","2","-ar","44100","-c:a","aac","-b:a","128k", audio)
        # mux (this is where v4 silently lost audio -> force stream map, then verify)
        r = sh("ffmpeg","-y","-i",inp,"-i",audio,
               "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy",
               "-shortest","-movflags","+faststart", out)
        if r.returncode != 0:
            print(f"FAIL {clip}: {r.stderr[-400:]}"); continue
        # ---- VERIFY the audio actually landed (v4's missing step) ----
        streams = sh("ffprobe","-v","error","-show_entries","stream=codec_type",
                     "-of","csv", out).stdout.strip().splitlines()
        has_vid = any("video" in s for s in streams)
        has_aud = any("audio" in s for s in streams)
        if not (has_vid and has_aud):
            print(f"!! {clip}: BAD STREAMS {streams}"); continue
        lv = sh("ffmpeg","-i",out,"-af","volumedetect","-f","null","-")
        mean = [l for l in lv.stderr.splitlines() if "mean_volume" in l]
        print(f"OK {clip} (offset {off}s, dur {d:.1f}s) -> {mean[0].strip() if mean else 'n/a'}")
    print("\nDone. Streams per output:")
    for clip,_ in CLIPS:
        out = os.path.join(BASE, OUTSUB, clip.replace(".mp4","_sfx.mp4"))
        print(" ", os.path.basename(out),
              sh("ffprobe","-v","error","-show_entries","stream=codec_type",
                 "-of","csv", out).stdout.strip().replace("\n",","))

if __name__ == "__main__":
    main()
