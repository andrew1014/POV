#!/usr/bin/env python3
"""
Add FREE gentle meadow/nature ambience to the piglet POV clips.

Synthesizes a soft nature soundscape locally (no network, no cost):
  - gentle wind (filtered brown noise)
  - soft bird chirps (sine-blip chirps at natural spacing)
Then mixes it at low volume under each clip and exports with the video.
Uses soundfile + numpy (docenv) and ffmpeg for final mux.
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

def wind(dur_s, sr=SR, seed=0):
    rng = np.random.default_rng(seed)
    # brown-ish noise (cumsum of white, normalized) for low rumble of wind
    n = rng.standard_normal(int(dur_s * sr))
    brown = np.cumsum(n)
    brown -= brown.mean()
    brown /= (np.abs(brown).max() + 1e-9)
    # lowpass-ish by smoothing
    k = np.ones(64) / 64
    brown = np.convolve(brown, k, mode="same")
    # gentle envelope (slow fade in/out, gentle breathing)
    t = np.linspace(0, dur_s, len(brown))
    env = 0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * t)   # slow swell
    return (brown * env * 0.25).astype(np.float32)

def bird_chirps(dur_s, sr=SR, seed=1, n=10):
    rng = np.random.default_rng(seed)
    out = np.zeros(int(dur_s * sr), dtype=np.float32)
    for _ in range(n):
        t0 = rng.uniform(0, dur_s - 0.4)
        dur = rng.uniform(0.18, 0.35)
        f0 = rng.uniform(2600, 4200)
        f1 = f0 + rng.uniform(-300, 500)
        tt = np.arange(int(dur * sr)) / sr
        # chirp: frequency sweep
        freq = np.linspace(f0, f1, len(tt))
        phase = 2 * np.pi * np.cumsum(freq) / sr
        tone = np.sin(phase) * np.exp(-tt * 12)   # plucked decay
        # envelope
        tone *= np.minimum(1, tt * 40) * np.minimum(1, (dur - tt) * 40)
        tone *= rng.uniform(0.5, 1.0)
        i0 = int(t0 * sr)
        i1 = min(i0 + len(tone), len(out))
        out[i0:i1] += tone[:i1 - i0]
    # normalize
    out /= (np.abs(out).max() + 1e-9)
    return (out * 0.22).astype(np.float32)

def main():
    os.makedirs(os.path.join(BASE, "with_audio"), exist_ok=True)
    for clip in CLIPS:
        inp = os.path.join(BASE, clip)
        # get duration
        dur = float(subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=noprint_wrappers=1:nokey=1", inp],
            capture_output=True, text=True).stdout.strip())
        w = wind(dur)
        b = bird_chirps(dur)
        mix = (w + b).astype(np.float32)
        # master gentle level
        mix *= 0.5
        wav = os.path.join(BASE, "with_audio", clip.replace(".mp4", "_ambience.wav"))
        sf.write(wav, mix, SR)
        out = os.path.join(BASE, "with_audio", clip.replace(".mp4", "_sfx.mp4"))
        subprocess.run([
            "ffmpeg","-y","-i",inp,"-i",wav,
            "-map","0:v","-map","1:a",
            "-c:v","copy","-c:a","aac","-b:a","128k",
            "-shortest", out
        ], check=True, capture_output=True)
        print(f"OK {clip} ({dur:.1f}s) -> {os.path.basename(out)}")

if __name__ == "__main__":
    main()
