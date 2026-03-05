from src.shapes import SHAPES
for name, s in SHAPES.items():
    rows = max(r for r, _ in s) - min(r for r, _ in s) + 1
    cols = max(c for _, c in s) - min(c for _, c in s) + 1
    print(f"{name}: {len(s)} cases, boite {rows}x{cols}")
