# -*- coding: utf-8 -*-
"""Compare candidate ambience beds on measurable properties (no ears available).

Reports duration, loudness, spectral balance and steadiness so a *quiet* bed can be chosen
without guessing. A good room-tone bed is steady, has a plausible noise floor, and is not
dominated by 200-800 Hz rumble or by hiss above 4 kHz.
"""
import os
import subprocess
import sys
import wave

import numpy as np

D = r"E:\APEX\Tools\assets\pov-beds"


def analyse(path):
    wav = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-ac", "1", "-ar", "22050", wav],
                   check=True)
    w = wave.open(wav)
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    fs = w.getframerate()
    dur = len(x) / fs
    rms = float(np.sqrt((x ** 2).mean()))
    peak = float(np.abs(x).max())

    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / fs)
    tot = spec.sum() or 1.0
    bands = {}
    for lo, hi in ((0, 80), (80, 200), (200, 800), (800, 3000), (3000, 8000), (8000, 11025)):
        m = (f >= lo) & (f < hi)
        bands[f"{lo}-{hi}"] = 100 * spec[m].sum() / tot

    fr = int(0.05 * fs)
    frames = [float(np.sqrt((x[i:i + fr] ** 2).mean())) for i in range(0, len(x) - fr, fr)]
    p10, p50, p90 = (float(np.percentile(frames, q)) for q in (10, 50, 90))

    print(f"\n{os.path.basename(path)}")
    print(f"  dur {dur:6.2f}s   rms {rms:.4f}   peak {peak:.4f}   crest {peak/(rms or 1e-9):.1f}")
    print("  bands: " + "  ".join(f"{k}={v:.1f}%" for k, v in bands.items()))
    print(f"  frame rms p10 {p10:.4f}  p50 {p50:.4f}  p90 {p90:.4f}  "
          f"p90/p10 {p90/(p10 or 1e-9):.2f}")
    try:
        os.remove(wav)
    except OSError:
        pass
    return dict(rms=rms, bands=bands, p10=p10, p50=p50, steadiness=p90 / (p10 or 1e-9))


if __name__ == "__main__":
    for name in sys.argv[1:]:
        analyse(os.path.join(D, name))
