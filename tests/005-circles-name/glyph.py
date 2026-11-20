import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.ops import unary_union
fp = FontProperties(fname="/home/claude/kit/fonts/Pacifico.ttf")
def area(q):
    x, y = q[:, 0], q[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
def outline(name):
    p = TextPath((0, 0), name, size=100, prop=fp)
    qs = [np.array(q) for q in p.to_polygons() if len(q) > 2]
    A = [area(q) for q in qs]
    sgn = np.sign(max(A, key=abs))  # outer orientation = biggest contour's
    outer = unary_union([Polygon(q).buffer(0) for q, a in zip(qs, A) if np.sign(a) == sgn])
    holes = [Polygon(q).buffer(0) for q, a in zip(qs, A) if np.sign(a) != sgn]
    g = outer.difference(unary_union(holes)) if holes else outer
    return g
if __name__ == "__main__":
    for name in ["Olivia", "Emma", "Sophia", "Liam", "Noah", "Mia", "Lucas", "Amelia", "Charlotte", "Isabella"]:
        g = outline(name)
        geoms = list(getattr(g, "geoms", [g]))
        rings = sum(1 + len(x.interiors) for x in geoms)
        print(f"{name:10s} parts {len(geoms)} rings {rings}")
