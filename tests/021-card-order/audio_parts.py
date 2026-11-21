"""Shared sound parts for 021 (v1's riffle, importable without running v1's score)."""
import sys
sys.path.insert(0, "/home/claude/kit")
import numpy as np
from scipy import signal
from kit import SR, sos


def riffle(d=0.5, seed=0):
    """card riffle: a burst of tiny filtered clicks that speeds up."""
    rg = np.random.default_rng(seed)
    out = np.zeros(int((d + 0.05) * SR))
    tt_ = 0.0
    while tt_ < d:
        c = signal.sosfilt(sos("bandpass", [1800, 7000]), rg.standard_normal(int(0.008 * SR))) * np.exp(-np.arange(int(0.008 * SR)) / (0.0015 * SR))
        i = int(tt_ * SR); out[i:i + len(c)] += c * (0.6 + 0.4 * rg.random())
        tt_ += 0.012 + 0.02 * (1 - tt_ / d) * rg.random()
    return out
