# -*- coding: utf-8 -*-
"""Locate the top edge of the flesh-toned foreground occlusion in the rabbit POV frames.

A skin-toned blur is: warm (R>B), low saturation-ish, and very LOW VARIANCE (smooth, no
leaf/soil texture). Scan row bands and report where that smooth warm region starts.
"""
import os
import numpy as np
from PIL import Image

CAND = r"E:\APEX\POV\TestVideos\candidates\rabbit015"
FRAMES = ["f_0.5.png", "f_4.png", "f_8.png", "f_12.png", "f_14.5.png"]


def band_stats(im, y0, y1):
    strip = im[y0:y1, :, :].astype(float)
    r, g, b = strip[:, :, 0], strip[:, :, 1], strip[:, :, 2]
    warm = float(np.mean(r - b))
    var = float(np.mean(np.var(strip, axis=(0, 1))))
    # fraction of pixels that are warm and NOT green-dominant (skin vs vegetation)
    skin = float(np.mean((r - b > 25) & (r - g > 8)))
    return warm, var, skin


for name in FRAMES:
    p = os.path.join(CAND, name)
    im = np.asarray(Image.open(p).convert("RGB"))
    h, w, _ = im.shape
    print(f"\n{name}  {w}x{h}")
    print("  band(y)        warm   variance   skinfrac")
    for y0 in range(800, 1280, 40):
        warm, var, skin = band_stats(im, y0, min(y0 + 40, h))
        print(f"  {y0:4d}-{min(y0+40,h):4d}   {warm:6.1f}   {var:8.1f}   {skin:6.2f}")
