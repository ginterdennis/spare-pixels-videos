import numpy as np, sys
from sim import simulate, HB
# crown region (half-res coords): x 100..280, y 0..125 ; body region y > 125
yy, xx = np.mgrid[0:HB, 0:HB]
crown = (xx > 100) & (xx < 280) & (yy < 125)
res = []
for cfg in [dict(v0=380, p_spawn=0.35, cap=10, low_start=True), dict(v0=400, p_spawn=0.45, cap=12, low_start=True)]:
    for seed in range(1, 120):
        fr, rev, hits, born = simulate(seed=seed, T=6.3, **cfg)
        c5 = np.mean(rev[crown] <= 5.0); c4 = np.mean(rev[crown] <= 4.0)
        tot = np.mean(rev <= 6.3); t3 = np.mean(rev <= 3.0)
        res.append((c5, c4, tot, t3, seed, cfg))
res = [r for r in res if r[2] > 0.45]
res.sort(key=lambda r: r[0])
for r in res[:8]:
    print(f"crown@5 {r[0]:.2f} crown@4 {r[1]:.2f} tot@6.3 {r[2]:.2f} tot@3 {r[3]:.2f} seed {r[4]} {r[5]}")
