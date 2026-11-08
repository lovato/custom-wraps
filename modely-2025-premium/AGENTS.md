> This file extends the repo-root `AGENTS.md` (UV orientation rules) with the
> verified panel map, safe text sizes, and the visualizer verification workflow
> for this model. Both were confirmed end-to-end on a finished, applied wrap.

# Custom Wrap Guide — Model Y Premium (2025+)

Verified end-to-end on 2026-11-07 with the "Feliz Aniversário" wrap: built
programmatically, then checked panel by panel in the 3D visualizer
(teslawrapgallery.com/visualizer) in the two views that matter —
**Front+Driver+Roof** and **Back**. Everything below is confirmed against
those renders, not just inferred from the flat template.

## Golden rules

- PNG is a UV texture, 1024×1024, ≤ 1 MB. Paint **only** inside the white
  islands of `template.png`; everything outside stays pure black.
- Erode the island mask by ~2 px before final export. Art that touches an
  island edge gets clipped or wraps around a panel edge on the car.
- Compose with code (e.g. PIL) at 2× and downscale. Use generated art for
  loose motifs only; **never let an image generator draw text** — it garbles
  words and cannot hold an orientation.
- Verify every design in the visualizer before calling it done (workflow at
  the bottom). The flat PNG lies about orientation.

## Panel map (1024×1024 PNG coordinates)

PNG top = front of the car, PNG bottom = rear.

| Panel | bbox (x, y) | size |
|---|---|---|
| Front bumper | 245–776, 8–117 | 532×110 |
| Hood | 375–644, 110–338 | 270×229 |
| Front fender L / R | 111–331, 114–366 / 694–911, 114–367 | ~220×253 |
| Mirror L / R | 272–341, 368–406 / 679–748, 367–406 | 70×40 |
| Front door L / R | 82–258, 348–594 / 762–937, 350–595 | ~177×247 |
| Rear door L / R | 69–234, 570–791 / 784–949, 573–795 | 166×222 |
| Cant rail L / R (thin strip by the cabin) | 342–388, 346–810 / 632–678, 347–811 | 47×465 |
| Rear quarter L / R | 124–264, 779–949 / 757–898, 782–952 | ~141×171 |
| Rear pillar strip L / R | 302–356, 814–961 / 666–718, 816–963 | ~54×148 |
| Rear bumper corner L / R | 55–173, 885–1013 / 853–968, 888–1016 | ~118×129 |
| Hatch lip (above the light bar) | 357–663, 874–929 | 307×56 |
| Tailgate (below the light bar) | 396–630, 939–1013 | 235×75 |

Note: the template file also has a white frame around the whole image —
that is **not** paintable area. The islands are the 20 blobs listed above.

## Orientation rules (verified in the visualizer)

### Side panels (fenders, doors, rear quarters)

- PNG vertical axis = vehicle's front-to-rear axis (top = front).
- PNG horizontal axis = roof-to-rocker; the roof side faces the cabin
  (the inner edge of each side island).
- Place upright art/text rotated **90° clockwise on the PNG-left islands**
  and **90° counterclockwise on the PNG-right islands**. In the flat PNG
  the art then looks sideways, with letter tops facing the cabin. On the
  car it reads upright, front to rear.
- Consequence for continuous art: the side column is stacked front→rear in
  the PNG (fender → front door → rear door → quarter), so a ribbon or
  pattern drawn straight through the column in PNG space flows
  continuously across the panels on the car. A phrase can also flow panel
  to panel, e.g. "Feliz" on the front door + "Aniversário!" on the rear
  door reads as one line on the car.

### Hood and front bumper

- Rotate art/text **180°** in the PNG (letter tops toward the windshield).
  It then reads correctly standing in front of the car and in the
  Front+Driver+Roof view.
- Give the text block "padding": keep it off the windshield edge, and keep
  ~15 px margin from the island's front edge — the hood curves down and
  eats edge art.

### Rear (hatch lip + tailgate)

- **Upright in the PNG** = upright on the car. No rotation.
- Hatch lip is only 56 px tall: keep text cap height ≤ ~26 px and centre it
  slightly *below* the island's middle. The panel slants away under the
  rear glass, so anything in its top sliver disappears at level viewing
  angles (it is fine from a normal standing viewpoint, which looks down
  at the panel).
- Tailgate fits one strong line: "Aniversário!" at ~40 px cap height
  across its 235 px width.
- Split-message trick: line 1 on the hatch lip + line 2 on the tailgate
  reads as one two-line sign, split by the light bar.

### Mirrors, cant rails, pillar strips, bumper corners

- Pattern, ribbons or a solid accent colour only. Too small/oddly shaped
  for text or directional art.

## Safe text sizes (from the reference build)

| Placement | Max text length (along panel) | Max cap height |
|---|---|---|
| Front door (rotated) | ~205 px | ~130 px |
| Rear door (rotated) | ~205 px | ~140 px |
| Hood, per line | ~240 px | ~80 px |
| Hatch lip | ~150 px | ~26 px |
| Tailgate | ~210 px | ~58 px |

## Verification workflow

1. Go to https://teslawrapgallery.com/visualizer/, select
   **Model Y Premium (2025+)**.
2. Upload the PNG ("Drop image or click to upload").
3. Check the **Front+Driver+Roof** view (the default) and the **Back**
   view. Those two are what the driver sees ~99% of the time in the car's
   own visualizations.
4. Rotate by dragging: use **slow, small drags** — the viewer has momentum
   and overshoots; wait ~4 s for the view to settle before judging.
5. Judge with real **viewport screenshots**. Printing the page or saving
   it as PDF renders the WebGL canvas as a blank grey box — useless.
6. Read every word in both views. If a word is upside down, mirrored, or
   clipped in either view, the wrap is wrong — fix the PNG, not your eyes.
