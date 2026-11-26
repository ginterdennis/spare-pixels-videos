"""pick round 3's seed: the peacock's blue centre (half-res disc at (190, 215), r 80) should stay mostly covered
until ~5 s of the 6.6 s round, while >45 % of the picture is open by 6.3 s."""
import numpy as np
from sim import simulate, HB
yy, xx = np.mgrid[0:HB, 0:HB]
centre = (xx - 190) ** 2 + (yy - 215) ** 2 < 80 ** 2
res = []
for cfg in [dict(v0=400, p_spawn=0.45, cap=12, n0=1), dict(v0=380, p_spawn=0.4, cap=11, low_start=True)]:
    for seed in range(1, 120):
        fr, rev, hits, born = simulate(seed=seed, T=6.6, **cfg)
        c5 = np.mean(rev[centre] <= 5.0); c4 = np.mean(rev[centre] <= 4.0)
        tot = np.mean(rev <= 6.3)
        res.append((c5, c4, tot, seed, cfg))
res = [r for r in res if r[2] > 0.45]
res.sort(key=lambda r: r[0])
for r in res[:6]:
    print(f"centre@5 {r[0]:.3f} centre@4 {r[1]:.3f} tot@6.3 {r[2]:.2f} seed {r[3]} {r[4]}")
