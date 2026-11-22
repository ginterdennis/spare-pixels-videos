"""Bouncing-ball reveal (smooth scratch-off, no grid). Balls split on wall hits; every point a ball
passes over is uncovered. REV = time each half-res pixel was first touched (inf = never)."""
import numpy as np
BOX = 760
HB = BOX // 2           # reveal map at half resolution, upscaled bilinear -> soft round edges


def simulate(seed=7, T=8.0, v0=420, p_spawn=0.5, cap=16, r=15, rrev=44, fps=30, sub=4, n0=1, start=0.0, low_start=False):
    rng = np.random.default_rng(seed)
    balls = []
    if low_start:   # start low in the box at a seeded angle (keeps the top of the picture hidden longer)
        a = rng.uniform(0, 2 * np.pi)
        balls.append([rng.uniform(0.3, 0.7) * BOX, rng.uniform(0.7, 0.85) * BOX, v0 * np.cos(a), v0 * np.sin(a)])
        n0 = 0
    for k in range(n0):
        a = 1.1 + k * 2.1
        balls.append([BOX * (0.5 + 0.2 * np.cos(k * 2.4)), BOX * (0.3 + 0.15 * k % 0.5), v0 * np.cos(a), v0 * np.sin(a)])
    born = [start] * len(balls)
    rev = np.full((HB, HB), np.inf)
    hits = []
    frames = []
    dt = 1 / fps / sub
    t = 0.0
    rr = rrev / 2
    yy, xx = np.mgrid[0:HB, 0:HB]
    for f in range(int(T * fps)):
        for s in range(sub):
            t += dt
            if t < start:
                continue
            new = []
            for i, b in enumerate(balls):
                b[0] += b[2] * dt; b[1] += b[3] * dt
                hit = False
                if b[0] < r: b[0] = 2 * r - b[0]; b[2] = abs(b[2]); hit = True
                if b[0] > BOX - r: b[0] = 2 * (BOX - r) - b[0]; b[2] = -abs(b[2]); hit = True
                if b[1] < r: b[1] = 2 * r - b[1]; b[3] = abs(b[3]); hit = True
                if b[1] > BOX - r: b[1] = 2 * (BOX - r) - b[1]; b[3] = -abs(b[3]); hit = True
                if hit:
                    hits.append((t, b[0], b[1], i))
                    if len(balls) + len(new) < cap and rng.random() < p_spawn:
                        ang = rng.uniform(0, 2 * np.pi)
                        sp = np.hypot(b[2], b[3]) * rng.uniform(0.92, 1.08)
                        nb = [b[0], b[1], sp * np.cos(ang), sp * np.sin(ang)]
                        if b[0] <= r + 1: nb[2] = abs(nb[2])
                        if b[0] >= BOX - r - 1: nb[2] = -abs(nb[2])
                        if b[1] <= r + 1: nb[3] = abs(nb[3])
                        if b[1] >= BOX - r - 1: nb[3] = -abs(nb[3])
                        new.append(nb)
                cx, cy = b[0] / 2, b[1] / 2
                x0, x1 = max(0, int(cx - rr - 1)), min(HB, int(cx + rr + 2))
                y0, y1 = max(0, int(cy - rr - 1)), min(HB, int(cy + rr + 2))
                sl = rev[y0:y1, x0:x1]
                m = ((xx[y0:y1, x0:x1] + 0.5 - cx) ** 2 + (yy[y0:y1, x0:x1] + 0.5 - cy) ** 2 < rr * rr) & np.isinf(sl)
                sl[m] = t
            for nb in new:
                balls.append(nb); born.append(t)
        frames.append([(b[0], b[1]) for b in balls])
    return frames, rev, hits, born


if __name__ == "__main__":
    import sys
    cfg = dict(v0=float(sys.argv[1]), p_spawn=float(sys.argv[2]), cap=int(sys.argv[3]), n0=int(sys.argv[4]), T=float(sys.argv[5]))
    for seed in range(1, 11):
        fr, rev, hits, born = simulate(seed=seed, **cfg)
        cov = lambda T: np.mean(rev <= T) * 100
        print(seed, " ".join(f"{T:.0f}s:{cov(T):3.0f}%" for T in np.arange(1, cfg['T'] + 0.01, 1)), "balls", len(fr[-1]))
