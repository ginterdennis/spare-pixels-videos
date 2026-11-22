"""028: "Is this a business?" Part 1 remade in Blender (A/B test against the 2D original 022).

Every motion is a pure function of time, ported 1:1 from the Remotion original
(series/is-this-a-business/src/Part1.tsx, Building.tsx, part1.json), so the 3D picture hits the
same beats as 022's captions, stairs counter and soundtrack. No bpy here: the Blender build
(blender/build028.py) bakes it, and the cloud side imports it for checks.
Units: metres, seconds. Blender axes: z up, the cutaway faces -y (camera at negative y).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_T = os.path.join(HERE, "part1.json")
if not os.path.exists(_T):
    _T = os.path.join(HERE, "..", "..", "series", "is-this-a-business", "src", "part1.json")
T = json.load(open(_T))
FPS = 30
END = T["end"]
N = int(round(END * FPS))

# ------------------------------------------------------------------ the original's 2D geometry (px)
LV = [492, 622, 752, 882, 1012, 1162]          # floor lines 4, 3, 2, 1, 0, -1
SA, SB = 330, 650
MACHINE_X = 842
DOOR_L, DOOR_R = 196, 824

# ------------------------------------------------------------------ 3D layout (m)
SX = 0.0185                                    # 1 px of the original = 1.85 cm horizontally
FH = 2.6                                       # floor height


def X(px):
    return (px - 510) * SX


Z = [(5 - k) * FH for k in range(6)]           # floor surface of level k (0 = floor 4 ... 5 = basement)
HOUSE_X0, HOUSE_X1 = X(110), X(910)            # -7.4 .. 7.4
DEPTH = 3.4                                    # back wall at y = DEPTH
Y_STAIR = 1.55                                 # walking line on the stairs / basement floor
STAIR_W = 1.25
Y_DOOR = 2.75                                  # standing in front of a door (doors on the back wall)
WASHER = (X(MACHINE_X), 2.62, 0.0)             # washer centre on the floor, against the back wall
STAND = X(MACHINE_X - 82)                      # where the path ends, left of the washer


def path2d(lv, side="L"):
    pts = [(DOOR_L if side == "L" else DOOR_R, LV[lv])]
    for k in range(lv, 5):
        xs, xe = (SA, SB) if k % 2 == 0 else (SB, SA)
        pts += [(xs, LV[k]), (xe, LV[k + 1])]
    pts.append((MACHINE_X - 82, LV[5]))
    return pts


def path3d(lv, side="L"):
    """same vertices as path2d, in 3D"""
    p = [(X(DOOR_L if side == "L" else DOOR_R), Y_DOOR, Z[lv])]
    for k in range(lv, 5):
        xs, xe = (SA, SB) if k % 2 == 0 else (SB, SA)
        p += [(X(xs), Y_STAIR, Z[k]), (X(xe), Y_STAIR, Z[k + 1])]
    p.append((STAND, Y_STAIR, Z[5]))
    return p


def _lens(p):
    L = [0.0]
    for i in range(1, len(p)):
        L.append(L[-1] + math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]))
    return L


def along(lv, side, u):
    """(x, y, z), heading of motion (+1 right / -1 left), walked metres, on stairs?, for fraction u
    of the ORIGINAL 2D path (so u means the same as in the 2D version and in its stairs counter)"""
    p2, p3 = path2d(lv, side), path3d(lv, side)
    L = _lens(p2)
    tot = L[-1]
    d = min(tot, max(0.0, u * tot))
    i = 1
    while i < len(p2) - 1 and L[i] < d:
        i += 1
    seg = (L[i] - L[i - 1]) or 1.0
    k = (d - L[i - 1]) / seg
    a, b = p3[i - 1], p3[i]
    pos = tuple(a[j] + (b[j] - a[j]) * k for j in range(3))
    face = 1 if p2[i][0] >= p2[i - 1][0] else -1
    walked = sum(math.dist(p3[j - 1], p3[j]) for j in range(1, i)) + math.dist(a, pos)
    stairs = abs(p2[i][1] - p2[i - 1][1]) > 1
    return pos, face, walked, stairs


# ------------------------------------------------------------------ helpers (as in theme.ts)
def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_in_out(x):
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def tw(t, start, dur, ease=None):
    k = clamp01((t - start) / dur) if dur else (1.0 if t >= start else 0.0)
    return ease(k) if ease else k


def lerp(a, b, k):
    return a + (b - a) * k


def ins(t, s):
    return s[0] <= t < s[1]


# ------------------------------------------------------------------ colours (theme.ts)
C = dict(paper="#F3ECE0", ink="#1C2140", navy="#283163", wall="#E9DFCE", wallDark="#DCCFB9",
         basement="#D8CCB6", floor="#C9B99D", earth="#BFA88A", stair="#D9C8AA", gold="#FFC94D",
         goldDark="#E8A92A", teal="#2F8F89", coral="#EF6A57", pink="#F28DB2", lilac="#B79BE0",
         sky="#8FC1E3", white="#FBF8F2", skin="#F2C29B", skin2="#C98B62", skin3="#8D5A3B",
         hair="#3B2A22", green="#5FA36B")
NEIGHBOUR_LAUNDRY = ["pink", "lilac", "coral", "pink", "sky"]
JONAS_LAUNDRY = ["gold", "navy", "white", "goldDark", "teal"]
JONAS = dict(hoodie="gold", pants="navy", hair="hair", skin="skin", shoes="white", style="curly")
NEIGHBOURS = [  # (look, level, side, phase offset, speed, basket)
    (dict(hoodie="pink", pants="ink", hair="#C8692E", skin="skin", shoes="white", style="bun"), 0, "R", 0.1, 0.55, NEIGHBOUR_LAUNDRY),
    (dict(hoodie="teal", pants="#6B5A4A", hair="hair", skin="skin2", shoes="ink", style="short"), 1, "L", 0.45, 0.62, ["white", "sky", "navy"]),
    (dict(hoodie="coral", pants="navy", hair="#E7C36A", skin="skin", shoes="white", style="long"), 1, "R", 0.8, 0.5, ["lilac", "white", "pink"]),
    (dict(hoodie="lilac", pants="ink", hair="hair", skin="skin3", shoes="white", style="curly"), 2, "L", 0.25, 0.58, ["gold", "teal", "white"]),
    (dict(hoodie="sky", pants="#4E4A6B", hair="#8E8E8E", skin="skin", shoes="ink", style="bald"), 2, "R", 0.6, 0.47, ["navy", "white", "sky"]),
    (dict(hoodie="green", pants="ink", hair="hair", skin="skin2", shoes="white", style="cap"), 3, "L", 0.05, 0.6, ["coral", "white", "gold"]),
    (dict(hoodie="navy", pants="#7A6A58", hair="#C8692E", skin="skin", shoes="white", style="short"), 3, "R", 0.7, 0.52, ["white", "white", "sky"]),
    (dict(hoodie="white", pants="teal", hair="hair", skin="skin3", shoes="ink", style="bun"), 4, "L", 0.35, 0.66, ["pink", "gold", "lilac"]),
    (dict(hoodie="goldDark", pants="ink", hair="#E7C36A", skin="skin", shoes="white", style="curly"), 4, "R", 0.9, 0.6, ["teal", "white", "navy"]),
]


# ------------------------------------------------------------------ scene logic (ports of Part1.tsx)
CLOSE = ("s2", "s4", "s6", "s8")


def is_close(t):
    return any(ins(t, T[s]) for s in CLOSE)


ZOOM_MAX = 3.4


def zoom_at(t):
    zin = lambda end: lerp(1, ZOOM_MAX, tw(t, end - T["zoomIn"], T["zoomIn"], ease_in_out))
    zout = lambda start: lerp(ZOOM_MAX, 1, tw(t, start, T["zoomOut"], ease_out))
    if ins(t, T["s1"]):
        return zin(T["s1"][1])
    for s, up in (("s3", "up3"), ("s5", "up5"), ("s7", "up7")):
        if ins(t, T[s]):
            return zout(T[s][0]) if t < T[up][0] else zin(T[s][1])
    if t >= T["s9"][0]:
        return zout(T["s9"][0])
    return 1.0


def jonas_overview(t):
    """-> dict(u, basket, moving, rev, visible, face) on the Jonas path (level 0, side L)"""
    def down(a, basket):
        u = tw(t, a[0], a[1] - a[0])
        return dict(u=u, basket=basket, moving=a[0] <= t < a[1], rev=False, visible=True, face=None)

    def up(a, basket):
        u = 1 - tw(t, a[0], a[1] - a[0])
        return dict(u=u, basket=basket, moving=a[0] <= t < a[1], rev=True, visible=True, face=None)

    if ins(t, T["s1"]):
        u = lerp(0.03, 1, tw(t, T["walk1"][0], T["walk1"][1] - T["walk1"][0], lambda x: 1 - (1 - x) ** 1.5))
        return dict(u=u, basket=JONAS_LAUNDRY, moving=t < T["walk1"][1], rev=False, visible=True, face=None)
    for s, upk, tag, dn, basket in (("s3", "up3", "tag3", "down3", JONAS_LAUNDRY), ("s5", "up5", "tag5", "down5", JONAS_LAUNDRY),
                                    ("s7", "up7", "tag7", "down7", [])):
        if ins(t, T[s]):
            if t < T[tag]:
                return up(T[upk], basket)
            r = down(T[dn], basket)
            if t < T[dn][0]:
                r["visible"] = False
            return r
    r = up(T["up9"], JONAS_LAUNDRY)
    if t >= T["up9"][1]:
        r["moving"] = False
        r["face"] = 1
    if t >= T["cardOut"]:
        k = tw(t, T["cardOut"], 0.4, ease_in_out)
        r = dict(u=0.03 * k, basket=JONAS_LAUNDRY, moving=False, rev=False, visible=True, face=1)
    return r


def crowd_k(t):
    return tw(t, T["crowd9"], 0.35, ease_out) * (1 - tw(t, T["cardOut"], 0.35, ease_in_out))


def neighbour(t, i):
    look, lv, side, off, spd, basket = NEIGHBOURS[i]
    ph = ((t - T["crowd9"]) * spd * 0.9 + off) % 2
    u = ph if ph < 1 else 2 - ph
    return dict(u=u, rev=ph >= 1, basket=basket, lv=lv, side=side)


def washer_state(t):
    """state, drum colours, pile on top (colours or None), pile growth 0..1, sock, display, door open 0..1"""
    st = dict(state="running", drum=NEIGHBOUR_LAUNDRY, pile=None, pileK=1.0, sock=False, display="RUN", door=0.0)
    if t >= T["s3"][0] + 0.9:
        st.update(state="done", display="END", sock=True)
    if t >= T["s6"][0]:
        m0, ld, s6 = T["move6"][0], T["load6"], T["start6"]
        st.update(state="done" if t < s6 else "running", display="END" if t < s6 else "1:50",
                  sock=t < m0 + 0.3,
                  drum=NEIGHBOUR_LAUNDRY if t < m0 + 0.45 else ([] if t < ld else JONAS_LAUNDRY),
                  pile=NEIGHBOUR_LAUNDRY, pileK=tw(t, m0 + 0.2, 0.6, ease_out),
                  door=clamp01((t - (m0 - 0.25)) / 0.2) * (1 - clamp01((t - (s6 - 0.2)) / 0.18)))
    if t >= T["s7"][0] + 1.0:
        st.update(state="done", display="END", drum=JONAS_LAUNDRY, pile=None, sock=False, door=0.0)
    if t >= T["s8"][0]:
        st.update(state="running", display="RUN", drum=NEIGHBOUR_LAUNDRY, pile=JONAS_LAUNDRY, pileK=1.0, sock=False)
    if t >= T["s9"][0]:
        st.update(pile=None)
    if t >= T["cardOut"]:
        st.update(state="running", drum=NEIGHBOUR_LAUNDRY, pile=None)
    return st


def clock_minutes(t):
    if ins(t, T["s4"]):
        return 20 * tw(t, T["clock4"][0], T["clock4"][1] - T["clock4"][0], ease_in_out)
    return 0.0 if t < T["s4"][0] else 20.0


def note_k(t):
    return tw(t, T["note8"], 0.35, ease_out) if t >= T["s8"][0] and t < T["s9"][0] else 0.0


# ------------------------------------------------------------------ Jonas in the close-ups (port of CloseUp)
PX_M = 1.35 / 400        # close-up px -> m (Jonas at 300 px stands 1.35 m left of the washer at 700 px)


def jonas_close(t):
    s0 = next(T[s][0] for s in CLOSE if ins(t, T[s]))
    jx, face, walk_m, pose = 300, 1, None, "carry"
    expr, basket, floor_basket, pose_k, sweat, tap, holding = "neutral", JONAS_LAUNDRY, None, 1.0, 0.0, 0.0, None

    def leave(at):
        nonlocal face, jx, walk_m
        if t >= at - 0.12:
            face = -1
        if t >= at:
            d = (t - at) * 820
            jx -= d
            walk_m = d * PX_M

    if ins(t, T["s2"]):
        expr = "shock" if t < s0 + 0.9 else "tired"
        sweat = tw(t, s0 + 0.5, 0.4)
        leave(T["leave2"])
    elif ins(t, T["s4"]):
        expr = "annoyed"
        if t >= T["clock4"][0]:
            tap = (t - T["clock4"][0]) * 18
            expr = "tired"
        leave(T["leave4"])
    elif ins(t, T["s6"]):
        jx = 430
        m0 = T["move6"][0]
        expr = "annoyed" if t < m0 else "neutral"
        if m0 - 0.15 <= t < T["leave6"] - 0.1:
            pose = "reach"
            cyc = (t - m0) * 2.6
            pose_k = 0.5 - 0.5 * math.cos(cyc * math.pi * 2)
            basket = None
            floor_basket = JONAS_LAUNDRY if t < T["load6"] else []
            if m0 <= t < T["load6"]:
                holding = "pink" if t < m0 + 0.45 else "gold"
        if t >= T["leave6"] - 0.1:
            basket = []
        if t >= T["start6"]:
            expr = "happy"
        leave(T["leave6"])
    else:  # s8
        basket = []
        expr = "neutral" if t < s0 + 0.25 else "shock"
        sweat = tw(t, s0 + 0.6, 0.3)
    settle = 1 - tw(t, s0, 0.35, ease_out)
    x = WASHER[0] - (700 - jx) * PX_M
    return dict(x=x, face=face, walk=walk_m, pose=pose, pose_k=pose_k, expr=expr, basket=basket,
                floor_basket=floor_basket, sweat=sweat, tap=tap, holding=holding, settle=settle)


# ------------------------------------------------------------------ events for checks
def events():
    ev = {k: v for k, v in T.items() if isinstance(v, (int, float))}
    for k, v in T.items():
        if isinstance(v, list):
            ev[k + "_0"], ev[k + "_1"] = v
    return ev


if __name__ == "__main__":
    print("frames", N, "close-up frames", sum(is_close(i / FPS) for i in range(N)))
    for t in (0.0, 1.0, 2.5, 6.5, 12.5, 17.6, 22.3, 26.9):
        j = jonas_overview(t)
        pos, face, walked, stairs = along(0, "L", j["u"])
        print(f"t={t:5.2f} u={j['u']:.3f} pos=({pos[0]:.2f},{pos[1]:.2f},{pos[2]:.2f}) face={face} zoom={zoom_at(t):.2f}")
