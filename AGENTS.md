# Custom Wrap UV Guidelines

## Model Y Premium (2025+) orientation

The PNG is a UV texture, not a top-down preview of how graphics appear on the
car. Never assume that text which is upright in `template.png` will be upright
on the rendered vehicle.

For the tall side-door islands in `modely-2025-premium/template.png`:

- The PNG's vertical axis maps along the vehicle's front-to-rear axis.
- The PNG's horizontal axis maps along the door's roof-to-rocker axis.
- Rotate upright side-view text and logos **90° clockwise on the left PNG
  islands** (the islands left of the central black cabin).
- Rotate upright side-view text and logos **90° counterclockwise on the right
  PNG islands**.
- Mirror the placement between sides, but do not mirror readable text.

Therefore, door numbers such as `95` should look sideways and face inward
toward the central cabin in the flat PNG. After UV mapping, both sides should
read normally from outside the vehicle.

Before delivering a wrap:

1. Compare directional artwork with Tesla's official examples, especially
   `modely-2025-premium/example/Ani.png` and `Vintage_Stripes.png`.
2. Mentally rotate the left side counterclockwise and the right side clockwise
   to preview each side of the vehicle.
3. Preserve the exact template mask: paint only white islands and keep all
   surrounding pixels black.
4. Export a 512–1024 px square PNG no larger than 1 MB.
