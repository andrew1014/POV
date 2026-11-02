# -*- coding: utf-8 -*-
"""Generate a Wan 2.2 TI2V-5B clip locally through ComfyUI's REST API.

Zero marginal cost — local GPU only. Native vertical mode is 704x1280 at 24 fps; 121 frames
is a touch over five seconds. The model is silent, so audio is added afterwards by the
existing finish_vertical.py pipeline.

    python gen_wan_clip.py "prompt" [--out NAME] [--w 704] [--h 1280] [--length 121]
                              [--steps 30] [--seed N] [--image START.png]

Prints wall-clock render time so we can judge whether local generation is practical.
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HOST = "http://127.0.0.1:8188"
OUT_DIR = r"E:\APEX\POV\TestVideos\wan"
INPUT_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Comfy-Desktop", "ComfyUI-Shared", "input")

UNET = "wan2.2_ti2v_5B_fp16.safetensors"
CLIP = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
VAE = "wan2.2_vae.safetensors"

# Wan 2.2 was trained with this style of negative; it is noticeably better behaved with it.
NEG = ("色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，"
       "最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，"
       "画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，"
       "杂乱的背景，三条腿，背景人很多，倒着走")

DEFAULT_PROMPT = ("A baby rabbit sits among clover in a meadow at dawn, very close to the camera, "
                  "nose twitching as it sniffs the air, soft golden morning light, shallow depth of "
                  "field, gentle natural movement, macro wildlife photography")


def post(path, payload):
    req = urllib.request.Request(HOST + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def get(path, timeout=30):
    with urllib.request.urlopen(HOST + path, timeout=timeout) as r:
        return json.loads(r.read().decode())


def build(prompt, seed, w, h, length, steps, fps, start_image=None, gguf_model=None):
    if gguf_model:
        # ComfyUI-GGUF: quantised weights, far smaller VRAM footprint than the 10 GB fp16 file.
        unet_node = {"class_type": "UnetLoaderGGUF",
                     "inputs": {"unet_name": gguf_model}}
    else:
        unet_node = {"class_type": "UNETLoader",
                     "inputs": {"unet_name": UNET, "weight_dtype": "default"}}
    g = {
        "1": unet_node,
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": CLIP, "type": "wan"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["2", 0]}},
        "6": {"class_type": "Wan22ImageToVideoLatent",
              "inputs": {"vae": ["3", 0], "width": w, "height": h,
                         "length": length, "batch_size": 1}},
        "7": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": steps, "cfg": 5.0,
                         "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
                         "model": ["1", 0], "positive": ["4", 0],
                         "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecodeTiled",
              "inputs": {"samples": ["7", 0], "vae": ["3", 0],
                         "tile_size": 256, "overlap": 64,
                         "temporal_size": 32, "temporal_overlap": 8}},
        "9": {"class_type": "SaveWEBM",
              "inputs": {"images": ["8", 0], "filename_prefix": "wan_clip",
                         "codec": "vp9", "fps": float(fps), "crf": 20.0}},
    }
    if start_image:
        g["10"] = {"class_type": "LoadImage", "inputs": {"image": start_image}}
        g["6"]["inputs"]["start_image"] = ["10", 0]
    return g


def main() -> None:
    FLAGS = {"--out", "--w", "--h", "--length", "--steps", "--seed", "--fps", "--image", "--gguf"}
    args, i = [], 1
    while i < len(sys.argv):
        if sys.argv[i] in FLAGS:
            i += 2
            continue
        args.append(sys.argv[i])
        i += 1

    def opt(name, default):
        return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

    prompt = args[0] if args else DEFAULT_PROMPT
    w = int(opt("--w", "704"))
    h = int(opt("--h", "1280"))
    length = int(opt("--length", "81"))
    steps = int(opt("--steps", "30"))
    fps = int(opt("--fps", "24"))
    name = opt("--out", "wan_test")
    seed = int(opt("--seed", "-1"))
    if seed < 0:
        seed = int.from_bytes(os.urandom(4), "big") % 2**31

    start_image = None
    src = opt("--image", None)
    if src:
        import shutil
        os.makedirs(INPUT_DIR, exist_ok=True)
        start_image = "wan_start_" + os.path.basename(src)
        shutil.copyfile(src, os.path.join(INPUT_DIR, start_image))

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"{w}x{h}  {length} frames @ {fps}fps = {length/fps:.2f}s  steps {steps}  seed {seed}")

    t0 = time.time()
    gguf_model = opt("--gguf", None)
    if gguf_model:
        print("using GGUF:", gguf_model)
    pid = post("/prompt", {"prompt": build(prompt, seed, w, h, length, steps, fps,
                                          start_image, gguf_model)})["prompt_id"]
    print("queued", pid, flush=True)

    info = None
    while time.time() - t0 < 3600:
        try:
            hist = get(f"/history/{pid}")
        except Exception as e:
            # A reset here means ComfyUI itself died (OOM during decode), not a network blip.
            raise SystemExit(f"ComfyUI went down mid-render ({type(e).__name__}). "
                             f"Lower --length or --h before retrying.")
        if pid in hist:
            info = hist[pid]
            break
        time.sleep(5)
    if info is None:
        raise SystemExit("timed out after 60 minutes")
    render_s = time.time() - t0
    print(f"RENDER TIME {render_s:.1f}s ({render_s/length:.2f}s per frame)")

    files = []
    for node in info.get("outputs", {}).values():
        files.extend(node.get("images", []) + node.get("gifs", []))
    if not files:
        raise SystemExit(f"no output: {json.dumps(info)[:400]}")

    outs = []
    for f in files:
        q = urllib.parse.urlencode({"filename": f["filename"],
                                    "subfolder": f.get("subfolder", ""),
                                    "type": f.get("type", "output")})
        data = urllib.request.urlopen(f"{HOST}/view?{q}", timeout=300).read()
        webm = os.path.join(OUT_DIR, f"{name}.webm")
        with open(webm, "wb") as fh:
            fh.write(data)
        print("WROTE", webm, len(data), "bytes")

        mp4 = os.path.join(OUT_DIR, f"{name}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", mp4],
                       check=True)
        outs.append(mp4)
        print("WROTE", mp4, os.path.getsize(mp4), "bytes")

    print("done", len(outs))


if __name__ == "__main__":
    main()
