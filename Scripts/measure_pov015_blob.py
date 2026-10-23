# -*- coding: utf-8 -*-
"""Measure the skin-toned foreground blob in the rabbit POV frames (finish check only)."""
import os
import numpy as np
from PIL import Image

CAND = r"E:\APEX\POV\TestVideos\candidates\rabbit015"

for name in ("f_0.5.png", "f_4.png", "f_8.png", "f_12.png", "f_14.5.png"):
    p = os.path.join(CAND, name)
    im = np.asarray(Image.open(p).convert("RGB")).astype(int)
    h, w, _ = im.shape
    r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    # skin-ish: warm, R noticeably above B, not blown out, not green-dominant
    mask = (r > 120) & (r - b > 30) & (r - g > 12) & (g > b) & (r < 250)
    # restrict to the lower half — that's where the foreground occlusion lives
    mask[: h // 2, :] = False
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        print(f"{name:10s} no skin-like region below half height")
        continue
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    print(f"{name:10s} {w}x{h}  blob rows {y0}-{y1} (={100*(h-y0)/h:.1f}% up from bottom), "
          f"cols {x0}-{x1}, pixels {len(ys)} ({100*len(ys)/(w*h):.1f}% of frame)")
