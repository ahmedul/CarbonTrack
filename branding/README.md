CarbonTrack Branding Kit
========================

This folder contains a lightweight, original branding set for CarbonTrack: a square SVG logo mark suitable for LinkedIn avatars and a LinkedIn cover banner at the correct dimensions.

Contents
- logo-mark.svg — Square logo mark (1:1), works on light and dark backgrounds
- banner-linkedin.svg — LinkedIn cover image (1584×396)
- colors.md — Color palette and usage notes
 - Note: A copy of the logo is used by the app at frontend/assets/logo-mark.svg

Tagline options (pick one)
- Track. Understand. Reduce.
- Carbon tracking made simple.
- Measure today. Reduce tomorrow.

Recommended default: “Track. Understand. Reduce.”

Exporting PNGs
- With Inkscape (recommended):
  inkscape branding/logo-mark.svg --export-type=png --export-filename=branding/logo-mark-1024.png
  inkscape branding/banner-linkedin.svg --export-type=png --export-filename=branding/banner-linkedin.png

- With rsvg-convert:
  rsvg-convert -w 1024 -h 1024 branding/logo-mark.svg > branding/logo-mark-1024.png
  rsvg-convert -w 1584 -h 396 branding/banner-linkedin.svg > branding/banner-linkedin.png

LinkedIn specs
- Logo: square; upload logo-mark-1024.png.
- Cover: 1584×396; keep key text/icons near the center-left to avoid cropping.
