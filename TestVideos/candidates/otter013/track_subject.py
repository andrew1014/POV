"""Face-anchored tracking for pov013: find the otter's horizontal centre per frame.

Method: the sea otter's wet dark fur is the darkest large object in the lower-middle
band of the frame (the dark coastline sits in the top ~25%, so it is excluded).
We threshold dark pixels in that band and take their column-wise centroid.

VALIDATION: we already have three independent vision readings of the head centre
(t=2s -> 0.25, t=7s -> 0.60, t=12s -> 0.90). If this tracker reproduces those,
the path is trustworthy; if it does not, we fall back to blur-pad rather than
ship a blind crop.
"""
import subprocess, sys, os
import numpy as np
from PIL import Image

SRC = "pov013_raw1080.mp4"
OUT = "track"
os.makedirs(OUT, exist_ok=True)

DUR = 15.041667
STEP = 0.5
times = [round(t, 2) for t in np.arange(0.5, DUR, STEP)]

# vertical band to search: skip the sky/coastline at top, skip the very bottom edge
TOP_FRAC, BOT_FRAC = 0.28, 0.88

path = []
for t in times:
    png = os.path.join(OUT, f"t{t}.png")
    if not os.path.exists(png):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", SRC,
                        "-frames:v", "1", png], check=True)
    im = Image.open(png).convert("RGB")
    W, H = im.size
    a = np.asarray(im, dtype=np.float32) / 255.0
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    y0, y1 = int(TOP_FRAC * H), int(BOT_FRAC * H)
    band = lum[y0:y1, :]
    # darkest ~6% of the band's pixels
    thr = np.percentile(band, 6)
    mask = band <= thr
    cols = mask.sum(axis=0).astype(np.float64)
    # smooth the column profile so a stray speck cannot drag the centroid
    k = np.ones(41) / 41.0
    cols_s = np.convolve(cols, k, mode="same")
    xs = np.arange(W, dtype=np.float64)
    total = cols_s.sum()
    cx = float((cols_s * xs).sum() / total) if total > 0 else W / 2.0
    path.append((t, cx / W, float(mask.sum())))

print(f"{'t':>6} {'head_x_frac':>12} {'dark_px':>9}")
for t, f, n in path:
    print(f"{t:>6} {f:>12.3f} {int(n):>9}")

# ---- validate against the three vision anchors ----
anchors = [(2.0, 0.25), (7.0, 0.60), (12.0, 0.90)]
print("\nVALIDATION vs vision anchors:")
ok = True
for at, av in anchors:
    best = min(path, key=lambda r: abs(r[0] - at))
    d = best[1] - av
    flag = "OK" if abs(d) <= 0.10 else "MISMATCH"
    if abs(d) > 0.10:
        ok = False
    print(f"  t={at:>4}s  vision={av:.2f}  tracked={best[1]:.3f}  delta={d:+.3f}  {flag}")

print("\nTRACKER_TRUSTWORTHY:", ok)
np.save("track_path.npy", np.array([[t, f] for t, f, _ in path]))