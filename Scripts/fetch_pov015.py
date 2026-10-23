# -*- coding: utf-8 -*-
"""Fetch a completed POV render by request id (after a poll-loop timeout lost the handle).

Reconstructs the fal queue URLs from the managed gateway origin + endpoint + request id,
rehydrates a SyncRequestHandle, and pulls the result JSON.
"""
import importlib.util
import json
import os
import sys
import urllib.request

HERMES = r"C:\Users\avega.VEGANATOR\AppData\Local\hermes\hermes-agent"
CAND = r"E:\APEX\POV\TestVideos\candidates\rabbit015"
STATE = os.path.join(CAND, "render_state.json")
RAW = os.path.join(CAND, "pov015_RAW.mp4")

sys.path.insert(0, HERMES)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    state = json.load(open(STATE))
    rid, endpoint = state["request_id"], state["endpoint"]
    plugin = load(os.path.join(HERMES, "plugins", "video_gen", "fal", "__init__.py"), "fal_video_plugin")
    from tools.fal_common import _normalize_fal_queue_url_format

    gateway = plugin._resolve_managed_fal_video_gateway()
    client = plugin._get_managed_fal_video_client(gateway)
    fmt = _normalize_fal_queue_url_format(gateway.gateway_origin)
    status_url = f"{fmt}{endpoint}/requests/{rid}/status"
    response_url = f"{fmt}{endpoint}/requests/{rid}"
    print(f"request {rid}\nstatus_url {status_url}")

    handle = client._request_handle_class(
        request_id=rid, response_url=response_url, status_url=status_url,
        cancel_url=f"{fmt}{endpoint}/requests/{rid}/cancel", client=client._http_client)
    print("status:", handle.status(with_logs=False))
    result = handle.get()
    video = result.get("video") if isinstance(result, dict) else None
    url = video.get("url") if isinstance(video, dict) else video
    print("URL:", url)
    state.update({"status": "COMPLETED", "url": url})
    json.dump(state, open(STATE, "w"), indent=2)

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(RAW, "wb") as f:
        f.write(r.read())
    print(f"DOWNLOADED {RAW} ({os.path.getsize(RAW)} B)")


if __name__ == "__main__":
    main()
