"""027: the pixel-art cat on the tile screen (18 x 24 tiles, row 0 = top).
Shared by the Blender build (tile colours + animation states) and the preview below."""
import json

COLS, ROWS = 18, 24
ART = [
    "..*...........*...",
    "........*.........",
    "...F..........F...",
    "...FF........FF...",
    "...FPF......FPF...",
    "...FPPFFFFFFPPF...",
    "...FFFFfFFfFFFF...",
    "...FFFFFffFFFFF...",
    "...FFYYYFFYYYFF...",
    "...FFYBYFFYBYFF...",
    "...FFYYYFFYYYFF...",
    "...FFFFFFFFFFFF...",
    "ww.FFFFFPPFFFFF.ww",
    "..wFFFWkWWkWFFFw..",
    "....FFFWWWWFFF....",
    ".....FFWWWWFF.....",
    "....FFFWWWWFFF....",
    "....FfFWWWWFfF..f.",
    "...FFfFWWWWFfFF.f.",
    "...FFfFWWWWFfFF.f.",
    "...FFFFWWWWFFFFf..",
    "...FWWWFFFFWWWFf..",
    "...FWPWFFFFWPWFff.",
    "..................",
]
PAL = {
    "F": (185, 190, 228), "f": (122, 130, 184), "k": (92, 70, 168), "P": (255, 120, 190),
    "Y": (255, 211, 107), "B": (104, 52, 170), "W": (240, 242, 255), "w": (150, 160, 215),
    "*": (150, 225, 255),
}
BG_TOP, BG_BOT = (26, 30, 78), (12, 14, 40)
HOLE = (8, 5)                 # (row, col): the gold pixel that fell out (left eye, top-left corner)
EYES = [(8, 5), (8, 10)]      # top-left tile of each 3x3 eye
PAW = [(r, c) for r in (20, 21, 22) for c in (11, 12, 13)]   # the paw that reaches out (viewer's right)


def bg(r):
    t = r / (ROWS - 1)
    return tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))


def base():
    g = []
    for r, line in enumerate(ART):
        assert len(line) == COLS, (r, len(line))
        g.append([PAL.get(ch, bg(r)) for ch in line])
    return g


def state(name):
    """Colour grid for an expression. pupils: look_l / look_c / look_r; blink; happy; squeeze."""
    g = base()
    F, B, Y, k = PAL["F"], PAL["B"], PAL["Y"], PAL["k"]
    for (r0, c0) in EYES:
        cells = [(r0 + i, c0 + j) for i in range(3) for j in range(3)]
        if name.startswith("look"):
            dc = {"look_l": 0, "look_c": 1, "look_r": 2, "look_d": 1, "look_u": 1}[name]
            dr = {"look_d": 2, "look_u": 0}.get(name, 1)
            for (r, c) in cells:
                g[r][c] = Y
            g[r0 + dr][c0 + dc] = B
        elif name == "blink":
            for (r, c) in cells:
                g[r][c] = F
            for j in range(3):
                g[r0 + 1][c0 + j] = k
        elif name == "happy":           # ^ ^
            for (r, c) in cells:
                g[r][c] = F
            g[r0 + 1][c0] = k; g[r0][c0 + 1] = k; g[r0 + 1][c0 + 2] = k
        elif name == "squeeze":         # > <  (sneeze)
            for (r, c) in cells:
                g[r][c] = F
            left = c0 < 9
            g[r0][c0 + (0 if left else 2)] = k
            g[r0 + 1][c0 + 1] = k
            g[r0 + 2][c0 + (0 if left else 2)] = k
    return g


STATES = ["look_c", "look_l", "look_r", "look_u", "look_d", "blink", "happy", "squeeze"]

if __name__ == "__main__":
    from PIL import Image, ImageDraw
    s = 24
    out = Image.new("RGB", (len(STATES) * (COLS * s + 20), ROWS * s), (0, 0, 0))
    for n, st in enumerate(STATES):
        g = state(st)
        d = ImageDraw.Draw(out)
        ox = n * (COLS * s + 20)
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) == HOLE and st in ("look_c", "look_l"):
                    continue
                d.rounded_rectangle((ox + c * s + 1, r * s + 1, ox + c * s + s - 2, r * s + s - 2), 4, fill=g[r][c])
    out.save("/tmp/art_preview.png")
    json.dump({"cols": COLS, "rows": ROWS, "hole": HOLE, "paw": PAW, "eyes": EYES,
               "states": {st: state(st) for st in STATES}}, open("art.json", "w"))
    print("ok")
