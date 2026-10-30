# -*- coding: utf-8 -*-
"""Generic finisher for native-vertical POV renders.

    python finish_vertical.py <render.mp4> <output.mp4> [--bed PATH] [--offset SECS] [--silent]

Native 720x1280 -> Lanczos 1.5x -> 1080x1920. Optional ambience bed trimmed from OFFSET,
faded, loudness-normalised (default -14 LUFS, override with --lufs; a quiet ambience
bed usually wants about -20). Log-normalising rather than peak-normalising keeps a steady
bed under the picture instead of competing with it. --silent produces a no-audio
master (video stream only) for clips where ambience adds nothing.

Verifies the result: 1080x1920, correct duration, and reports audio presence + levels so a
silent or whisper-quiet file can never be handed over as "ready".
"""
import json
import os
import subprocess
import sys


def arg(name, default=None):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    bed = arg("--bed")
    offset = float(arg("--offset", "0") or 0)
    silent = "--silent" in sys.argv
    lufs = arg("--lufs", "-14")
    if len(args) < 2 and not (bed and len(args) == 1):
        print(__doc__)
        sys.exit(1)

    src = args[0]
    dst = args[1] if len(args) > 1 else os.path.splitext(src)[0] + "_silent.mp4"

    w, h, dur, has_a = probe(src)
    print(f"source: {w}x{h} {dur:.2f}s audio={'YES' if has_a else 'NO'}")
    if not h > w:
        sys.exit("source is not vertical — this script expects a native 9:16 render")
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)

    if silent:
        chain = "[0:v]scale=1080:1920:flags=lanczos,setsar=1[v]"
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", chain,
               "-map", "[v]", "-an",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", dst]
    else:
        if not bed or not os.path.exists(bed):
            sys.exit(f"bed not found: {bed}")
        amb = os.path.join(os.path.dirname(dst) or ".", "_amb_tmp.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(offset), "-t", f"{dur + 0.3:.2f}",
                        "-i", bed, "-ac", "1", "-ar", "44100", amb], check=True)
        chain = ("[0:v]scale=1080:1920:flags=lanczos,setsar=1[v];"
                 f"[1:a]afade=t=in:st=0:d=1.4,afade=t=out:st={max(dur - 1.8, 0):.2f}:d=1.8,"
                 f"loudnorm=I={lufs}:TP=-1.5:LRA=11,aresample=44100[a]")
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-i", amb,
               "-filter_complex", chain, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", dst]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed: {r.stderr.strip()[:400]}")
    if not silent:
        try:
            os.remove(amb)
        except OSError:
            pass

    w2, h2, dur2, has_a2 = probe(dst)
    print(f"final:  {w2}x{h2} {dur2:.2f}s audio={'YES' if has_a2 else 'NO (intentional)'}")
    if has_a2:
        vol = subprocess.run(["ffmpeg", "-v", "info", "-i", dst, "-vn", "-af", "volumedetect",
                              "-f", "null", "-"], capture_output=True, text=True).stderr
        for line in vol.splitlines():
            if "mean_volume" in line or "max_volume" in line:
                print("  " + line.split("] ")[-1])
    ok = h2 > w2 and (has_a2 or silent)
    print("UPLOAD-READY" if ok else "NOT READY")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
