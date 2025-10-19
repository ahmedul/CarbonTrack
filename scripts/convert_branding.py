#!/usr/bin/env python3
"""
Convert SVG branding assets to PNGs for LinkedIn and general use.
Requirements: cairosvg

Outputs:
- branding/logo-mark-1024.png (LinkedIn logo recommended)
- branding/logo-mark-300.png (fallback small)
- branding/banner-linkedin.png (1584x396)
"""
from pathlib import Path

try:
    import cairosvg  # type: ignore
except Exception:
    raise SystemExit("cairosvg is required. Install with: pip install cairosvg")

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "branding"

SVG_LOGO = BRAND / "logo-mark.svg"
SVG_BANNER = BRAND / "banner-linkedin.svg"

PNG_LOGO_1024 = BRAND / "logo-mark-1024.png"
PNG_LOGO_300 = BRAND / "logo-mark-300.png"
PNG_BANNER = BRAND / "banner-linkedin.png"


def convert_svg_to_png(svg_path: Path, png_path: Path, width: int, height: int) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width, output_height=height)
    print(f"✅ Wrote {png_path} ({width}x{height})")


def main() -> None:
    if not SVG_LOGO.exists() or not SVG_BANNER.exists():
        raise SystemExit("Missing branding SVGs. Expected branding/logo-mark.svg and branding/banner-linkedin.svg")

    convert_svg_to_png(SVG_LOGO, PNG_LOGO_1024, 1024, 1024)
    convert_svg_to_png(SVG_LOGO, PNG_LOGO_300, 300, 300)
    convert_svg_to_png(SVG_BANNER, PNG_BANNER, 1584, 396)


if __name__ == "__main__":
    main()
