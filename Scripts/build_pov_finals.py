import subprocess, os, json

TEST = r"E:\APEX\POV\TestVideos"
OUT = r"E:\APEX\POV\Videos"
AMB = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "english_meadow.mp3")

JOBS = [
    (r"animals\pov_otter_clam.mp4", "pov_otter_clam_VERT.mp4", 2100.0),
    (r"piglets\with_audio_v5\pov_piglet_flowerfield_sfx.mp4", "pov_piglet_flowerfield_VERT.mp4", None),
    (r"piglets\with_audio_v5\pov_piglet_butterfly_sfx.mp4", "pov_piglet_butterfly_VERT.mp4", None),
    (r"piglets\with_audio_v5\pov_piglet_trough_sfx.mp4", "pov_piglet_trough_VERT.mp4", None),
    (r"piglets\with_audio_v5\pov_piglet_scene2_companion_butterfly_sfx.mp4",
     "pov_piglet_companion_VERT.mp4", None),
    (r"animals\pov_otter_face_vert.mp4", "pov_otter_face_VERT.mp4", None),
]


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


def build(src, dst, offset):
    w, h, dur, has_a = probe(src)
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(dst):
        try:
            os.remove(dst)
        except OSError:
            pass
    vertical = h > w
    add_amb = (offset is not None) and not has_a

    args = ["ffmpeg", "-y", "-v", "error", "-i", src]
    tmp = os.path.join(TEST, "_amb_tmp.wav")
    if add_amb:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(offset), "-t", f"{dur + 0.2:.2f}",
                        "-i", AMB, "-ac", "1", "-ar", "44100", tmp], check=True)
        args += ["-i", tmp]

    if vertical:
        fc = None
        args += ["-map", "0:v", "-map", "0:a?"]
    else:
        chain = ("[0:v]split[bg][fg];[bg]scale=1080:1920,boxblur=18:2[b];"
                 "[fg]scale=-1:1080[f];[b][f]overlay=(W-w)/2:(H-h)/2[v]")
        if add_amb:
            chain += f";[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st={max(dur-1.8,0):.2f}:d=1.8,volume=0.9[a]"
            args += ["-map", "[v]", "-map", "[a]"]
        else:
            args += ["-map", "[v]", "-map", "0:a?"]
        args += ["-filter_complex", chain]

    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", dst]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{os.path.basename(dst):40s} FAILED: {r.stderr.strip()[:160]}")
        return
    w2, h2, dur2, has_a2 = probe(dst)
    ok = "OK" if (h2 > w2 and has_a2) else "CHECK"
    print(f"{os.path.basename(dst):40s} {w2}x{h2} {dur2:6.2f}s audio={'YES' if has_a2 else 'NO '} {has_a2 and ''}{ok}")


print("building POV finals...")
for src, name, off in JOBS:
    sp = os.path.join(TEST, src)
    if not os.path.exists(sp):
        print(f"{name:40s} MISSING SOURCE")
        continue
    build(sp, os.path.join(OUT, name), off)
print("done.")
