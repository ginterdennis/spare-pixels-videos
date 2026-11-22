"""027 "The pixel that fell out": every motion in the video as a pure function of time.

No bpy in here: the Blender build (blender/build.py) execs this file and bakes `bake()` into
per-frame keyframes, and the cloud side imports it for timing.json, checks and plots.
Units: metres, seconds. Blender axes: z up, the screen faces -y (the camera sits at negative y).
"""
import math

FPS = 30
END = 24.0
N = int(END * FPS)

# ---------------------------------------------------------------- layout
COLS, ROWS = 18, 24
P = 0.025                    # tile pitch
S = 0.0225                   # tile (and hero) size: a cube
HALF = S / 2
Z0 = 0.06                    # bottom edge of the tile screen
G = 3.0                      # toy gravity (real 9.81 makes a 2 cm hero look like a flea)
TILE_FRONT = -HALF           # front faces of the tiles (y)
BEZEL_FRONT = -0.016


def tile_xyz(r, c):
    return ((c - 8.5) * P, 0.0, Z0 + (23.5 - r) * P)


HOLE_RC = (8, 5)
HOLE = tile_xyz(*HOLE_RC)                        # (-0.0875, 0, 0.4475)
PAW_RC = [(r, c) for r in (20, 21, 22) for c in (4, 5, 6)]
PAW_C = tile_xyz(21, 5)                          # paw centre (-0.0875, 0, 0.1225)
NOSE_RC = (12, 8.5)

H0 = (-0.060, -0.130, 0.0)                       # where he sits after falling out (ground point)
PAD = dict(c=(-0.130, -0.200), size=(0.076, 0.076), h=0.012)
BOOKS = dict(c=(-0.300, -0.130), h=0.047)
MUG = dict(c=(-0.170, -0.100), r=0.040, h=0.095)
RIM = (MUG["c"][0] - 0.035, MUG["c"][1], MUG["h"])  # landing point on the rim (books side)
SPLAT_Z = 0.33
H1 = (HOLE[0], -0.125, 0.0)                      # where he lands after sliding down the screen
PALM_DESK = (HOLE[0], -0.0585, 0.010)            # paw group centre when the palm lies on the desk
PALM_TOP = PALM_DESK[2] + HALF                   # palm surface height on the desk


# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):                       # smoothstep-ish cubic in-out
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_io(u, p=3):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** p / 2


def ease_out(u, p=3):
    u = clamp(u)
    return 1 - (1 - u) ** p


def ease_in(u, p=2):
    return clamp(u) ** p


def back_out(u, s=1.7):            # overshoot
    u = clamp(u) - 1
    return 1 + u * u * ((s + 1) * u + s)


def lerp(a, b, u):
    return a + (b - a) * u


def lerp3(a, b, u):
    return tuple(lerp(a[i], b[i], u) for i in range(3))


def heading_to(p0, p1):
    """heading so the hero's front (-y local) faces from p0 towards p1 (xy)"""
    return math.atan2(p1[0] - p0[0], -(p1[1] - p0[1]))


def ang_lerp(a, b, u):
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + d * u


def ang_near(a, ref):
    """a shifted by 2pi*k to be as close as possible to ref (keeps euler curves continuous)"""
    return a + 2 * math.pi * round((ref - a) / (2 * math.pi))


# ---------------------------------------------------------------- hero timeline
class Pose:
    __slots__ = ("loc", "rot", "scl", "look", "lid", "eye", "glow", "insl")

    def __init__(self, loc, h=0.0, tilt=(0.0, 0.0), sq=1.0, sqax="z", look=(0, 0), lid=1.0, eye=1.0,
                 glow=1.0, insl=False):
        self.loc = loc
        self.rot = (tilt[0], tilt[1], h)
        if sqax == "z":
            self.scl = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
        else:                       # squash along the facing axis (splat on the screen)
            self.scl = (1 / math.sqrt(sq), sq, 1 / math.sqrt(sq))
        self.look, self.lid, self.eye, self.glow, self.insl = look, lid, eye, glow, insl


SEG = []                            # (t0, t1, fn(t) -> Pose)
EV = {}                             # named event times -> timing.json


def seg(t0, t1, fn):
    SEG.append((t0, t1, fn))
    return t1


def on_ground(g, sq=1.0):
    return (g[0], g[1], g[2] + S * sq / 2)


def sit(t0, t1, g, h, look=(0, 0), lid=1.0, breathe=True, slump=0.0):
    def f(t):
        sq = 1 + (0.025 * math.sin(2 * math.pi * (t - t0) / 1.3) if breathe else 0) - slump
        return Pose(on_ground(g, sq), h, (slump * 0.8, 0), sq, look=look, lid=lid)
    return seg(t0, t1, f)


def turn(t0, t1, g, h0, h1, look=(0, 0), lid=1.0, lift=0.004):
    def f(t):
        u = (t - t0) / (t1 - t0)
        loc = on_ground(g)
        loc = (loc[0], loc[1], loc[2] + lift * math.sin(math.pi * clamp(u)))
        return Pose(loc, ang_lerp(h0, h1, ease_io(u)), look=look, lid=lid)
    return seg(t0, t1, f)


def hop(t0, g0, g1, apex_extra, h0=None, h1=None, antic=0.10, land=0.20, look=(0, 0.6), spin=(0.0, 0.0),
        antic_sq=0.70, name=None):
    """antic squash on g0, ballistic flight to g1 (apex = higher end + apex_extra), landing squash.
    Returns the end time. Heading turns from h0 to h1 during the flight."""
    z0, z1 = g0[2] + HALF, g1[2] + HALF
    apex = max(z0, z1) + apex_extra
    tu, td = math.sqrt(2 * (apex - z0) / G), math.sqrt(2 * (apex - z1) / G)
    T = tu + td
    vz = G * tu
    h0 = heading_to(g0, g1) if h0 is None else h0
    h1 = h0 if h1 is None else h1
    tk, tl = t0 + antic, t0 + antic + T
    if name:
        EV[name + "_takeoff"], EV[name + "_land"] = tk, tl

    def fa(t):                                     # anticipation
        u = (t - t0) / antic
        sq = 1 - (1 - antic_sq) * ease_out(u, 2)
        return Pose(on_ground(g0, sq), h0, sq=sq, look=look)

    def ff(t):                                     # flight
        tau = t - tk
        x = lerp(g0[0], g1[0], tau / T)
        y = lerp(g0[1], g1[1], tau / T)
        z = z0 + vz * tau - 0.5 * G * tau * tau
        st = 1 + 0.28 * math.exp(-tau / 0.06) - 0.10 * math.exp(-(T - tau) / 0.04)
        u = tau / T
        return Pose((x, y, z), ang_lerp(h0, h1, ease_io(min(1, u * 1.4))),
                    (spin[0] * ease_io(u), spin[1] * ease_io(u)), st, look=look)

    def fl(t):                                     # landing squash, damped
        tau = t - tl
        sq = 1 - 0.32 * math.exp(-tau * 11) * math.cos(2 * math.pi * tau * 4.2)
        return Pose(on_ground(g1, sq), h1, sq=sq, look=look)

    seg(t0, tk, fa)
    seg(tk, tl, ff)
    return seg(tl, tl + land, fl)


def build_hero():
    SEG.clear(); EV.clear()
    H_CAM, H_SCR = 0.0, math.pi
    t = 0.0
    # --- falls out (off screen until the reveal), looking up at the hole
    t = sit(t, 3.10, H0, H_CAM, look=(0, 1))
    EV["reveal"] = 3.0
    t = hop(t, H0, H0, 0.010, H_CAM, H_CAM, antic=0.06, land=0.14, look=(0, 0), antic_sq=0.85)  # "hi" hop
    t = turn(t, t + 0.24, H0, H_CAM, H_SCR, look=(0, 1))
    EV["turned"] = t
    EV["try1"] = 5.30                               # after "Now he wants back in." (voice A)
    t = sit(t, EV["try1"] + 0.30, H0, H_SCR, look=(0, 1))
    # --- TRY 1: straight up, way too short
    t = hop(t, H0, H0, 0.095, H_SCR, H_SCR, antic=0.16, land=0.10, antic_sq=0.62, name="j1")
    t = hop(t, H0, H0, 0.016, H_SCR, H_SCR, antic=0.01, land=0.18, antic_sq=0.95)          # bounce
    EV["nope"] = EV["j1_land"]
    t_d0 = t

    def dizzy(tt):
        u = tt - t_d0
        a = 0.30 * math.exp(-u * 3.0)
        return Pose(on_ground(H0, 0.92), H_SCR + 0.25 * math.sin(u * 9) * math.exp(-u * 2),
                    (a * math.sin(u * 13), a * math.cos(u * 13)), 0.92, lid=0.45)
    t = seg(t, t + 0.62, dizzy)
    EV["try2"] = round((t + 0.12) * FPS) / FPS
    t = sit(t, EV["try2"], H0, H_SCR, lid=0.8)
    # --- TRY 2: platform hops to the mug, big leap, splat on the screen
    gpad = (PAD["c"][0], PAD["c"][1], PAD["h"])
    gbook = (BOOKS["c"][0] + 0.010, BOOKS["c"][1] - 0.010, BOOKS["h"])
    h1 = heading_to(H0, gpad)
    t = turn(t, t + 0.12, H0, H_SCR, h1, look=(0, 0.5))
    t = hop(t, H0, gpad, 0.032, h1, h1, name="p1", land=0.14)
    h2 = heading_to(gpad, gbook)
    t = turn(t, t + 0.10, gpad, h1, h2)
    t = hop(t, gpad, gbook, 0.032, h2, h2, name="p2", land=0.14)
    h3 = heading_to(gbook, RIM)
    t = turn(t, t + 0.10, gbook, h2, h3)
    t = hop(t, gbook, RIM, 0.032, h3, h3, name="p3", land=0.06)
    t_r0 = t

    def teeter(tt):                                 # balancing on the thin rim
        u = tt - t_r0
        a = 0.42 * math.exp(-u * 4.0)
        return Pose(on_ground(RIM), h3, (a * math.sin(u * 16), 0.15 * a * math.sin(u * 11)),
                    look=(0.8 * math.sin(u * 16), 0))
    t = seg(t, t + 0.45, teeter)
    EV["teeter"] = t_r0
    hit = (HOLE[0], TILE_FRONT - HALF, SPLAT_Z - HALF)          # ground-point form: z = centre - HALF
    h4 = heading_to(RIM, hit)
    t = turn(t, t + 0.10, RIM, h3, h4, look=(0, 1))
    # the leap (flight only; the splat takes over at the screen)
    Lz0, Lz1, Lapex = RIM[2] + HALF, SPLAT_Z, 0.36
    LT = math.sqrt(2 * (Lapex - Lz0) / G) + math.sqrt(2 * (Lapex - Lz1) / G)
    Lvz = G * math.sqrt(2 * (Lapex - Lz0) / G)
    La = t; Lk = t + 0.20; Ll = Lk + LT
    EV["leap"], EV["splat"] = Lk, Ll

    def leap_antic(tt):
        sq = 1 - 0.42 * ease_out((tt - La) / 0.20, 2)
        return Pose(on_ground(RIM, sq), h4, sq=sq, look=(0, 1))

    def leap_fly(tt):
        tau = tt - Lk
        u = tau / LT
        x = lerp(RIM[0], hit[0], u); y = lerp(RIM[1], hit[1], u)
        z = Lz0 + Lvz * tau - 0.5 * G * tau * tau
        st = 1 + 0.35 * math.exp(-tau / 0.07)
        return Pose((x, y, z), ang_lerp(h4, H_SCR, ease_io(u)), (-0.5 * math.sin(math.pi * u), 0), st,
                    look=(0, 1))
    seg(La, Lk, leap_antic); t = seg(Lk, Ll, leap_fly)

    def stuck(tt):
        tau = tt - Ll
        sq = 0.40 + 0.10 * math.exp(-tau * 9) * math.cos(2 * math.pi * tau * 6)
        return Pose((hit[0], TILE_FRONT - S * sq / 2, SPLAT_Z), H_SCR, sq=sq, sqax="y")
    t = seg(t, t + 0.32, stuck)
    Ts = t
    SL = 0.45
    a_sl = 2 * (SPLAT_Z - (Z0 + HALF + 0.002)) / SL ** 2

    def slide(tt):
        tau = tt - Ts
        sq = lerp(0.40, 0.72, ease_io(tau / SL))
        z = SPLAT_Z - 0.5 * a_sl * tau * tau
        return Pose((hit[0], TILE_FRONT - S * sq / 2, z), H_SCR, sq=sq, sqax="y")
    t = seg(t, t + SL, slide)
    EV["slid"] = t
    Tp0 = t; zst = Z0 + HALF + 0.002; yst = TILE_FRONT - S * 0.72 / 2
    vzp = 0.30
    Tp = (vzp + math.sqrt(vzp ** 2 + 2 * G * (zst - HALF))) / G

    def pop(tt):                                    # falls off the bezel, tumbles backwards to H1
        tau = tt - Tp0
        u = tau / Tp
        z = zst + vzp * tau - 0.5 * G * tau * tau
        return Pose((H1[0], lerp(yst, H1[1], u), z), H_SCR, (-2 * math.pi * ease_io(u), 0),
                    lerp(0.85, 1.0, u))
    t = seg(t, t + Tp, pop)
    EV["flop"] = t
    Tf = t

    def flop(tt):
        tau = tt - Tf
        sq = 1 - 0.38 * math.exp(-tau * 10) * math.cos(2 * math.pi * tau * 4)
        return Pose(on_ground(H1, sq), H_SCR, (-2 * math.pi, 0), sq=sq, lid=0.5)
    t = seg(t, t + 0.22, flop)

    def slump(tt):
        return Pose(on_ground(H1, 0.9), H_SCR, (-2 * math.pi + 0.10, 0), 0.9, lid=0.5)
    t = seg(t, t + 0.12, slump)
    # --- TRY 3: the cat's paw
    EV["try3"] = round(t * FPS) / FPS
    t = turn(t, t + 0.26, H1, H_SCR, 2 * math.pi, look=(0, -1), lid=0.55)     # faces us, sad
    EV["paw_pop"] = EV["try3"] + 0.68                # tiles pop behind him once "Try three." is said
    EV["paw_out"] = EV["paw_pop"] + 0.34
    EV["paw_land"] = EV["paw_out"] + 0.62
    t = sit(t, EV["paw_land"] + 0.05, H1, 2 * math.pi, look=(0, -1), lid=0.5, slump=0.06)
    # notices: eyes wide, hop-turn to face the paw
    t = turn(t, t + 0.10, H1, 2 * math.pi, 2 * math.pi, look=(0, 0.3), lid=1.0, lift=0.008)
    t = turn(t, t + 0.18, H1, 2 * math.pi, 3 * math.pi, look=(0, 0), lid=1.0)
    palm_g = (PALM_DESK[0], PALM_DESK[1], PALM_TOP)
    t = hop(t, H1, palm_g, 0.03, 3 * math.pi, 3 * math.pi, name="onpaw", land=0.14)
    EV["lift"] = t + 0.06
    EV["lift_end"] = EV["lift"] + 0.95

    def ride(tt):
        pg = paw_group_lift(tt)
        loc = (pg[0][0], pg[0][1], pg[0][2] + HALF + HALF)
        u = (tt - EV["lift"]) / (EV["lift_end"] - EV["lift"])
        w = 0.10 * math.sin(math.pi * clamp(u)) * math.sin(tt * 14)
        return Pose(loc, 3 * math.pi, (w, 0), look=(0, 1))
    t = seg(t, EV["lift_end"] + 0.06, ride)
    top = (PALM_DESK[0], PALM_DESK[1], HOLE[2] - HALF)      # palm surface at the top
    t = turn(t, t + 0.20, top, 3 * math.pi, 4 * math.pi, look=(0, 0))
    t = sit(t, t + 0.22, top, 4 * math.pi, look=(0, 0))
    EV["wink"] = t - 0.16
    # hop backwards into the slot
    Ia = t; Ik = t + 0.08; IT = 0.28; Il = Ik + IT
    EV["hopin"], EV["click"] = Ik, Il

    def in_antic(tt):
        sq = 1 - 0.25 * ease_out((tt - Ia) / 0.08, 2)
        return Pose(on_ground(top, sq), 4 * math.pi, sq=sq)

    def in_fly(tt):
        u = (tt - Ik) / IT
        y = lerp(top[1], HOLE[1], ease_in(u, 1.4))
        z = HOLE[2] + 0.028 * math.sin(math.pi * min(1, u / 0.8)) if u < 0.8 else HOLE[2]
        return Pose((HOLE[0], y, z), 4 * math.pi, (0.25 * math.sin(math.pi * u), 0), 1.08)
    seg(Ia, Ik, in_antic); t = seg(Ik, Il, in_fly)
    # --- home: in the slot. Eyes blink, then he becomes just a pixel again
    EV["eyes_off"] = EV["click"] + 0.75
    EV["happy"] = EV["click"] + 0.90
    EV["wide"] = EV["click"] + 1.70
    EV["sad_look"] = EV["wide"] + 0.05
    EV["squeeze"] = EV["wide"] + 0.45
    EV["achoo"] = EV["squeeze"] + 0.65
    wave_hit = EV["achoo"] + math.hypot(HOLE_RC[0] - NOSE_RC[0], HOLE_RC[1] - NOSE_RC[1]) / WAVE_V
    EV["eject"] = wave_hit

    def slot(tt):
        tau = tt - EV["click"]
        push_ = 0.006 * math.exp(-tau * 14) * math.cos(tau * 40)
        e = 1.0 - ease((tt - EV["eyes_off"]) / 0.15)
        return Pose((HOLE[0], HOLE[1] + push_ + ripple_y(tt, *HOLE_RC), HOLE[2]), 4 * math.pi,
                    lid=1.0 if not (0.40 < tau < 0.52) else 0.1, eye=e, glow=0.0, insl=True)
    t = seg(t, wave_hit, slot)
    # --- ejected by the sneeze: up, spinning, lands back on H0 (the loop starts there)
    vz_e = 0.60
    zf = H0[2] + HALF
    Te = (vz_e + math.sqrt(vz_e ** 2 + 2 * G * (HOLE[2] - zf))) / G
    EV["eject_land"] = wave_hit + Te

    def eject(tt):
        tau = tt - wave_hit
        u = tau / Te
        z = HOLE[2] + vz_e * tau - 0.5 * G * tau * tau
        x = lerp(HOLE[0], H0[0], u); y = lerp(HOLE[1] - 0.004, H0[1], u)
        return Pose((x, y, z), lerp(4 * math.pi, 6 * math.pi, ease_io(u)),
                    (-3 * math.pi * ease_out(u, 2), 0.6 * math.sin(math.pi * u)), 1.0 + 0.15 * math.exp(-tau / 0.08),
                    eye=1.35, look=(0, 0))
    t = seg(t, EV["eject_land"], eject)
    Tl = t

    def land_end(tt):
        tau = tt - Tl
        sq = 1 - 0.35 * math.exp(-tau * 10) * math.cos(2 * math.pi * tau * 4)
        return Pose(on_ground(H0, sq), 6 * math.pi, (-3 * math.pi, 0), sq=sq, eye=1.2, look=(0, 1))
    t = seg(t, t + 0.4, land_end)
    t = sit(t, END + 0.5, H0, 6 * math.pi, look=(0, 1))   # loop: same as frame 0 (heading 0 mod 2pi)
    EV["cta"] = EV["eject"] + 0.80
    return t


def hero(t):
    for (t0, t1, f) in SEG:
        if t0 <= t < t1:
            return f(t)
    return SEG[-1][2](t)


def blinks():
    """times the hero blinks (both eyes); the wink before he hops into the slot is separate (EV["wink"])"""
    e = EV
    return [e["reveal"] + 0.14, e["turned"] + 0.75, e["try1"] + 0.12, e["try2"] + 0.05, e["teeter"] + 0.55,
            e["try3"] + 0.45, e["lift"] + 0.45, e["click"] + 0.42]


# ---------------------------------------------------------------- the cat's paw (9 tiles)
def paw_group(t):
    """(centre location, rot_x) of the paw group. rot_x=-pi/2: palm up (tile fronts face +z)."""
    rest, desk = PAW_C, PALM_DESK
    top = (PALM_DESK[0], PALM_DESK[1], HOLE[2] - HALF - HALF)
    if t < EV["paw_out"]:
        return rest, 0.0
    if t < EV["paw_land"]:
        u = (t - EV["paw_out"]) / (EV["paw_land"] - EV["paw_out"])
        # out of the screen first, then swing down and round into a flat palm
        k = ease_io(u)
        out = (rest[0], -0.075, rest[2] + 0.02)
        a = lerp3(rest, out, ease_out(min(1, u / 0.45), 2))
        b = lerp3(out, desk, ease_io((u - 0.35) / 0.65))
        loc = a if u < 0.35 else b
        bounce = 0.004 * math.sin(math.pi * clamp((u - 0.9) / 0.1))
        return (loc[0], loc[1], loc[2] + bounce), -math.pi / 2 * k
    if t < EV["lift"]:
        return desk, -math.pi / 2
    if t < EV["click"]:
        u = (t - EV["lift"]) / (EV["lift_end"] - EV["lift"])
        loc = lerp3(desk, top, ease_io(u))
        return loc, -math.pi / 2
    back = EV["click"] + 0.15
    if t < back:
        return top, -math.pi / 2
    u = (t - back) / 0.85
    if u >= 1:
        return rest, 0.0
    k = ease_io(u)
    mid = (rest[0], -0.07, (top[2] + rest[2]) / 2)
    loc = lerp3(top, mid, ease_io(u / 0.5)) if u < 0.5 else lerp3(mid, rest, ease_io((u - 0.5) / 0.5))
    return loc, -math.pi / 2 * (1 - k)


def paw_group_lift(t):
    top = (PALM_DESK[0], PALM_DESK[1], HOLE[2] - HALF - HALF)
    u = (t - EV["lift"]) / (EV["lift_end"] - EV["lift"])
    return lerp3(PALM_DESK, top, ease_io(u)), -math.pi / 2


def paw_pop(t, k):
    """y offset (towards the camera, negative) of paw tile k (0..8) inside the group."""
    t_out = EV["paw_pop"] + 0.035 * k
    t_in = EV["click"] + 0.15 + 0.85 + 0.03 * k
    if t < t_out:
        return 0.0
    if t < t_in:
        return -0.010 * back_out((t - t_out) / 0.12, 2.2)
    return -0.010 * (1 - ease_out((t - t_in) / 0.12))


# ---------------------------------------------------------------- tile wall offsets (y, +y = into the screen)
WAVE_V = 30.0          # tiles per second


def ripple_y(t, r, c):
    y = 0.0
    # splat: the tiles round the impact dent in and wobble
    tau = t - EV["splat"]
    if 0 <= tau < 0.6:
        rr, cc = 23.5 - (SPLAT_Z - Z0) / P, HOLE_RC[1]
        d = math.hypot(r - rr, c - cc)
        if d < 4.5:
            y += 0.0045 * math.exp(-d * d / 4.0) * math.exp(-tau * 7) * math.cos(tau * 30)
    # "ah... ah...": the whole wall breathes in twice before the sneeze
    tau = t - EV["squeeze"]
    if 0 <= tau < EV["achoo"] - EV["squeeze"]:
        u = tau / (EV["achoo"] - EV["squeeze"])
        y += 0.0035 * math.sin(math.pi * clamp(u * 2.2)) * (1 if u < 0.46 else 0) \
            + 0.0055 * math.sin(math.pi * clamp((u - 0.5) * 2.0)) * (1 if u >= 0.5 else 0)
    # ACHOO: a ring wave out of the nose pushes every tile towards the camera
    tau = t - EV["achoo"]
    if 0 <= tau < 1.2:
        d = math.hypot(r - NOSE_RC[0], c - NOSE_RC[1])
        front = WAVE_V * tau
        amp = 0.020 * math.exp(-tau * 2.2)
        y += -amp * math.exp(-((d - front) / 1.6) ** 2)
        if d < front:                               # small after-wobble behind the front
            y += -0.004 * math.exp(-tau * 4) * math.sin((front - d) * 1.2)
    return y


def ripple_rot(t, r, c):
    """(rx, rz) tilt of a tile: tiles at a wave front turn their faces away from its centre,
    so the bevel highlights roll across the wall (a pure push towards the camera barely reads head-on)."""
    rx = rz = 0.0
    tau = t - EV["achoo"]
    if 0 <= tau < 1.2:
        dr, dc = r - NOSE_RC[0], c - NOSE_RC[1]
        d = math.hypot(dr, dc) or 1.0
        g = 0.65 * math.exp(-((d - WAVE_V * tau) / 1.6) ** 2) * math.exp(-tau * 2.2)
        rx += g * dr / d; rz += g * dc / d
    tau = t - EV["splat"]
    if 0 <= tau < 0.6:
        rr, cc = 23.5 - (SPLAT_Z - Z0) / P, HOLE_RC[1]
        dr, dc = r - rr, c - cc
        d = math.hypot(dr, dc) or 1.0
        if d < 4.5:
            g = -0.35 * math.exp(-d * d / 4.0) * math.exp(-tau * 7) * math.cos(tau * 30)
            rx += g * dr / d; rz += g * dc / d
    return rx, rz


# ---------------------------------------------------------------- the cat's expression
def cat_state(t):
    e = EV
    keys = [
        (0.00, "look_c"), (0.55, "look_l"), (1.10, "look_r"), (1.65, "look_d"),
        (e["try1"], "look_d"), (e["j1_takeoff"] + 0.10, "look_c"), (e["j1_land"], "look_d"),
        (e["try2"] + 0.25, "look_l"), (e["leap"], "look_c"), (e["splat"], "blink"), (e["splat"] + 0.12, "look_d"),
        (e["paw_pop"] - 0.20, "blink"), (e["paw_pop"] - 0.10, "look_d"),
        (e["lift"] + 0.60, "look_c"), (e["click"], "look_c"),
        (e["happy"], "happy"), (e["sad_look"], "look_c"), (e["squeeze"], "squeeze"),
        (e["eject"] + 0.30, "look_c"),
    ]
    st = "look_c"
    for (k, s) in keys:
        if t >= k:
            st = s
    return st


# ---------------------------------------------------------------- camera
def look_quat(cam, tgt, roll=0.0):
    """quaternion (w,x,y,z) for a Blender camera at cam looking at tgt (camera looks down -Z, up +Y)"""
    fx, fy, fz = (tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2])
    n = math.sqrt(fx * fx + fy * fy + fz * fz); fx, fy, fz = fx / n, fy / n, fz / n
    # camera axes: z_c = -forward, x_c = forward x up(world z), y_c = z_c x x_c
    zx, zy, zz = -fx, -fy, -fz
    xx, xy, xz = fy * 1 - fz * 0, fz * 0 - fx * 1, fx * 0 - fy * 0
    m = math.sqrt(xx * xx + xy * xy + xz * xz); xx, xy, xz = xx / m, xy / m, xz / m
    if roll:
        c, s = math.cos(roll), math.sin(roll)
        yx0, yy0, yz0 = zy * xz - zz * xy, zz * xx - zx * xz, zx * xy - zy * xx
        xx, xy, xz = c * xx + s * yx0, c * xy + s * yy0, c * xz + s * yz0
    yx, yy, yz = zy * xz - zz * xy, zz * xx - zx * xz, zx * xy - zy * xx
    m00, m01, m02 = xx, yx, zx
    m10, m11, m12 = xy, yy, zy
    m20, m21, m22 = xz, yz, zz
    tr = m00 + m11 + m22
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        return (0.25 * s, (m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s)
    if m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2
        return ((m21 - m12) / s, 0.25 * s, (m01 + m10) / s, (m02 + m20) / s)
    if m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2
        return ((m02 - m20) / s, (m01 + m10) / s, 0.25 * s, (m12 + m21) / s)
    s = math.sqrt(1.0 + m22 - m00 - m11) * 2
    return ((m10 - m01) / s, (m02 + m20) / s, (m12 + m21) / s, 0.25 * s)


# push-in that runs across the loop seam: wide at EV["wide"] .. tight on the hole at WHIP0.
# The target stays centred on both eyes until late (u**3), so frame 0 shows both eyes (the viewer
# compares them to find the gap); the camera sits a little right of and below the target for depth.
WHIP0, WHIP1 = 2.20, 3.00
PUSH_A = dict(tgt=(0.004, 0.0, 0.372), d=1.16)
PUSH_B = dict(tgt=(-0.074, 0.0, 0.438), d=0.34)
PUSH_DIR = (0.09, -1.0, -0.06)
REVEAL = dict(pos=(-0.040, -0.355, 0.050), tgt=(-0.061, -0.130, 0.036), lens=50.0)


def push(t):
    L0 = END - EV["wide"]
    tp = t if t < WHIP1 else t - END
    v = clamp((tp + L0) / (L0 + WHIP0))
    a = 0.22
    c = 1 / (1 - a / 2)
    u = c * v * v / (2 * a) if v <= a else c * a / 2 + c * (v - a)
    tgt = lerp3(PUSH_A["tgt"], PUSH_B["tgt"], u ** 5)
    d = lerp(PUSH_A["d"], PUSH_B["d"], u)
    pos = tuple(tgt[i] + d * PUSH_DIR[i] for i in range(3))
    return pos, tgt, 50.0, tgt, lerp(5.6, 2.8, u)


def smooth_hero(t, sigma=0.22, step=1 / 60):
    """zero-lag gaussian average of the hero's position (follow-cam target)"""
    acc = [0.0, 0.0, 0.0]; wsum = 0.0
    k = -3 * sigma
    while k <= 3 * sigma:
        w = math.exp(-0.5 * (k / sigma) ** 2)
        p = hero(t + k).loc
        acc = [acc[i] + w * p[i] for i in range(3)]; wsum += w
        k += step
    return tuple(a / wsum for a in acc)


def camera(t):
    """-> pos, target, lens(mm), focus point, f-stop"""
    E = EV
    if t < WHIP0 or t >= E["wide"]:
        return push(t)
    if t < WHIP1:                                   # whip down the screen to him
        p0, t0_, _, _, _ = push(WHIP0)
        u = ease_io((t - WHIP0) / (WHIP1 - WHIP0))
        pos = lerp3(p0, REVEAL["pos"], u)
        tgt = lerp3(t0_, REVEAL["tgt"], ease_io((t - WHIP0) / (WHIP1 - WHIP0) * 1.05))
        foc = lerp3(t0_, hero(t).loc, ease_in((t - WHIP0) / (WHIP1 - WHIP0), 3))
        return pos, tgt, 50.0, foc, lerp(5.6, 2.8, u)
    if t < E["try1"]:                               # reveal, then tilt up to the hole (zoom out)
        # dolly back + zoom out + tilt up: the hole ends ~y 620 px, he ends ~y 1490 px (above TikTok's UI)
        u = ease_io((t - 3.75) / 1.45)
        drift = 0.012 * clamp((t - 3.0) / 0.75)
        pos = lerp3((REVEAL["pos"][0], REVEAL["pos"][1] + drift, REVEAL["pos"][2]),
                    (-0.050, -0.55, 0.060), u)
        el = math.radians(16.0)
        up = lerp3(REVEAL["tgt"], (-0.072, -0.55 + 0.4 * math.cos(el), 0.060 + 0.4 * math.sin(el)), u)
        lens = lerp(50.0, 21.0, u)
        foc = lerp3(hero(t).loc, (HOLE[0], 0, HOLE[2] - 0.12), ease_io((t - 4.2) / 0.9))
        return pos, up, lens, foc, lerp(2.8, 4.0, u)
    if t < E["try2"]:                               # TRY 1: three-quarter view, tilts with his jump
        h = hero(t).loc
        u = (t - E["try1"]) / (E["try2"] - E["try1"])
        pos = (0.205 - 0.03 * u, -0.43 + 0.03 * u, 0.080)
        tgt = (-0.060, -0.115, 0.050 + 0.45 * (h[2] - HALF))
        return pos, tgt, 38.0, h, 3.2
    if t < E["try3"]:                               # TRY 2: follow cam
        h = smooth_hero(t)
        u = ease_io((t - E["leap"] + 0.3) / 0.6)    # rises and pulls back for the leap
        off = lerp3((0.150, -0.330, 0.085), (0.165, -0.430, 0.040), u)
        pos = (h[0] + off[0], h[1] + off[1], h[2] + off[2])
        tgt = (h[0] + 0.02, h[1] + 0.03, h[2] + lerp(0.015, 0.06, u))
        return pos, tgt, 35.0, hero(t).loc, 3.2
    if t < E["lift"]:                               # TRY 3: medium on him and the paw
        u = (t - E["try3"]) / (E["lift"] - E["try3"])
        pos = (0.125 - 0.02 * u, -0.400 + 0.02 * u, 0.110)
        tgt = (-0.065, -0.080, 0.075)
        foc = lerp3(hero(t).loc, (HOLE[0], -0.08, 0.05), 0.35)
        return pos, tgt, 36.0, foc, 4.0
    if t < E["click"]:                              # crane up with the paw, push in on the hole
        pg = paw_group(t)[0]
        u = ease_io((t - E["lift"]) / (E["lift_end"] - E["lift"]))
        v = ease_io((t - E["lift_end"]) / (E["click"] - E["lift_end"]))
        base_pos = (0.105, -0.38, 0.110)
        top_pos = (0.020, -0.40, 0.470)
        pos = lerp3(lerp3(base_pos, top_pos, u), (-0.050, -0.245, 0.452), v)
        tgt0 = (-0.065, -0.080, 0.075)
        tgt = lerp3(tgt0, (HOLE[0], -0.04, pg[2] + 0.03), u)
        tgt = lerp3(tgt, (HOLE[0] + 0.004, 0.0, HOLE[2] - 0.004), v)
        lens = lerp(36.0, 50.0, max(u * 0.5, v))
        return pos, tgt, lens, hero(t).loc, 4.0
    # after the click: pull back out to the wide start of the push
    u = ease_io((t - E["click"]) / (E["wide"] - E["click"]))
    p0, t0_ = (-0.050, -0.245, 0.452), (HOLE[0] + 0.004, 0.0, HOLE[2] - 0.004)
    pa, ta, _, _, fa = push(EV["wide"])
    pos = lerp3(p0, pa, u)
    tgt = lerp3(t0_, ta, u)
    return pos, tgt, 50.0, tgt, lerp(4.0, fa, u)


# ---------------------------------------------------------------- bake everything per frame
def build():
    build_hero()
    return EV


def bake():
    build()
    out = dict(hero=[], cam=[], paw=[], pop=[], cat=[])
    for i in range(N):
        t = i / FPS
        out["hero"].append(hero(t))
        out["cam"].append(camera(t))
        out["paw"].append(paw_group(t))
        out["pop"].append([paw_pop(t, k) for k in range(9)])
        out["cat"].append(cat_state(t))
    return out


if __name__ == "__main__":
    import json, sys
    build()
    ev = {k: round(v, 3) for k, v in sorted(EV.items(), key=lambda kv: kv[1])}
    for k, v in ev.items():
        print(f"{v:7.3f}  {k}")
    json.dump(ev, open("timing.json", "w"), indent=1)
