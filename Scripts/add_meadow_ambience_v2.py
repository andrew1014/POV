#!/usr/bin/env python3
"""
REVISED free meadow ambience — warm, natural, NO tinkly high sine-blips.
Fixes: the old 'bird chirps' were raw high sine tones that read as fairy-tinkle.
New approach:
  - WARM WIND: richer brown-noise gust layer (dominant), lowpassed, slow swell.
  - DEEP GRASS RUSTLE: soft filtered noise shimmer (mid-band).
  - BIRDS: realistic short FM-chirp (swept up+down w/ harmonics), few & distant,
    lowpassed, under -30dB so they're texture not melody.
All synthesized locally (free), then mixed under the video at gentle level.
"""
import os, subprocess
import numpy as np
import soundfile as sf

BASE = r"E:\APEX\POV\TestVideos\piglets"
CLIPS = [
    "pov_piglet_flowerfield.mp4",
    "pov_piglet_butterfly.mp4",
    "pov_piglet_trough.mp4",
    "pov_piglet_scene2_companion_butterfly.mp4",
]
SR = 44100
OUT_SUB = "with_audio_v2"

def lowpass(x, cutoff, sr=SR):
    from scipy import signal as sg  # available? fallback if not
    try:
        b, a = sg.butter(2, cutoff / (sr/2), btype="low")
        return sg.filtfilt(b, a, x)
    except Exception:
        # simple moving-average fallback
        k = np.ones(max(1, int(sr/cutoff/2))) / max(1, int(sr/cutoff/2))
        return np.convolve(x, k, mode="same")

def wind_gust(dur_s, sr=SR, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.standard_normal(int(dur_s * sr))
    brown = np.cumsum(n)
    brown -= brown.mean()
    brown /= (np.abs(brown).max() + 1e-9)
    brown = lowpass(brown, 700, sr)          # warm low rumble
    t = np.linspace(0, dur_s, len(brown))
    # slow gusty envelope (irregular swells)
    env = 0.5 + 0.5*np.sin(2*np.pi*0.07*t) + 0.3*np.sin(2*np.pi*0.11*t+1.3)
    env = np.clip(env, 0.15, 1.0)
    return (brown * env * 0.35).astype(np.float32)

def grass_rustle(dur_s, sr=SR, seed=2):
    rng = np.random.default_rng(seed)
    n = rng.standard_normal(int(dur_s * sr))
    # band-pass-ish shimmer
    k = np.ones(8)/8
    n = np.convolve(n, k, mode="same")
    n -= np.convolve(np.cumsum(n)[:len(n)]/len(n), np.ones(32)/32, mode="same")
    n /= (np.abs(n).max()+1e-9)
    return (n * 0.12).astype(np.float32)

def bird_call(dur_s, sr=SR, seed=3, n=5):
    rng = np.random.default_rng(seed)
    out = np.zeros(int(dur_s*sr), dtype=np.float32)
    for _ in range(n):
        t0 = rng.uniform(0.5, dur_s-1.0)
        for _sub in range(2):            # 2-note call
            f0 = rng.uniform(1800, 3200)
            dur = rng.uniform(0.10, 0.18)
            tt = np.arange(int(dur*sr))/sr
            f = f0 * (1 + 0.5*np.sin(2*np.pi*8*tt))   # FM warble
            tone = np.sin(2*np.pi*np.cumsum(f)/sr)
            tone *= np.exp(-tt*18)
            # harmonic softness via lowpass
            tone = lowpass(tone, 4000, sr)
            i0 = int((t0+rng.uniform(0,0.3))*sr)
            i1 = min(i0+len(tone), len(out))
            out[i0:i1] += (tone * rng.uniform(0.4,0.9))[:i1-i0]
            t0 += dur + rng.uniform(0.05,0.2)
    out /= (np.abs(out).max()+1e-9)
    return (out * 0.18).astype(np.float32)   # distant birds, low

def main():
    os.makedirs(os.path.join(BASE, OUT_SUB), exist_ok=True)
    for clip in CLIPS:
        inp = os.path.join(BASE, clip)
        dur = float(subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=noprint_wrappers=1:nokey=1",inp],
            capture_output=True,text=True).stdout.strip())
        w = wind_gust(dur)
        g = grass_rustle(dur)
        b = bird_call(dur)
        mix = (w + g + b).astype(np.float32)
        mix *= 0.6   # master gentle
        wav = os.path.join(BASE, OUT_SUB, clip.replace(".mp4","_amb.wav"))
        out = os.path.join(BASE, OUT_SUB, clip.replace(".mp4","_sfx.mp4"))
        sf.write(wav, mix, SR)
        subprocess.run([
            "ffmpeg","-y","-i",inp,"-i",wav,
            "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","128k",
            "-shortest", out], check=True, capture_output=True)
        print(f"OK {clip} ({dur:.1f}s)")
        # loudness report
        r = subprocess.run(["ffmpeg","-i",out,"-af","volumedetect","-f","null","-"],
                           capture_output=True,text=True)
        mv = [l for l in r.stderr.splitlines() if "mean_volume" in l]
        print("   ", mv[0].strip() if mv else "")

if __name__ == "__main__":
    main()
