# -*- coding: utf-8 -*-
"""POV #015 — baby rabbit in clover at dawn.

Renders through the SAME managed FAL gateway the video_generate tool uses, but submits,
saves the request id, and polls it ourselves. Reason: the tool wrapper caps at 420 s and
a 15 s seedance render can exceed that, losing the result URL after the spend.

Usage:
  python render_pov015.py --dry     # build + print payload, no spend
  python render_pov015.py           # submit, poll, download
"""
import importlib.util
import json
import os
import sys
import time
import urllib.request

HERMES = r"C:\Users\avega.VEGANATOR\AppData\Local\hermes\hermes-agent"
POV = r"E:\APEX\POV"
_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
CAND = _ARGS[0] if _ARGS else os.path.join(POV, "TestVideos", "candidates", "rabbit015")
PROMPT_PATH = os.path.join(CAND, "prompt.txt")
STATE_PATH = os.path.join(CAND, "render_state.json")
RAW_PATH = os.path.join(CAND, "render.mp4")

sys.path.insert(0, HERMES)


def load_plugin():
    spec = importlib.util.spec_from_file_location(
        "fal_video_plugin", os.path.join(HERMES, "plugins", "video_gen", "fal", "__init__.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def download(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dst, "wb") as f:
        f.write(r.read())


def main():
    dry = "--dry" in sys.argv
    os.makedirs(CAND, exist_ok=True)
    prompt = open(PROMPT_PATH, encoding="utf-8").read().strip()
    print(f"prompt bytes: {len(prompt.encode('utf-8'))}", flush=True)

    mod = load_plugin()
    family_id, meta = mod._resolve_family(None)
    payload = mod._build_payload(
        meta, prompt=prompt, image_url=None, duration=15, aspect_ratio="9:16",
        resolution="720p", negative_prompt=None, audio=False, seed=None)
    print(f"family={family_id}", flush=True)
    print(f"endpoint={meta['text_endpoint']}", flush=True)
    print("payload keys:", list(payload), flush=True)
    print("payload json bytes:", len(json.dumps(payload).encode("utf-8")), flush=True)
    if dry:
        print("DRY RUN — nothing submitted, nothing spent.")
        return

    handle = mod._submit_fal_video_request(meta["text_endpoint"], payload)
    rid = getattr(handle, "request_id", None)
    print(f"SUBMITTED request_id={rid}", flush=True)
    json.dump({"request_id": rid, "family": family_id, "endpoint": meta["text_endpoint"],
               "prompt_bytes": len(prompt.encode("utf-8")), "submitted": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(STATE_PATH, "w"), indent=2)

    deadline = time.time() + 1500
    status = None
    while time.time() < deadline:
        try:
            status = handle.status(with_logs=False)
        except Exception as exc:                      # transient poll error — keep waiting
            print(f"poll error: {exc}", flush=True)
            time.sleep(10)
            continue
        print(f"[{time.strftime('%H:%M:%S')}] status={status}", flush=True)
        if status in ("COMPLETED", "ERROR", "FAILED"):
            break
        time.sleep(10)
    if status != "COMPLETED":
        print(f"NOT COMPLETED (status={status}) — request_id {rid} kept in {STATE_PATH}", flush=True)
        sys.exit(2)

    result = handle.get()
    video = result.get("video") if isinstance(result, dict) else None
    url = video.get("url") if isinstance(video, dict) else video
    print(f"RESULT URL: {url}", flush=True)
    state = json.load(open(STATE_PATH))
    state.update({"status": "COMPLETED", "url": url})
    json.dump(state, open(STATE_PATH, "w"), indent=2)
    download(url, RAW_PATH)
    print(f"DOWNLOADED {RAW_PATH} ({os.path.getsize(RAW_PATH)} B)", flush=True)


if __name__ == "__main__":
    main()
