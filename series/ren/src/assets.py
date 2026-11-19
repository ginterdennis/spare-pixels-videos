"""Hand-placed pixel art for 'Ren: Day 1'. Every sprite is a character grid; '.' is transparent."""
import numpy as np

def hx(h):
    h = h.lstrip("#"); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

OUT = hx("0a0b14")

# ---------------- inventory items (16x16) ----------------
ITEMS = []   # (key, name, sub, grid, palette)

def item(key, name, sub, rows, pal):
    for r in rows: assert len(r) == 16, (key, r, len(r))
    assert len(rows) == 16, (key, len(rows))
    p = {"k": OUT}; p.update({c: hx(v) for c, v in pal.items()})
    ITEMS.append(dict(key=key, name=name, sub=sub, grid=rows, pal=p))

item("bottle", "WATER BOTTLE", "half full", [
    "......kkkk......",
    "......kbbk......",
    "......kbbk......",
    ".....kkkkkk.....",
    ".....kppphk.....",
    "....kpppphpk....",
    "....kpppphpk....",
    "....kpppphpk....",
    "....kssssssk....",
    "....kWWWWHWk....",
    "....kWWWWHWk....",
    "....kWWWWHWk....",
    "....kWWWWWWk....",
    "....kWWWWWWk....",
    ".....kkkkkk.....",
    "................"], dict(b="2f6fe0", p="cfe2f7", h="ffffff", s="a8dcff", W="3d8fe0", H="7fc0ff"))

item("knife", "POCKET KNIFE", "", [
    "................",
    "............kk..",
    "...........khk..",
    "..........khGk..",
    ".........khGk...",
    "........khGk....",
    ".......khGk.....",
    "......kMMk......",
    ".....kRRRk......",
    "....kRRRk.......",
    "...kRwRk........",
    "..kRRRk.........",
    "..kkkk..........",
    "................",
    "................",
    "................"], dict(h="eef1f8", G="9aa2b8", M="6b7088", R="d23a32", w="ffffff"))

item("battery", "9V BATTERY", "", [
    "................",
    "....kk....kk....",
    "...kggk..kggk...",
    "..kkkkkkkkkkkk..",
    "..kCCCCCCCCCCk..",
    "..kCcCCCCCCCCk..",
    "..kNNNNNNNNNNk..",
    "..kNwwwNwNwNNk..",
    "..kNwNwNwNwNNk..",
    "..kNwwwNwNwNNk..",
    "..kNNNwNwNwNNk..",
    "..kNwwwNNwNNNk..",
    "..kNNNNNNNNNNk..",
    "..kNNNNNNNNNNk..",
    "..kkkkkkkkkkkk..",
    "................"], dict(g="c9cede", C="d9893a", c="f2b26b", N="2b3150", w="f2f4ff"))

item("steelwool", "STEEL WOOL", "", [
    "................",
    "................",
    "......kkkk......",
    "....kkgGhGkk....",
    "...kgGgGGgGgk...",
    "..kGgGhgGgGgGk..",
    "..kgGGgGgGGgGk..",
    ".kgGgGgGgGhGgGk.",
    ".kGgGGgGgGGgGgk.",
    ".kgGhGgGGgGgGGk.",
    "..kGgGgGgGgGgk..",
    "..kgGGgGgGhGGk..",
    "...kGgGgGgGgk...",
    "....kkgGgGkk....",
    "......kkkk......",
    "................"], dict(g="b8bccb", G="767b90", h="eef0f7"))

item("tape", "DUCT TAPE", "", [
    "................",
    "................",
    ".....kkkkkk.....",
    "...kkhgggggkk...",
    "..khgggggggGGk..",
    "..kgggkkkkgGGk..",
    ".khggk....kgGGk.",
    ".kgggk....kgGGk.",
    ".kgggk....kgGGk.",
    ".kgggk....kgGGk.",
    "..kgggkkkkgGGkk.",
    "..kgggggggGGGkgk",
    "...kkgggggGkk.gk",
    ".....kkkkkk...gk",
    "..............kk",
    "................"], dict(g="b9bfcc", G="878da0", h="eef1f6"))

item("paracord", "PARACORD", "10 m", [
    "................",
    "................",
    "....kkkkkkkk....",
    "..kkOoOoOoOokk..",
    ".kOokkkkkkkkoOk.",
    ".kok.kkkkkk.kok.",
    ".kOkkOoOoOokkOk.",
    ".kokOkkkkkkoko..",
    ".kOkok....kOkk..",
    ".kokOkkkkkkoko..",
    ".kOkkoOoOoOkkOk.",
    ".kok.kkkkkk.kok.",
    ".kOokkkkkkkkoOk.",
    "..kkoOoOoOoOkk..",
    "....kkkkkkkoOk..",
    "..........kkOk.."], dict(O="f07a2c", o="b9521c"))

item("blanket", "SPACE BLANKET", "", [
    "................",
    "................",
    "..kkkkkkkkkkkk..",
    "..kSSsSSSsSSSk..",
    "..kSsSSDSSsSSk..",
    "..kSSSDSSSSsSk..",
    "..kSSDSSsSSSDk..",
    "..kSDSSSSDSSSk..",
    "..kDSSsSSSDSSk..",
    "..kSSSSSDSSsSk..",
    "..kSsSSDSSSSSk..",
    "..kSSSDSSsSSDk..",
    "..kSSSSSSSSSSk..",
    "..kkkkkkkkkkkk..",
    "................",
    "................"], dict(S="e3bd45", s="fff2b8", D="a8822a"))

item("phone", "DEAD PHONE", "", [
    "................",
    "....kkkkkkkk....",
    "....kDDDDDDk....",
    "....kSSSSSSk....",
    "....kSSScSSk....",
    "....kSScSSSk....",
    "....kScSSSSk....",
    "....kSccSSSk....",
    "....kSSScSSk....",
    "....kSSSScSk....",
    "....kSSSScSk....",
    "....kSSSSSSk....",
    "....kDDDDDDk....",
    "....kDDDDDDk....",
    "....kkkkkkkk....",
    "................"], dict(D="3a3f55", S="14172a", c="8a93c0"))

item("needle", "SEWING NEEDLE", "", [
    "................",
    "............kkk.",
    "...........kg.gk",
    "..........kg.gk.",
    ".........kggkk..",
    "........kggk..r.",
    ".......kggk...r.",
    "......kggk...r..",
    ".....kggk...r...",
    "....kggk..rr....",
    "...kggk..r......",
    "..kggk..........",
    ".kgk............",
    ".kk.............",
    "................",
    "................"], dict(g="dfe3ee", r="e0453a"))

item("granola", "GRANOLA BARS", "x3", [
    "................",
    "................",
    "................",
    "................",
    ".kkkkkkkkkkkkkk.",
    "kGkGGGGGGGGGGkGk",
    ".kkGyyyyyyyyGkk.",
    "kGkGybybyybyGkGk",
    ".kkGyyyyyyyyGkk.",
    "kGkGGGGGGGGGGkGk",
    ".kkkkkkkkkkkkkk.",
    "................",
    "................",
    "................",
    "................",
    "................"], dict(G="3fa34d", y="f3d46b", b="9a6a2e"))

item("bags", "TRASH BAGS", "x2", [
    "................",
    ".......kk.......",
    "......kBBk......",
    ".....kBkkBk.....",
    "......kBBk......",
    ".....kBBBBk.....",
    "....kBBBBBBk....",
    "...kBBBBBBBBk...",
    "..kBBBhBBBBBBk..",
    "..kBBhBBBBBBBk..",
    ".kBBBhBBBBBBBBk.",
    ".kBBBBBBBBBBBBk.",
    ".kBBBBBBBBBBBBk.",
    "..kBBBBBBBBBBk..",
    "...kkkkkkkkkk...",
    "................"], dict(B="2e3348", h="6a7194"))

item("lighter", "EMPTY LIGHTER", "", [
    "................",
    "......kkkkk.....",
    "......kgGgk.....",
    ".....kWkGgk.....",
    ".....kkkkkkk....",
    ".....kRRRRRk....",
    ".....kRrRRRk....",
    ".....kRrRRRk....",
    ".....kRRRRRk....",
    ".....kRRRRRk....",
    ".....kRRRRRk....",
    ".....kRRRRRk....",
    ".....kRRRRRk....",
    ".....kkkkkkk....",
    "................",
    "................"], dict(g="d8dce8", G="8d93a8", W="555a70", R="c94848", r="ee8c8c"))

# ---------------- Ren (back view, 20x32) ----------------
REN_PAL = {"k": OUT, "H": hx("a83c27"), "d": hx("7a2a1c"), "h": hx("d0573a"), "S": hx("e2b04a"), "s": hx("b98a2c"),
           "J": hx("c4462d"), "j": hx("e06a48"), "P": hx("4c5c3b"), "p": hx("6e8152"), "Q": hx("39472c"),
           "G": hx("2b2f45"), "N": hx("2a2f48"), "n": hx("3c4466"), "B": hx("1b1d2a"), "b": hx("34384f")}
REN_A = [
    "........kkkk........",
    "......kkHHHHkk......",
    ".....kdHHHHHhHk.....",
    "....kdHHHHHHHhHk....",
    "....kdHHHHHHHhHk....",
    "....kdHHHHHHHHHk....",
    "....kddHHHHHHHHk....",
    ".....kddddddddk.....",
    "....kkSSSSSSsSkk....",
    "...kJJkSSSSSSkjJk...",
    "..kJJkkkkkkkkkkjJk..",
    "..kJJkPPPPPPPPkjJk..",
    "..kJJkPpPPPPpPkjJk..",
    "..kJJkPpPPPPpPkjJk..",
    "..kJJkPPkkkkPPkjJk..",
    "..kJJkPPkQQkPPkjJk..",
    "..kJJkPPkkkkPPkjJk..",
    "..kJJkPPPPPPPPkjJk..",
    "..kGGkPPPPPPPPkGGk..",
    "..kkkkkkkkkkkkkkkk..",
    "....kJJJJJJJJJJk....",
    "....kJJJJJJJJjJk....",
    "....kNNNnkkNNNnk....",
    "....kNNNnk.kNNnk....",
    "....kNNNnk.kNNnk....",
    "....kNNNnk.kNNnk....",
    "....kNNNnk.kNNnk....",
    "....kNNNnk.kNNnk....",
    "...kBBBbBk.kBBbBk...",
    "...kBBBBBk.kBBBBk...",
    "...kkkkkkk.kkkkkk...",
    "...................."]
# scarf tail fluttering in the wind (two frames, drawn to the right of the neck)
SCARF_A = [(14, 8, "S"), (15, 8, "S"), (16, 7, "S"), (16, 8, "s"), (17, 7, "S"), (18, 6, "s")]
SCARF_B = [(14, 8, "S"), (15, 9, "S"), (16, 9, "S"), (16, 8, "s"), (17, 9, "s"), (18, 10, "S")]
for r in REN_A: assert len(r) == 20, (r, len(r))
assert len(REN_A) == 32

def grid_to_rgba(rows, pal, extra=()):
    h, w = len(rows), len(rows[0])
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != ".":
                a[y, x, :3] = pal[c]; a[y, x, 3] = 255
    for x, y, c in extra:
        if 0 <= x < w and 0 <= y < h:
            a[y, x, :3] = pal[c]; a[y, x, 3] = 255
    return a

def ren_sprite(frame):
    return grid_to_rgba(REN_A, REN_PAL, SCARF_A if frame % 2 == 0 else SCARF_B)

def item_rgba(it):
    return grid_to_rgba(it["grid"], it["pal"])
