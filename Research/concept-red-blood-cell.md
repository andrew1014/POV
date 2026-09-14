# POV Concept — "You Are a Red Blood Cell"

Status: APPROVED by Andrew 2026-09-13 → cheap test render in progress.
Lane: impossible first-person POV (no character, no lip-sync, no continuity — pipeline-friendly).

## Hook
Nobody has ever seen inside their own bloodstream *as* a blood cell. Personal + impossible.

## Beat sheet (15s, one unbroken shot)
| Beat | What the viewer is |
|---|---|
| 0–2s | Inside a dark red artery; glistening, pulsing muscular walls; tide of biconcave cells tumbling past the lens |
| 2–6s | Ejected through a heart valve into a cavernous chamber; valve slams behind; walls flex like a slow fist |
| 6–10s | The squeeze — capillary (2–4 µm) narrower than the cell (7–8 µm); single-file deformation, wall brushes lens |
| 10–13s | The lung — alveoli, bright light floods, cell brightens dull maroon → brilliant scarlet |
| 13–15s | Back at the heart. Loop point. |

End caption: "That whole trip took 60 seconds. You'll make about 1,400 more today."

## Grounded facts (cited)
- Full circuit of the body ≈ **60 s** (Wikipedia, Red blood cell: "take on average 60 seconds to complete one cycle of circulation"); other sources give ~20 s at peak.
- Capillary diameters **2–4 µm** while RBCs are **~7–8 µm** — cells deform to pass single file (PMC8006275, "How Do Red Blood Cells Die?").
- RBC lifespan ~120 days → ~1,440 circuits/day at 60 s each (basis for the caption).

## Prompt
First-person POV from inside a human bloodstream — the camera IS a red blood cell, wet macro-photography
realism, extreme shallow depth of field. Rushing through a dark red artery: glistening muscular walls
pulsing and flexing, translucent biconcave cells tumbling past the lens in a thick tide, subsurface
scattering, deep crimson palette, faint warm glow from the vessel wall. One continuous unbroken shot —
no cuts, no humans, no faces, no text. The vessel opens into a vast translucent heart chamber; a membrane
valve snaps shut behind the camera with a wet slap; the walls crush inward like a slow fist, plasma haze
and light shafts. It narrows into a capillary so tight the lens is squeezed between the walls, wall
texture streaking past in blurred crimson, single-file compression. Then the lung's alveoli: pale pink
translucent membrane, bright white light flooding through, the scene blooming from dark maroon into
glowing scarlet as oxygen saturates the frame. Immersive, visceral, biological, non-graphic, no blood
splatter.

## Pipeline note (verify, don't assume)
`hermes config get video_gen` → provider `nous`, model **`minimax-h3-max`** — NOT the pixverse backend the
POV skill documents. The skill's "pixverse always returns landscape, ignores 9:16" note may not apply.
Confirm real aspect ratio + resolution behaviour from the test render before building the vertical workflow.

## Rejected alternates (for the record)
- Venera 13, 127 minutes on Venus (457 °C / 89 atm) — strong, kept for later.
- The last 8 seconds of a star (core collapse → supernova) — kept for later.
