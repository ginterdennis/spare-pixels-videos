import numpy as np
GW, GH = 54, 96
def hexc(h): h = h.lstrip("#"); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float)
def scene():
    a = np.zeros((GH, GW, 3))
    yy, xx = np.mgrid[0:GH, 0:GW]
    # sky gradient
    top, hor = hexc("#1C4FBF"), hexc("#86CDF5")
    t = np.clip(yy / 50, 0, 1)[..., None]
    a[:] = top * (1 - t) + hor * t
    # sun
    d = np.hypot(xx - 41, yy - 17)
    a[d < 9.5] = hexc("#FFB52E"); a[d < 7.5] = hexc("#FFE34D")
    # puffy clouds (union of circles)
    for cx, cy, sc in [(10, 13, 1.0), (17, 27, 0.8), (45, 34, 0.9)]:
        for ox, oy, r in [(-3, 0, 2.6), (0, -1.5, 3.3), (3.5, 0, 2.6), (6, 0.8, 1.9), (-5.5, 0.8, 1.7)]:
            m = np.hypot(xx - (cx + ox * sc), (yy - (cy + oy * sc)) * 1.0) < r * sc
            m &= yy <= cy + 1.5 * sc
            a[m] = hexc("#FFFFFF")
    # mountains (violet)
    ridge = 47 - 7 * np.abs(np.sin((xx[0] + 3) / 7.5)) - 3 * np.abs(np.sin(xx[0] / 3.1))
    for x in range(GW):
        a[int(ridge[x]):, x] = hexc("#7A4FC9")
        a[int(ridge[x]):int(ridge[x]) + 2, x] = hexc("#9A72E0")
    # hills (green), two layers
    h1 = 55 - 3 * np.sin(xx[0] / 6.0)
    h2 = 61 - 3 * np.sin(xx[0] / 4.5 + 1.5)
    for x in range(GW):
        a[int(h1[x]):, x] = hexc("#3FAF3A")
        a[int(h2[x]):, x] = hexc("#2E8F2C")
    # tulip field: rows from y=68 down, thicker towards bottom
    y = 68; k = 0
    cols = [hexc("#E8262B"), hexc("#FF7A1A"), hexc("#E8268E"), hexc("#FFD21F")]
    while y < GH:
        th = 1 + k // 2
        a[y:y + th, :] = cols[k % 4]
        y += th
        g = 1 + k // 3
        a[y:y + g, :] = hexc("#2A8A2E")
        y += g; k += 1
    # hot-air balloon at centre (fixation dot sits on it)
    cx, cy = 27, 45
    d = ((xx - cx) / 8.0) ** 2 + ((yy - cy) / 9.5) ** 2
    bal = d < 1
    stripes = ((xx - cx + 40) // 3) % 2 == 0
    a[bal & stripes] = hexc("#E8262B"); a[bal & ~stripes] = hexc("#FFD21F")
    a[(yy == cy) & bal] = hexc("#1C4FBF")
    # ropes + basket
    a[54:56, 23] = hexc("#5A3A1A"); a[54:56, 31] = hexc("#5A3A1A")
    a[56:59, 24:31] = hexc("#8B5A2B")
    return a.clip(0, 255)
# ---- colour science: sRGB <-> Lab
def srgb2lin(c): c = c / 255; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255
M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
WP = np.array([0.95047, 1.0, 1.08883])
def f(t): return np.where(t > (6 / 29) ** 3, np.cbrt(t), t / (3 * (6 / 29) ** 2) + 4 / 29)
def finv(t): return np.where(t > 6 / 29, t ** 3, 3 * (6 / 29) ** 2 * (t - 4 / 29))
def rgb2lab(rgb):
    xyz = srgb2lin(rgb) @ M.T / WP
    fx, fy, fz = f(xyz[..., 0]), f(xyz[..., 1]), f(xyz[..., 2])
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], -1)
def lab2rgb(lab):
    fy = (lab[..., 0] + 16) / 116; fx = fy + lab[..., 1] / 500; fz = fy - lab[..., 2] / 200
    xyz = np.stack([finv(fx), finv(fy), finv(fz)], -1) * WP
    return lin2srgb(xyz @ np.linalg.inv(M).T)
def adapt_image(rgb, L=62, chroma=1.25):
    lab = rgb2lab(rgb)
    out = np.stack([np.full(lab.shape[:2], L), -lab[..., 1] * chroma, -lab[..., 2] * chroma], -1)
    return lab2rgb(out).clip(0, 255)
def gray_image(rgb):
    lab = rgb2lab(rgb)
    L = lab[..., 0]
    L = 50 + (L - 50) * 1.05
    return lab2rgb(np.stack([L, np.zeros_like(L), np.zeros_like(L)], -1)).clip(0, 255)
if __name__ == "__main__":
    from PIL import Image
    s = scene()
    ims = [s, adapt_image(s), gray_image(s)]
    st = np.concatenate([np.kron(x, np.ones((6, 6, 1))) for x in ims], 1)
    Image.fromarray(st.astype(np.uint8)).save("scene_test.png")
