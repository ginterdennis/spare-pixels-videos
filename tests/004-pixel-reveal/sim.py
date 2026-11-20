import numpy as np
N = 24; CELL = 36; BOX = N * CELL
def simulate(seed=7, v0=560, p_spawn=0.55, cap=34, r=16, rrev=30, fps=30, sub=4, T=21.0, start=0.4):
    rng = np.random.default_rng(seed)
    balls = [[BOX * 0.5, BOX * 0.18, *(v0 * np.array([np.cos(1.1), np.sin(1.1)]))]]
    born = [start]
    rev = np.full((N, N), np.inf)
    hits = []  # (t, x, y, ball_index)
    frames = []
    dt = 1 / fps / sub
    t = 0.0
    cy, cx = np.mgrid[0:N, 0:N]
    ccx = (cx + 0.5) * CELL; ccy = (cy + 0.5) * CELL
    nf = int(T * fps)
    for f in range(nf):
        for s in range(sub):
            t += dt
            if t < start: continue
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
                        # aim back into the box
                        if b[0] <= r + 1: nb[2] = abs(nb[2])
                        if b[0] >= BOX - r - 1: nb[2] = -abs(nb[2])
                        if b[1] <= r + 1: nb[3] = abs(nb[3])
                        if b[1] >= BOX - r - 1: nb[3] = -abs(nb[3])
                        new.append(nb)
                d2 = (ccx - b[0]) ** 2 + (ccy - b[1]) ** 2
                m = (d2 < rrev ** 2) & np.isinf(rev)
                rev[m] = t
            for nb in new:
                balls.append(nb); born.append(t)
        frames.append([(b[0], b[1]) for b in balls])
    return frames, rev, hits, born
if __name__ == "__main__":
    import sys
    for seed in range(1, 13):
        fr, rev, hits, born = simulate(seed=seed)
        cov = lambda T: np.mean(rev <= T) * 100
        print(seed, " ".join(f"{T}s:{cov(T):4.0f}%" for T in (4, 6, 8, 10, 12, 14, 16, 18, 20)), "balls", len(fr[-1]), "hits", len(hits))
