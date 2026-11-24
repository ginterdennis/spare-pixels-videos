import numpy as np
from sim import simulate, HB
# watermelon rind band (half-res coords): y < 108 (full res < 216), full width
yy, xx = np.mgrid[0:HB, 0:HB]
rind = yy < 108
res = []
for cfg in [dict(v0=400, p_spawn=0.45, cap=12, low_start=True), dict(v0=380, p_spawn=0.4, cap=11, low_start=True)]:
    for seed in range(1, 140):
        fr, rev, hits, born = simulate(seed=seed, T=6.6, **cfg)
        c5 = np.mean(rev[rind] <= 5.2); c4 = np.mean(rev[rind] <= 4.0)
        tot = np.mean(rev <= 6.3)
        res.append((c5, c4, tot, seed, cfg))
res = [r for r in res if r[2] > 0.45]
res.sort(key=lambda r: r[0])
for r in res[:6]:
    print(f"rind@5.2 {r[0]:.3f} rind@4 {r[1]:.3f} tot@6.3 {r[2]:.2f} seed {r[3]} {r[4]}")
