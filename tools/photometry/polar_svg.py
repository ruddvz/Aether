from __future__ import annotations

from pathlib import Path
import math


def render_polar_svg(report: dict, output: str | Path, plane_index: int = 0, size: int = 800) -> Path:
    """Render a simple normalized polar candela diagram without plotting dependencies."""
    p = Path(output)
    angles = report["photometry"]["verticalAnglesDeg"]
    candela = report["photometry"]["candela"][plane_index]
    peak = max(candela) if candela else 0.0
    if peak <= 0:
        raise ValueError("Cannot render polar diagram with zero candela")

    cx = cy = size / 2
    radius = size * 0.39
    points = []
    for a, cd in zip(angles, candela):
        theta = math.radians(a - 90.0)
        r = radius * (cd / peak)
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append(f"{x:.2f},{y:.2f}")

    grid = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        rr = radius * frac
        grid.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="#d7d7d7" stroke-width="1"/>')
    for deg in (0, 45, 90, 135, 180, 225, 270, 315):
        t = math.radians(deg)
        x = cx + radius * math.cos(t); y = cy + radius * math.sin(t)
        grid.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="#e2e2e2" stroke-width="1"/>')

    max_cd = report["photometry"]["maxCandela"]
    plane = report["photometry"]["horizontalAnglesDeg"][plane_index]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
<rect width="100%" height="100%" fill="#fafafa"/>
<g>{''.join(grid)}</g>
<polyline points="{' '.join(points)}" fill="none" stroke="#171717" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="{cx}" cy="{cy}" r="3" fill="#b88952"/>
<text x="28" y="42" font-family="system-ui, sans-serif" font-size="22" fill="#171717">Normalized polar distribution</text>
<text x="28" y="70" font-family="system-ui, sans-serif" font-size="14" fill="#666">H={plane:g}° · peak {max_cd:g} cd · source values preserved in report JSON</text>
</svg>'''
    p.write_text(svg, encoding="utf-8")
    return p
