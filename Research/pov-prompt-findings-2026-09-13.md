# POV Prompt Findings — 2026-09-13 (5-test campaign)

Goal set by Andrew: creativity at an 11, POVs of things you'd never normally see. Research first,
pitch before generating.

## What failed (all cheap 5s / 480p pixverse-v6 tests)
| Test | Concept | Result |
|---|---|---|
| 1 | "camera IS a red blood cell" | Invented a floating **anatomical heart diagram** (3rd person). Stylized, golden sparkles, gummy cells. |
| 2 | Blood cell, hard-locked POV + negatives | Stayed inside a tunnel (better) but smoky abstract walls, gummy candy cells, sparkles survived. |
| 3 | "camera IS the firefly's light" | Invented a large blurred **bee**, followed from behind. Not POV at all. |
| 4 | Rider's-eye on a hummingbird | Real bird + gorgeous garden light, but POV drifted to side-view halfway; fabric wings, doll-like eye. |
| 5 | Extreme low macro "ant's world" — towering backlit grass, boulder dew drops, legs at frame edge | ✅ **PHOTOREAL** — "indistinguishable from high-end macro nature footage." |

## The rule
- The model **cannot render pure embodiment** — it always materialises a subject. Never write "the camera is X".
- Creature close-ups (faces, wings, eyes) expose AI tells. Keep the creature small/partial.
- Win condition: **environment-dominant macro + scale shift + golden-hour light**, with the vantage
  as the never-seen thing.

## Accepted prompt (test 5)
Extreme low macro first-person POV, camera just centimetres above the forest floor at sunrise. The viewer
is an ant walking: two thin glossy black ant legs enter the bottom edge of the frame, slightly out of
focus, stepping rhythmically. A forest of grass stalks towers overhead like pillars, strongly backlit by
a low golden sun, glowing edges. Dew drops the size of boulders cling to the blades, each refracting the
light into warm flare. One heavy dew drop trembles, swells, and falls past the camera. Wet soil and
pebbles below, shallow depth of field, photoreal macro nature documentary realism, fine organic sensor
noise, no humans, no faces, no text, no cartoon look, one continuous unbroken shot.

## Test clips
- POV/TestVideos/bloodcell/ (2) · TestVideos/firefly/ (1) · TestVideos/hummingbird/ (1) · TestVideos/ant/ (1)

## Pipeline facts confirmed
- Default `video_gen` model `minimax-h3-max` is billing-blocked (HTTP 409) — must pass `model="pixverse-v6"`.
- pixverse-v6 returns **1280×720 landscape** even with `aspect_ratio: 9:16`, 24 fps, **no audio stream**.
