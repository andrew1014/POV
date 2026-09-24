# POV — Immersive Animal Shorts

**POV** is a series of AI-generated, first-person short-form videos: the camera is the viewer's own eyes as an animal in a world it was never meant to see up close. Every clip is a 15-second micro-story, rendered vertical for TikTok / YouTube Shorts.

> *"POV: you're a baby piglet running through a flower field. Golden hour. Nowhere to be."*

## What This Repo Is

Public home for the POV channel: production research, the serialized story arc, posting packages, and representative posters. It documents *how* the channel is made and where it's headed — a transparent production log and asset index.

## Series Concept

Two content tracks share one idea: **put the viewer somewhere they'd never physically be, at an animal's eye level.**

- **The "Two Piglets" serial** — a recurring cast built for attachment. You are a piglet; over four chapters you meet a companion, chase a butterfly together, and catch it — a loopable micro-arc. Recurring cast + a second piglet gives the clips continuity most one-off animal shorts lack.
- **One-off animal/nature POV** — pygmy hippo, sea otter, baby aardvark and similar trending subjects, each a self-contained moment.

Chosen because first-person animal POV renders exceptionally well with modern video models: **no character-consistency requirement, no lip-sync, no cross-cut continuity** — the model plays on its home turf (motion, light, texture), hiding the AI tells that plague talking-character work.

## Structure

```
Research/    — Channel strategy, trending-animal analysis, viral-driver research
Production/  — Upload/post packages (captions, titles, hashtags, AI labels, schedules)
posters/     — Representative stills from produced chapters
```

| Directory | Contents | Why |
|-----------|----------|-----|
| `Research/` | `pov-footage-channel-2026-09-04.md` (strategy verdict), `top10-cute-animals-2026-09-04.md` (subject analysis), `pov-two-piglets-arc.md` (serial story arc) | Grounds every creative decision in evidence |
| `Production/` | `TwoPiglets_Ch1-2_upload-package.md` — full launch package | One file to run the debut |
| `posters/` | `ch1_poster.png`, `ch2_poster.png` | Channel + repo imagery |

*(Rendered video masters live locally in the project vault, not in this repo.)*

## The POV Pipeline

1. **Research** — pick a subject and the beat (which moment is the payoff), grounded in trend + viral-driver analysis.
2. **Prompt** — first-person POV at the animal's eye level, over-the-shoulder framing, anti-mirror vocabulary (single subject, off-center, not duplicated), **native vertical 9:16**.
3. **Render** — free PixVerse V6. Tests render cheap; only the approved final renders HD.
4. **Audio** — real nature field recordings (archive.org daytime birdsong) mixed at a gentle level — never synthesized.
5. **Assembly** — verified 1080×1920 vertical, video + audio streams confirmed.
6. **Post** — AI-content label on every upload (synthetic), serial cross-linking, evening drops.

## The "Two Piglets" Arc (4 chapters)

| Ch | Beat | Status |
|----|------|--------|
| 1 | **The Run** — you gallop through a golden flower field | ✅ produced |
| 2 | **The Companion** — a second piglet catches up beside you | ✅ produced |
| 3 | **The Chase** — your friend bounds after a butterfly | 🔜 planned |
| 4 | **The Landing** — the butterfly settles; you both watch (loops to Ch1) | 🔜 planned |

## Engineering Notes

The pipeline is above. This is the part that was genuinely hard, recorded because each of
these cost real time to learn.

### A clip was wrongly rejected because it was judged from stills

Several static frames were extracted from a rendered clip and reviewed before it went out.
One was called a failure — the mouth region looked smeared and the pose read badly. The
creator watched the actual clip and liked it. The frames had been capturing a *motion* —
gnawing — which is inherently blurred in a single frame and perfectly legible in motion.

**The rule that came out of it:** stills verify **finish only** — sharpness, exposure,
framing, no burned-in text, correct aspect. They cannot verify whether a clip is *good*,
because the thing being judged is movement. Automated scores are diagnostics, not vetoes. A
clip that measures below benchmark but that the creator likes ships as-is.

### Model choice was made on measured sharpness, not preference

Vertical output needs a model that renders natively at 9:16. One candidate declared no
aspect ratio and produced 1280×720 landscape, which meant cropping to vertical and
upscaling by roughly 2.7× — noticeably soft, and about five times less sharp at final
resolution than a model rendering native 720×1280.

**Decision:** b-roll uses the model with native vertical output, accepting a gentler 1.5×
upscale. The comparison was made by measuring resolution at final size rather than by
eyeballing previews, because previews hide exactly this class of difference.

### Cheap tests, expensive finals

Every subject is proven with low-resolution test renders before any final render is paid
for. Candidates are reviewed side by side, and only the approved one is rendered at full
resolution — using the **exact** prompt that was approved, not an "improved" version of it.
Improving an approved prompt after the fact invalidates the approval.

### The failure mode this format avoids by design

First-person animal POV was chosen partly because it sidesteps the hardest problems in AI
video: there is no character-consistency requirement across cuts, no lip-sync, and no
continuity to maintain. The model is asked to do what it is good at — motion, light,
texture — rather than what it is bad at.

---

## Why This Channel

- **Near-zero marginal cost** — free video model renders, free field-recording audio, local assembly.
- **Fast to produce** — self-contained 15s clips, no voice, no continuity stitching.
- **Clear upside** — anchored on UGC/stock licensing and brand sponsorships (not ad payout); 15s clips are also re-editable into 60s+ compilations for YouTube monetization.

## Distribution

- **TikTok** (primary — short-form discovery)
- **YouTube Shorts** (secondary)

## Tech Stack

- **Video generation:** PixVerse V6 (FAL)
- **Audio:** real field recordings (archive.org), mixed with ffmpeg
- **Assembly:** ffmpeg (vertical 1080×1920, H.264, verified streams)
- **Research:** trend analysis + viral-driver research

---

*POV is an original AI content project by Andrew Vega.*
