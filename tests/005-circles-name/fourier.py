import numpy as np
from glyph import outline
def rings_of(g):
    geoms = list(getattr(g, "geoms", [g]))
    out = []
    for x in geoms:
        out.append(np.array(x.exterior.coords)[:-1])
        for h in x.interiors: out.append(np.array(h.coords)[:-1])
    return out
def build_path(name, M=4096, scale=1.0):
    g = outline(name)
    rings = rings_of(g)
    # order: by min x of ring (left to right), holes right after their parent naturally by x
    rings.sort(key=lambda r: r[:, 0].min())
    segs = []  # list of (points, pen_down)
    prev_end = None
    for r in rings:
        if prev_end is not None:
            k = np.argmin(np.sum((r - prev_end) ** 2, axis=1))
            r = np.roll(r, -k, axis=0)
        else:
            k = np.argmin(r[:, 0]); r = np.roll(r, -k, axis=0)
        r = np.vstack([r, r[:1]])
        if prev_end is not None:
            segs.append((np.vstack([prev_end, r[0]]), False))
        segs.append((r, True))
        prev_end = r[-1]
    # close back to start (pen up)
    segs.append((np.vstack([prev_end, segs[0][0][0]]), False))
    # resample by arc length; connectors are traversed faster (weight 0.35) so time isn't wasted
    lens = []
    for pts, down in segs:
        d = np.sum(np.hypot(*np.diff(pts, axis=0).T))
        lens.append(d * (1.0 if down else 0.35))
    L = sum(lens)
    P = []; D = []
    for (pts, down), l in zip(segs, lens):
        n = max(2, int(round(M * l / L)))
        dd = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
        s = np.linspace(0, dd[-1], n, endpoint=False)
        x = np.interp(s, dd, pts[:, 0]); y = np.interp(s, dd, pts[:, 1])
        P.append(x + 1j * y); D.append(np.full(n, down))
    z = np.concatenate(P) * scale
    pen = np.concatenate(D)
    return z, pen
def coeffs(z):
    M = len(z)
    c = np.fft.fft(z) / M
    k = np.fft.fftfreq(M, 1 / M).astype(int)
    order = np.argsort(-np.abs(c))
    # keep DC first
    order = [i for i in order if k[i] != 0]
    i0 = int(np.where(k == 0)[0][0])
    return c[i0], c[order], k[order]
def recon(c0, c, k, s, K):
    """positions of chain at parameter s in [0,1); returns array of K+1 points (complex)"""
    terms = c[:K] * np.exp(2j * np.pi * k[:K] * s)
    return c0 + np.concatenate([[0], np.cumsum(terms)])
def trace(c0, c, k, K, n=6000):
    s = np.arange(n) / n
    return c0 + (c[:K, None] * np.exp(2j * np.pi * k[:K, None] * s[None, :])).sum(0), s
if __name__ == "__main__":
    from PIL import Image, ImageDraw
    z, pen = build_path("Emma")
    z = np.conj(z)  # flip y for screen
    c0, c, k = coeffs(z)
    im = Image.new("RGB", (1200, 900), (10, 10, 20)); d = ImageDraw.Draw(im)
    for row, K in enumerate([20, 60, 200]):
        tr, s = trace(c0, c, k, K, 4000)
        pd = pen[(s * len(pen)).astype(int)]
        pts = [(p.real * 4 + 40, p.imag * 4 + 120 + row * 280) for p in tr]
        for a in range(len(pts) - 1):
            if pd[a]: d.line([pts[a], pts[a + 1]], fill=(255, 211, 107), width=3)
    im.save("fourier_test.png")
    print("max |c| radius", np.abs(c[:5]))
