# Underfoot — Channel Brief

**Brand:** Underfoot · **Handle:** `@underfootpov` · **Tagline:** POV from a world you walk past.
**Lane:** silent, immersive, first-person POV of things you'd never normally see — the vantage is the marvel.
**Sibling channel:** NOVA (`@nova.transmits`) — deep-space AI consciousness, talking transmissions. Different brand, same universe.

## Positioning
- NOT a generic cute-animal page. The hook is **an impossible vantage**, not a cute animal.
- **No narration, no talking, no burned text.** The hook lives in the title/description only.
- Clip length 8–15s, vertical 1080×1920, real ambience bed, no music sting.

## The proven prompt formula (see skill `ai-pov-video-channel`)
1. The model **cannot render pure embodiment** — never write "the camera IS the X"; it invents a subject instead.
2. Creature close-ups expose AI tells (plastic wings, doll eyes). Keep the creature small or partial.
3. **Win condition:** environment-dominant macro + scale shift + golden-hour light; the vantage is the never-seen thing.
4. Render with `video_generate(model="pixverse-v6", resolution="1080p", duration=15)` — the configured default `minimax-h3-max` is billing-blocked (HTTP 409).
5. pixverse returns **1280×720 landscape** regardless of `aspect_ratio` → vertical is always made in post (blur-pad).

## Production pipeline
- Test renders 480p/5s (cents) → frame-verify → HD 1080p pass only after Andrew approves.
- Finish: blur-pad to 1080×1920 → ambience bed (vary the source offset per clip) → **no captions**.
- Scripts: `POV\Scripts\build_pov_finals.py`, `pov_ant_finish.py`.
- Audio source: `%LOCALAPPDATA%\Temp\english_meadow.mp3` (real daytime meadow birdsong; pull a DIFFERENT window per clip).

## Folders
- `POV\Videos\` — upload-ready finals ONLY · `POV\TestVideos\<subject>\` — tests/reviews · `POV\Production\` — one posting package per clip · `POV\Branding\` — avatar/logo · `POV\Research\` — research docs · `POV\Archive\` — superseded.

## Channel assets
- Avatar: `POV\Branding\underfoot_avatar_1024.png` (dew drop at sunrise, from the ant clip's 14s frame).

## Platform rules
- 1080×1920 H.264; **AI label required everywhere**: YouTube → Altered content → Synthetic · TikTok → "AI-generated content" toggle · IG → AI info.
- Uploads happen in Andrew's signed-in browser — never claim a post is live.

## Posting cadence
- Launch clip ASAP, then 1 clip every 2–3 days.
- YouTube Tue 6pm ET · TikTok Wed 9am + Sat 7pm ET · Reels Thu 2pm ET.
- Reply to every comment in week one.

## Open items
- TikTok / Instagram availability for `@underfootpov` still unverified (needs the Chrome remote-debugging Allow click).
- Chibi "filmmaker" mascot: image generation is configured (fal · flux-2-klein) but no image tool was exposed in the build session — resolve before producing.
