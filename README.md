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
