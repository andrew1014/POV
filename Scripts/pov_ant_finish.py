#!/usr/bin/env python3
"""POV ant clip finisher: hook captions (ASS, approved style) + dawn ambience bed."""
import os, subprocess

D = r"E:\APEX\POV\TestVideos\ant"
OUT = r"E:\APEX\POV\Videos\pov_ant_sunrise_VERT.mp4"
SRC = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "english_meadow.mp3")
OFFSET = 1500.0          # distinct window from the same source (vary per clip)

CAPTIONS = [
    (0.30, 3.20, "POV: you are an ant."),
    (3.40, 7.00, "Sunrise. Two centimetres off the ground."),
    (7.20, 11.20, "Up here, one drop of dew weighs more than you do."),
    (11.40, 14.90, "You would never see this from above."),
]

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,62,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,1,2,60,60,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(sec):
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ass = os.path.join(D, "ant_hook.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write(HEADER)
        for s, e, t in CAPTIONS:
            f.write(f"Dialogue: 0,{ts(s)},{ts(e)},Default,,0,0,0,,{{\\an2}}{t}\n")
    print("captions ->", ass, len(CAPTIONS))

    amb = os.path.join(D, "amb_ant.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(OFFSET), "-t", "15.2",
                    "-i", SRC, "-ac", "1", "-ar", "44100", amb], check=True)
    print("ambience ->", amb, os.path.getsize(amb), "bytes")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", "ant_vert_nocap.mp4", "-i", "amb_ant.wav",
        "-filter_complex",
        "[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st=13.2:d=1.8,volume=0.9[a]",
        "-vf", "ass=ant_hook.ass",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT,
    ], check=True, cwd=D)
    print("FINAL ->", OUT)


if __name__ == "__main__":
    main()
