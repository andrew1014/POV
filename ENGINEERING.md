# Engineering Notes — POV Pipeline

Design decisions behind the POV production pipeline. Kept separate from the README so the
front page stays a summary.

---

## Evaluation: what stills can and cannot tell you

Rendered clips are reviewed by extracting static frames and inspecting them. This works for
some things and fails badly at others.

**Stills verify finish only:** sharpness, exposure, framing, absence of burned-in text,
correct aspect ratio. Those are properties of a frame and they are visible in a frame.

**Stills cannot judge whether a clip is good.** Motion is the subject of the format, and
motion is blurred in a still by definition. A review pass once rejected a clip because the
mouth region looked smeared in the sampled frames — the frames had caught the animal
mid-gnaw, which is exactly what the clip was supposed to show and looked correct in motion.

The rule: **automated scores are diagnostics, not vetoes.** A clip that measures below a
benchmark but reads well to a human ships. Measurement informs the decision; it does not
make it.

---

## Model selection by measured output, not by preference

Vertical delivery requires a model that renders **natively at 9:16**.

| Model behaviour | Raw output | To reach 1080×1920 | Result |
|-----------------|-----------|-------------------|--------|
| Declares no aspect ratio | 1280×720 landscape | Centre-crop + ~2.7× upscale | Visibly soft |
| Native vertical | 720×1280 | ~1.5× upscale | Acceptable |

The comparison was made by measuring sharpness at **final delivery resolution**. Comparing
previews would have hidden the difference entirely, because previews are small.

---

## Cost discipline

- **Test renders are cheap; finals are not.** Every subject is proven at low resolution
  before a full-resolution render is paid for.
- **Candidates are reviewed side by side**, and only the approved one is rendered at final
  quality.
- **An approved prompt is never modified afterwards.** Rendering an "improved" version of an
  approved prompt invalidates the approval — what was signed off is what ships.

---

## Format choice as risk management

First-person animal POV was selected partly for what it avoids. It has:

- no character-consistency requirement across shots
- no lip-sync
- no continuity stitching between clips

These are the three hardest problems in AI video. The format is chosen to stay on ground
where current models are strong — motion, light, texture — rather than where they are weak.

---

## Assembly

| Stage | Implementation |
|-------|---------------|
| Render | Video model API — native vertical |
| Audio | Real field recordings, mixed at a gentle level; never synthesised |
| Assembly | ffmpeg — 1080×1920, H.264 |
| Verification | Resolution and stream count confirmed before publish |
| Distribution | AI-content label on every upload |