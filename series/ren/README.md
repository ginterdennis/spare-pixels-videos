# REN — a pixel-art survival series by Spare Pixels

## Premise
A solar storm knocked out the power grid. No phones, no internet, no help coming.
Winter arrives in 21 days. Ren (always seen from behind, hood up, red jacket, olive backpack)
has 12 items. One part = one day.

## Episode format (Part N = Day N, 30–45 s, 9:16)
1. **Hook (0–3 s):** "DAY N" + the day's problem as a question in the dialogue box. The first frame must make sense on its own.
2. **Setup:** what goes wrong today and why it matters (water, cold, fire, food, injury, finding a route…).
3. **The smart part:** Ren solves it with items from the backpack, shown step by step.
   The trick must be real, physically correct survival science — check the facts before using them.
4. **Inventory screen:** what Ren has left. Used-up items disappear or change state (e.g. bottle level),
   found items can be added. Update the WATER / FOOD / WINTER meters.
5. **Close:** "Which item saves Ren next?" then "Day N+1 next. Follow so Ren survives."

## Episode plan (draft — adjust to what comments ask for)
| Day | Problem | Smart solution (real) | Items |
|---|---|---|---|
| 2 | The water runs out | Melt snow in a black trash bag in the sun; never eat snow directly, it drains body heat | trash bag, bottle |
| 3 | Freezing night, no fire | Touch both 9V terminals to steel wool: it glows and ignites tinder | 9V battery, steel wool |
| 4 | Lost without GPS | Stroke the sewing needle on the dead phone's speaker magnet, float it: a compass | needle, dead phone |
| 5 | Shelter from wind and cold | Lean-to from paracord + trash bags, space blanket reflecting heat inward | paracord, bags, space blanket |
| 6 | The lighter is "empty" | The flint wheel still sparks: catch the spark on dry tinder | empty lighter |

## Current state
See `state.json` (single source of truth; update it after every episode).

## Look and sound
- World drawn at 270×480 and scaled ×4 (×8 for close-ups) with nearest-neighbour; dithered night sky, aurora.
- Font: Silkscreen (OFL) at sizes that are multiples of 8 px; RPG dialogue boxes with typewriter text.
- Palette: navy night, aurora green/teal/violet, accent #FFD36B, Ren's jacket #C4462D.
- Music: 104 BPM chip-style pulse arpeggio + pad; item pickups land on the beat.
- Narrator (from Part 4, 22 Nov 2026): voice A via `kit/voice.py` (`narrate()` last in audio.py). Write the lines first and time the scenes from `voice.py measure`. Upload with `isAiGenerated: true`.
- Code: `src/` (assets.py = sprites, scene.py = picture, audio.py = sound).
  Fonts: `npm pack @fontsource/silkscreen`, convert the latin .woff files to .ttf with `src/woff2ttf.py` into `fonts/`.
