import numpy as np
LEFT = [
"............",
"............",
"..KK........",
"..oKK.......",
"..oIOO......",
"..oIIOO.....",
"..oIIIOO....",
"..oIIIIOO...",
".ooIIIIOOOOO",
".oOOOOOOOOOO",
"ooOOOOOOOOOO",
"oOOOOOOOOOOO",
"oOOOKEOOOOOO",
"WOOOKKOOOOOO",
"WWOOOOOOOOOO",
"WWWOOOOOOOOO",
".WWWWOOOOOOO",
"..WWWWWOOOOO",
"...WWWWWWWOO",
"....WWWWWWWW",
".....WWWWWKK",
"......WWWWKK",
".......WWWWW",
"............",
]
ROWS = [l + l[::-1] for l in LEFT]
PAL = {
 "O": (236, 122, 44), "o": (190, 86, 28), "W": (247, 238, 222), "K": (26, 24, 34),
 "E": (250, 250, 255), "I": (92, 40, 30),
}
def bg(r, c):
    t = r / 23
    top = np.array((22, 52, 92)); bot = np.array((40, 128, 140))
    col = top * (1 - t) + bot * t
    # a few faint stars
    if (r * 7 + c * 13) % 29 == 0 and r < 12: col = col * 0.5 + np.array((230, 240, 255)) * 0.5
    return tuple(int(x) for x in col)
def grid():
    N = len(ROWS)
    a = np.zeros((N, N, 3), np.uint8)
    for r, row in enumerate(ROWS):
        for c, ch in enumerate(row):
            a[r, c] = PAL[ch] if ch in PAL else bg(r, c)
    return a
if __name__ == "__main__":
    from PIL import Image
    g = grid()
    Image.fromarray(np.kron(g, np.ones((20, 20, 1), np.uint8))).save("preview.png")
