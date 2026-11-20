import numpy as np
GW, GH, S = 135, 240, 8
B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
YY, XX = np.mgrid[0:GH, 0:GW]
BAY = B4[YY % 4, XX % 4]
def hx(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
def canvas(): return np.zeros((GH, GW, 3))
def dgrad(a, y0, y1, pal, mask=None):
    P = np.array([hx(p) for p in pal]); k = len(P)
    p = np.clip((YY - y0) / max(1, (y1 - y0)), 0, 1) * (k - 1)
    idx = np.clip(np.floor(p + BAY).astype(int), 0, k - 1)
    m = (YY >= y0) & (YY < y1)
    if mask is not None: m &= mask
    a[m] = P[idx][m]
def disc(a, cx, cy, r, c, mask=None):
    m = (XX - cx) ** 2 + (YY - cy) ** 2 <= r * r
    if mask is not None: m &= mask
    a[m] = hx(c) if isinstance(c, str) else c
    return m
def stars(a, n, ymax, seed, cols=("#FFFFFF", "#BFD4FF", "#FFE9B0"), sparkle=4):
    r = np.random.default_rng(seed)
    for i in range(n):
        x, y = r.integers(1, GW - 1), r.integers(1, ymax)
        c = hx(cols[r.integers(len(cols))]) * r.uniform(0.55, 1.0)
        a[y, x] = c
        if i < sparkle:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): a[y + dy, x + dx] = c * 0.6
def ridge(x, base, amps, seed):
    r = np.random.default_rng(seed); y = np.full(len(x), float(base))
    for A, f in amps:
        y += A * np.sin(x * f + r.uniform(0, 6.28))
    return y
def fill_below(a, yline, c, shade=None):
    m = YY >= yline[None, :].round()
    a[m] = hx(c) if isinstance(c, str) else c
    return m
def peaks(x, base, n, h, seed, w=(14, 26)):
    r = np.random.default_rng(seed); y = np.full(len(x), float(base))
    for _ in range(n):
        cx = r.uniform(-10, GW + 10); hh = r.uniform(h * 0.5, h); ww = r.uniform(*w)
        y = np.minimum(y, base - hh + np.abs(x - cx) * hh / ww)
    return y
X = np.arange(GW)

def aurora():
    a = canvas()
    dgrad(a, 0, 175, ["#060A1C", "#0A1230", "#0F1C44", "#152A58", "#1B3A6A", "#24507C"])
    stars(a, 70, 120, 1)
    # aurora ribbons (smooth, layered)
    for k, (base, amp, f1, f2, col_lo, col_hi, height) in enumerate([
            (92, 12, 15.0, 5.5, "#2AF2A2", "#6E7CF0", 34), (104, 8, 10.0, 4.1, "#1FD8B0", "#B06EF0", 22)]):
        yc = base + amp * np.sin(X / f1 + k) + 4 * np.sin(X / f2 + 2 * k)
        ray = 0.65 + 0.35 * np.sin(X / 2.3 + k) * np.sin(X / 9.0)
        d = (yc[None, :] - YY)
        inten = np.where(d >= 0, np.exp(-d / height), np.exp(-(d / 3.0) ** 2)) * ray[None, :]
        lv = np.floor(inten * 3 + BAY).clip(0, 3) / 3
        tcol = np.clip(d / (height * 1.6), 0, 1)[..., None]
        C = hx(col_lo)[None, None, :] * (1 - tcol) + hx(col_hi)[None, None, :] * tcol
        a[:] = a * (1 - lv[..., None] * 0.7) + C * lv[..., None] * 0.7
    # back mountains with snow caps
    r1 = peaks(X, 168, 7, 48, 3)
    mb = YY >= r1[None, :]
    a[mb] = hx("#26335E")
    snow = mb & (YY < r1[None, :] + 7 + 2 * np.sin(X / 3)[None, :]) & (YY < 150)
    a[snow] = hx("#B9C8EA")
    # front ridge
    r2 = peaks(X, 196, 6, 34, 9, w=(18, 30))
    mf = YY >= r2[None, :]
    a[mf] = hx("#141C38")
    a[mf & (YY < r2[None, :] + 3) & (YY < 186)] = hx("#7F93C4")
    # snow field
    dgrad(a, 200, 240, ["#C7D5F2", "#AEBFE6", "#8FA3D3", "#7286BC"])
    # pines
    r = np.random.default_rng(5)
    for _ in range(26):
        cx = r.integers(0, GW); base = r.integers(198, 230); h = r.integers(10, 24)
        for k in range(h):
            w = int((k / h) * h * 0.38) + 1
            yy = base - h + k
            a[yy, max(0, cx - w):min(GW, cx + w + 1)] = hx("#0B1428") if k % 4 else hx("#132040")
        a[base:base + 2, cx] = hx("#0B1428")
    # cabin with lit window
    cx, cy = 96, 214
    a[cy - 8:cy, cx - 9:cx + 9] = hx("#3A2A2A")
    for k in range(7): a[cy - 8 - k, cx - 10 + k:cx + 10 - k] = hx("#D9E4FA") if k < 2 else hx("#2A1E22")
    a[cy - 6:cy - 2, cx - 6:cx - 2] = hx("#FFD36B"); a[cy - 6:cy - 2, cx + 2:cx + 6] = hx("#FFC24A")
    a[cy - 18:cy - 12, cx + 5:cx + 7] = hx("#2A1E22")
    for k in range(5): a[cy - 20 - k * 3, cx + 6 + (k % 2)] = hx("#8FA3D3")
    return a

def sunset():
    a = canvas()
    dgrad(a, 0, 150, ["#1E0B44", "#3B1263", "#6A1F86", "#A8338E", "#D9497E", "#F46F64", "#FF9A55", "#FFC46B"])
    # cloud strips
    r = np.random.default_rng(2)
    for _ in range(9):
        y = r.integers(40, 128); x0 = r.integers(-20, GW); L = r.integers(18, 50)
        a[y, max(0, x0):min(GW, x0 + L)] = a[y, max(0, x0):min(GW, x0 + L)] * 0.5 + hx("#FFB3C1") * 0.5
        a[y + 1, max(0, x0 + 4):min(GW, x0 + L - 6)] = a[y + 1, max(0, x0 + 4):min(GW, x0 + L - 6)] * 0.6 + hx("#E06A9A") * 0.4
    # retro sun
    m = (XX - 67) ** 2 + (YY - 138) ** 2 <= 30 ** 2
    m &= YY < 150
    sp = np.clip((YY - 108) / 42, 0, 1)
    sunc = hx("#FFE59A")[None, None, :] * (1 - sp[..., None]) + hx("#FF8A4A")[None, None, :] * sp[..., None]
    gaps = (YY > 124) & (((YY - 124) % 6) < ((YY - 124) // 6 + 1) * 0.8)
    a[m & ~gaps] = sunc[m & ~gaps]
    # sea
    dgrad(a, 150, 240, ["#4A1E70", "#3A1860", "#2A1250", "#1C0C3C", "#120828"])
    # reflection dashes
    for y in range(151, 238):
        k = (y - 150) / 90
        w = 30 * (1 - k * 0.6)
        for _ in range(3):
            if r.random() < 0.85:
                x0 = 67 + r.uniform(-w, w); L = r.integers(2, 9)
                c = hx("#FFC46B") if r.random() < 0.6 else hx("#FF7A7A")
                xs = slice(int(max(0, x0 - L / 2)), int(min(GW, x0 + L / 2)))
                a[y, xs] = a[y, xs] * 0.2 + c * 0.8 * (1 - k * 0.5)
    a[150, :] = hx("#FFB06B")
    # birds
    for bx, by in [(30, 70), (37, 64), (100, 52)]:
        a[by, bx] = a[by + 1, bx + 1] = a[by + 1, bx - 1] = hx("#2A0F3A")
        a[by - 1, bx + 2] = a[by - 1, bx - 2] = hx("#2A0F3A")
    return a

def neon():
    a = canvas()
    dgrad(a, 0, 150, ["#07041A", "#0D0628", "#170A3A", "#2A0D50", "#4A1268", "#6E1A78"])
    stars(a, 25, 70, 4, cols=("#FFFFFF", "#FF9AE6"), sparkle=1)
    gm = np.hypot(XX - 70, YY - 74)
    for rr, c, al in [(40, "#FF4FB0", 0.18), (30, "#FF6FC0", 0.25), (22, "#FF9AD6", 1.0)]:
        m = (gm < rr) & ((BAY < al) if al < 1 else True)
        a[m] = hx(c) if al == 1 else a[m] * 0.5 + hx(c) * 0.5
    a[(gm < 22) & (((YY - 56) % 5) == 0) & (YY > 74)] = hx("#2A0D50")
    r = np.random.default_rng(7)
    # back buildings
    x = 0
    while x < GW:
        w = r.integers(8, 16); h = r.integers(40, 80); top = 175 - h
        a[top:200, x:x + w] = hx("#1A0E36")
        for yy in range(top + 3, 198, 4):
            for xx in range(x + 2, min(GW, x + w - 1), 3):
                if r.random() < 0.35: a[yy, xx] = hx("#5A3A8A")
        x += w + r.integers(0, 3)
    # front buildings
    x = -4
    while x < GW:
        w = r.integers(14, 26); h = r.integers(60, 112); top = 205 - h
        x0, x1 = max(0, x), min(GW, x + w)
        a[top:206, x0:x1] = hx("#0C0820")
        a[top, x0:x1] = hx("#2A1A50")
        for yy in range(top + 4, 202, 5):
            for xx in range(x0 + 2, x1 - 1, 3):
                if r.random() < 0.45:
                    a[yy:yy + 2, xx] = hx(r.choice(["#34E1FF", "#FF4FB0", "#FFD36B", "#7A6CFF"])) * r.uniform(0.6, 1)
        if r.random() < 0.6 and x1 - x0 > 6:
            sx = x0 + 2; sy = top + r.integers(8, 30); L = r.integers(10, 26)
            c = hx(r.choice(["#FF4FB0", "#34E1FF"]))
            a[sy:sy + L, sx] = c; a[sy:sy + L, sx + 1] = c * 0.5
        x += w
    # street + reflections
    dgrad(a, 206, 240, ["#120A26", "#0C071C", "#080414"])
    for xx in range(GW):
        col = a[150:204, xx].max(0)
        for yy in range(207, 240):
            if r.random() < 0.18:
                a[yy, xx] = a[yy, xx] * 0.4 + a[204 - (yy - 206) * 2 % 54, xx] * 0.6
    # rain
    for _ in range(110):
        x, y = r.integers(0, GW), r.integers(0, 236)
        for k in range(3):
            if 0 <= x - k < GW: a[y + k, x - k // 2] = a[y + k, x - k // 2] * 0.5 + hx("#9FB6E8") * 0.5
    return a

def forest():
    a = canvas()
    dgrad(a, 0, 160, ["#081414", "#0C1E1C", "#112A24", "#173A2E", "#1F4A38", "#2A5C44"])
    stars(a, 30, 60, 8, sparkle=2)
    disc(a, 38, 52, 16, "#E9F2D8"); disc(a, 33, 48, 3, "#CBD8BC"); disc(a, 43, 58, 2, "#CBD8BC")
    r = np.random.default_rng(3)
    layers = [(140, "#2F5E4C", "#3E7560", 40, 15), (172, "#1E4134", "#2A5444", 52, 13), (210, "#10261F", "#173329", 66, 11)]
    for li, (base, c, c2, hmax, step) in enumerate(layers):
        # soft fog glow behind this layer
        fg = np.clip(1 - np.abs(YY - (base - 4)) / 16, 0, 1)
        fm = BAY < fg * 0.45
        a[fm] = a[fm] * 0.7 + hx("#7FB69A") * 0.3
        a[base:] = hx(c)
        x = -6
        while x < GW + 6:
            h = r.integers(int(hmax * 0.6), hmax); top = base - h
            tiers = 4; th = h // tiers
            for k in range(h):
                ti = min(tiers - 1, k // max(1, th))
                w = int((k - ti * th) * 0.75) + ti + 1
                yy = top + k
                xs = slice(max(0, x - w), min(GW, x + w + 1))
                a[yy, xs] = hx(c)
                if 0 <= x - w < GW and (k - ti * th) > 1: a[yy, max(0, x - w)] = hx(c2)
            a[base - 2:base + 1, max(0, x - 1):min(GW, x + 1)] = hx(c)
            x += r.integers(step - 4, step + 4)
    dgrad(a, 205, 240, ["#0C1D17", "#09150F", "#060E0A"])
    # mushrooms
    for mx in [22, 90, 112]:
        a[226:230, mx] = hx("#E8DCC0"); a[224:226, mx - 2:mx + 3] = hx("#D6453A"); a[224, mx] = hx("#FFFFFF")
    # fireflies
    for _ in range(26):
        x, y = r.integers(4, GW - 4), r.integers(120, 232)
        g = hx("#FFE27A")
        a[y, x] = g
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): a[y + dy, x + dx] = a[y + dy, x + dx] * 0.4 + g * 0.6
    return a

def lighthouse():
    a = canvas()
    dgrad(a, 0, 150, ["#050A1E", "#0A1430", "#102044", "#173058", "#20426C", "#2E5880"])
    stars(a, 80, 120, 31, sparkle=5)
    mm = disc(a, 30, 48, 11, "#F2F0E0"); a[mm & ((XX - 34) ** 2 + (YY - 45) ** 2 <= 100)] = hx("#2A3A5E")
    # beam from lamp to the left
    lx, ly = 104, 112
    ang = np.arctan2(YY - ly, XX - lx)
    beam = (np.abs(ang - np.pi * 0.97) < 0.11 + 0.0006 * np.abs(XX - lx)) & (XX < lx)
    fade = np.clip(1 - (lx - XX) / 130, 0, 1)
    bm = beam & (BAY < fade * 0.8)
    a[bm] = a[bm] * 0.45 + hx("#FFF0B8") * 0.55
    # sea
    dgrad(a, 150, 240, ["#2A4E78", "#1E3C64", "#152D50", "#0E203C", "#08152A"])
    r = np.random.default_rng(13)
    for y in range(152, 238):
        for _ in range(2):
            if r.random() < 0.7:
                x0 = 30 + r.uniform(-14, 14) * (1 + (y - 150) / 60); L = r.integers(2, 7)
                xs = slice(int(max(0, x0)), int(min(GW, x0 + L)))
                a[y, xs] = a[y, xs] * 0.3 + hx("#E8E6D0") * 0.7 * (1 - (y - 150) / 140)
    for _ in range(60):
        y, x = r.integers(152, 238), r.integers(0, GW)
        a[y, x:x + 3] = a[y, x:x + 3] * 0.6 + hx("#5A82B0") * 0.4
    a[150, :] = hx("#3E6A98")
    # cliff on the right
    top = 122 + 3 * np.sin(X / 4.0)
    cm = (YY >= top[None, :]) & (XX >= 86 - (YY - 122) * 12 / 28)
    a[cm] = hx("#0C1424")
    a[cm & (YY < top[None, :] + 2)] = hx("#2A3A52")
    # lighthouse tower
    for y in range(ly + 4, 124):
        w = 3 + (y - ly) // 4
        stripe = ((y - ly) // 5) % 2 == 0
        a[y, lx - w:lx + w + 1] = hx("#E9E4D8") if stripe else hx("#D2463C")
        a[y, lx + w] = a[y, lx + w] * 0.6
    a[ly - 5:ly + 4, lx - 4:lx + 5] = hx("#2A2A36")
    a[ly - 3:ly + 2, lx - 3:lx + 4] = hx("#FFE27A")
    a[ly - 8:ly - 5, lx - 3:lx + 4] = hx("#D2463C"); a[ly - 9, lx - 1:lx + 2] = hx("#D2463C")
    # small boat
    bx, by = 52, 176
    a[by, bx - 6:bx + 7] = hx("#0A1222"); a[by + 1, bx - 5:bx + 6] = hx("#0A1222")
    for k in range(9): a[by - 1 - k, bx:bx + max(1, (9 - k) // 2)] = hx("#C9D3E6")
    a[by - 11:by, bx - 1] = hx("#0A1222")
    return a

def desert():
    a = canvas()
    dgrad(a, 0, 185, ["#0B0926", "#16114A", "#271A66", "#3E2479", "#5E2F84", "#86418A", "#B05A86"])
    a[185:] = hx("#B05A86")
    stars(a, 60, 110, 12)
    m = disc(a, 88, 66, 30, "#F3E8CF")
    shade = m & ((XX - 98) ** 2 + (YY - 60) ** 2 > 32 ** 2)
    a[shade] = hx("#D8CBAE")
    for cx, cy, rr in [(80, 58, 5), (95, 76, 4), (100, 54, 3), (76, 78, 3)]:
        disc(a, cx, cy, rr, "#DCCFB2", mask=m)
    # dunes: three layers, lit/shadow by slope
    dunes = [(170, "#7A4A72", "#5A3460", 10), (190, "#C77E5A", "#8E4C42", 13), (214, "#E8AD66", "#AE6A44", 16)]
    for i, (base, lit, sh, A) in enumerate(dunes):
        y = base + A * np.sin(X / (16 + i * 6) + i * 2) + A * 0.4 * np.sin(X / 7 + i)
        dy = np.gradient(y)
        mm = YY >= y[None, :]
        full = np.where(np.broadcast_to((dy[None, :] > 0), (GH, GW))[..., None], hx(sh), hx(lit))
        a[mm] = full[mm]
        crest = mm & (YY < y[None, :] + 1.5)
        a[crest] = hx("#FFD49A") if i == 2 else a[crest] * 1.15
    # cactus on middle dune
    cx = 30; base = int(190 + 13 * np.sin(cx / 22 + 2) + 13 * 0.4 * np.sin(cx / 7 + 1))
    a[base - 22:base, cx - 1:cx + 2] = hx("#1F3A2A")
    a[base - 14:base - 11, cx - 5:cx - 1] = hx("#1F3A2A"); a[base - 20:base - 13, cx - 5:cx - 3] = hx("#1F3A2A")
    a[base - 10:base - 7, cx + 2:cx + 5] = hx("#1F3A2A"); a[base - 16:base - 9, cx + 4:cx + 6] = hx("#1F3A2A")
    return a

def space():
    a = canvas()
    dgrad(a, 0, 240, ["#04020C", "#070414", "#0A061C", "#0C0822", "#0A061C", "#05030E"])
    r = np.random.default_rng(21)
    # nebula blobs
    neb = np.zeros((GH, GW))
    for _ in range(14):
        cx, cy, s = r.uniform(0, GW), r.uniform(0, GH), r.uniform(12, 34)
        neb += np.exp(-(((XX - cx) ** 2 + (YY - cy) ** 2) / (2 * s * s))) * r.uniform(0.3, 0.8)
    neb = neb / neb.max()
    cA, cB = hx("#5B2A9A"), hx("#1E5FA8")
    mix = np.clip((XX / GW + YY / GH) / 2, 0, 1)[..., None]
    ncol = cA * (1 - mix) + cB * mix
    lvl = np.floor(neb * 4 + BAY).clip(0, 4) / 4
    a[:] = a * (1 - lvl[..., None] * 0.7) + ncol * lvl[..., None] * 0.7
    stars(a, 160, 238, 22, sparkle=8)
    # planet
    cx, cy, R = 62, 140, 36
    pm = (XX - cx) ** 2 + (YY - cy) ** 2 <= R * R
    bands = ["#F2C59A", "#E09A6A", "#C9734F", "#F0B585", "#B9603F", "#E7A774"]
    bi = (((YY - cy + R) / 7 + 0.4 * np.sin(XX / 5)).astype(int)) % len(bands)
    pc = np.stack([hx(b) for b in bands])[bi]
    light = np.clip(1 - ((XX - cx + 14) ** 2 + (YY - cy + 14) ** 2) / (2.2 * R * R), 0.25, 1)
    light = np.floor(light * 5 + BAY) / 5
    # ring
    def ring_mask(front):
        u = (XX - cx) * np.cos(-0.35) - (YY - cy) * np.sin(-0.35)
        v = (XX - cx) * np.sin(-0.35) + (YY - cy) * np.cos(-0.35)
        e = (u / 62) ** 2 + (v / 13) ** 2
        rm = (e < 1) & (e > 0.62)
        return rm & ((v > 0) if front else (v <= 0))
    rb = ring_mask(False)
    a[rb] = hx("#CBB7E8") * (0.7 + 0.3 * (BAY[rb] > 0.5))[:, None]
    a[pm] = (pc * light[..., None])[pm]
    rf = ring_mask(True)
    a[rf] = hx("#E6D8FA") * (0.75 + 0.25 * (BAY[rf] > 0.5))[:, None]
    # small moon
    mm = disc(a, 108, 58, 8, "#9FA6C4")
    a[mm & ((XX - 111) ** 2 + (YY - 55) ** 2 > 81)] = hx("#5E6488")
    return a

def blossom():
    a = canvas()
    dgrad(a, 0, 175, ["#7FA8E2", "#9DB4EA", "#BDB9EC", "#DABFE6", "#F3C6DA", "#FFD6CF", "#FFE6C8"])
    # sun glow low
    gm = ((XX - 30) ** 2 + (YY - 160) ** 2) < 26 ** 2
    a[gm & (BAY < 0.5)] = a[gm & (BAY < 0.5)] * 0.7 + hx("#FFF4DA") * 0.3
    # distant mountains
    r1 = peaks(X, 178, 5, 40, 31, w=(26, 40))
    mm = YY >= r1[None, :]; a[mm] = hx("#A6A6D8")
    a[mm & (YY < r1[None, :] + 4) & (YY < 152)] = hx("#F2F0FF")
    r2 = 190 + 6 * np.sin(X / 18) ; m2 = YY >= r2[None, :]; a[m2] = hx("#8E9CCF")
    # hill
    hy = 205 - 26 * np.exp(-((X - 95) / 45) ** 2)
    hm = YY >= hy[None, :]
    dgrad(a, 170, 240, ["#A6D69A", "#86C37E", "#6BAE6C", "#57985E"], mask=hm)
    # tree trunk
    tx = 92
    for y in range(140, 185):
        off = int(3 * np.sin((y - 140) / 9))
        w = 3 + (y - 140) // 14
        a[y, tx + off - w // 2:tx + off + w // 2 + 1] = hx("#5A3A3A")
    for (x0, y0, x1, y1) in [(92, 150, 70, 128), (94, 146, 116, 126), (91, 160, 66, 150), (95, 158, 118, 148)]:
        for k in range(30):
            u = k / 29; xx = int(x0 + (x1 - x0) * u); yy = int(y0 + (y1 - y0) * u)
            a[yy:yy + 2, xx:xx + 2] = hx("#5A3A3A")
    r = np.random.default_rng(5)
    for _ in range(70):
        cx, cy = r.normal(92, 22), r.normal(128, 13)
        rr = r.uniform(3, 7)
        c = r.choice(["#F7A1BF", "#FFC4D8", "#E8759E", "#FFD9E6"])
        m = ((XX - cx) ** 2 + (YY - cy) ** 2 < rr * rr) & (BAY < 0.85)
        a[m] = hx(c)
    for _ in range(45):
        x, y = r.integers(0, GW), r.integers(110, 236)
        a[y, x] = hx(r.choice(["#FFC4D8", "#F7A1BF"]))
    return a

def ocean():
    a = canvas()
    dgrad(a, 0, 240, ["#5ED6E2", "#3BB8D6", "#2697C4", "#1A78AE", "#125B92", "#0C4276", "#082E5A", "#051E40"])
    # light rays
    for k, x0 in enumerate([20, 48, 70, 96, 118]):
        m = (np.abs((XX - x0) - (YY * 0.28)) < 3 + YY * 0.03) & (YY < 170)
        fade = np.clip(1 - YY / 170, 0, 1)
        m &= BAY < fade * 0.55
        a[m] = a[m] * 0.75 + hx("#BFF6FF") * 0.25
    r = np.random.default_rng(9)
    # fish school
    for _ in range(22):
        fx, fy = r.normal(40, 14), r.normal(95, 9)
        fx, fy = int(fx), int(fy)
        c = hx("#0E3A63")
        a[fy, fx:fx + 4] = c; a[fy - 1, fx + 1:fx + 3] = c; a[fy + 1, fx + 1:fx + 3] = c
        a[fy - 1, fx + 4] = c; a[fy + 1, fx + 4] = c
    # jellyfish
    jx, jy = 96, 70
    jm = ((XX - jx) ** 2 / 100 + (YY - jy) ** 2 / 64 <= 1) & (YY <= jy)
    a[jm] = hx("#F59AD0"); a[jm & (YY < jy - 4)] = hx("#FFC6E6")
    for t_ in range(-8, 9, 3):
        for k in range(18):
            xx = jx + t_ + int(1.5 * np.sin(k / 3 + t_)); yy = jy + 1 + k
            if 0 <= xx < GW: a[yy, xx] = a[yy, xx] * 0.4 + hx("#F59AD0") * 0.6
    # bubbles
    for _ in range(20):
        bx, by, br = r.integers(5, GW - 5), r.integers(20, 200), r.integers(1, 3)
        m = np.abs(np.hypot(XX - bx, YY - by) - br) < 0.6
        a[m] = a[m] * 0.4 + hx("#DFFBFF") * 0.6
    # seabed
    sb = 214 + 4 * np.sin(X / 9) + 2 * np.sin(X / 3.3)
    sm = YY >= sb[None, :]
    dgrad(a, 205, 240, ["#C9B27A", "#AE9462", "#8C744C"], mask=sm)
    # seaweed + coral
    for sx in [8, 15, 52, 120, 127]:
        for k in range(r.integers(20, 40)):
            yy = 216 - k; xx = sx + int(2 * np.sin(k / 4 + sx))
            a[yy, xx:xx + 2] = hx("#2E9A5A") if k % 3 else hx("#4FC27A")
    for cx_, col in [(34, "#FF7A6B"), (78, "#FF9AC0"), (100, "#FFB45A")]:
        for k in range(14):
            a[214 - k, cx_] = hx(col)
            if k in (5, 9): a[214 - k, cx_ - 3:cx_ + 4] = hx(col)
            if k in (7, 11): a[214 - k - 2:214 - k, cx_ - 3] = hx(col); a[214 - k - 2:214 - k, cx_ + 3] = hx(col)
    return a

WALLS = [("Aurora", aurora), ("Sunset", sunset), ("Neon rain", neon), ("Lighthouse", lighthouse),
         ("Desert moon", desert), ("Ringed planet", space), ("Blossom dawn", blossom), ("Deep blue", ocean)]
def render_all():
    from PIL import Image
    out = []
    for i, (n, f) in enumerate(WALLS):
        a = f().clip(0, 255).astype(np.uint8)
        im = Image.fromarray(np.kron(a, np.ones((S, S, 1), np.uint8)))
        im.save(f"wall_{i+1}.png"); out.append(im)
    return out
if __name__ == "__main__":
    from PIL import Image
    ims = render_all()
    st = Image.new("RGB", (270 * 8, 480))
    for k, im in enumerate(ims): st.paste(im.resize((270, 480), Image.NEAREST), (k * 270, 0))
    st.save("walls_preview.png")
