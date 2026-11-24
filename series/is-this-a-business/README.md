# "Is this a business?" (story series; Parts 1-4 made, Part 5 promised)

Inspired by the format of an illustrated "would anyone pay for this?" story series the user sent on 20 Nov 2026. Our story, character, art and music are original.
How it works: Part 1 tells an everyday problem as a micro-story, Part 2 shows a small fix, Part 3 asks whether people would pay for it. Each part ends on a "Next · Part n" card.

**Story:** Jonas lives on floor 4. The house's only washing machine is in the basement (80 stairs each way, 16 per floor).

| Part | File | Length | Hook on frame 0 | Ends with |
|---|---|---|---|---|
| 1 | `videos/022-biz-part1-laundry-stairs.mp4` | 27.0 s | "How one load of laundry became 640 stairs." (counter 0 → 640) | Next · Part 2: "Could a tiny sensor end the stair trips?" |
| 2 | `videos/023-biz-part2-sensor.mp4` | 25.4 s | "A €10 box on the washer. It feels the shaking." | Next · Part 3: "Would 10 flats pay €1 a month for it?" |
| 3 | `videos/024-biz-part3-would-they-pay.mp4` | 22.8 s | "Would 10 flats pay €1 a month for this?" | "Comment YES or NO. If YES wins, Jonas builds it." (sets up a Part 4) |
| 4 | `videos/030-biz-part4-wifi.mp4` | 25.6 s | "Jonas built it. Day one: silence." (voiced A+) | Next · Part 5: "The landlord found out." |

Part 1 beats: taken (no idea how long) → back an hour later: done, but someone's wet laundry is inside → waits 20 min → moves it out, starts his load → 10 minutes late, someone moved HIS laundry ("was in my way!") → 4 trips, 640 stairs → "Now picture 10 flats. One machine."
Part 2 beats: sensor feels shaking = running, still = done → Jonas checks the app first (BUSY → FREE) → loads and scans the QR sticker so the load is his → phone buzzes when done, nudges again if he is slow → 2 trips, 320 stairs.
Part 3 beats: receipt (Wi-Fi chip €6.25, motion sensor €3.40, ~€10; 10 flats × €1 = €10/month, paid off in month 1) → the house votes from their doors (7 yes, 2 no, 1 "can it find my lost sock?") → "Would YOU pay €1?"

## Look
Warm paper background, navy ink outlines (6 px), gold/teal/coral accents, Inter ExtraBold captions in white cards with a hard shadow, Silkscreen for the series pill, stairs counter and labels. Palette in `src/theme.ts`. Cast: Jonas (gold hoodie, curly hair) and 9 neighbours (`NEIGHBOURS` in `src/Part1.tsx`; the pink one in 4B is whose laundry Jonas moved).

## Facts (checked 20 Nov 2026)
- A flight of stairs between floors typically has 13–18 steps; we use 16 per floor (angi.com, gambrick.com).
- DIY washer-done detectors use an accelerometer/vibration sensor on top of the machine plus an ESP32 (Instructables "Washing Machine Notification Sensor", Hackaday, Home Assistant community).
- Prices: ESP32 dev board €6.25–8.93 (Waveshare); MPU-6050 module €3.40 (openelab) / €4.28 (joy-iT). Hence "~€10 in parts".
- The vote in Part 3 is fiction (Jonas's house), not survey data.
- Part 4 (checked 24 Nov 2026): concrete floors and slabs absorb a lot of 2.4 GHz Wi-Fi (Keenetic's attenuation table: concrete floor/ceiling ~15-25 dB, reinforced slab ~20-25 dB, approximate), which is why basements often have no signal. ESP-NOW lets ESP32 boards talk to each other directly without a router (Espressif developer blog, "ESP-NOW for outdoor applications"), so a second ESP32 with Wi-Fi reach can pass the message on. The video names no protocol or dB number, only "a second €6 chip passes the message upstairs".

## Build
```bash
cd series/is-this-a-business
cp ../../kit/fonts/{Inter-Black,Inter-ExtraBold,Inter-Bold,Silkscreen,Silkscreen-Bold,Pacifico,JBMono-Bold}.ttf public/
npm ci
npx remotion bundle src/index.ts --out-dir build
node stills.mjs Part1 0 3.6 15 20        # check frames first (stills/)
CHS=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
npx remotion render build Part1 out/part1_silent.mp4 --browser-executable=$CHS --concurrency=2 --crf=16 --x264-preset=slow
python3 audio1.py                         # score + sfx from the kit, synced to src/part1.json (Part 4: audio4.py, voiced)
bash finish.sh 1                          # full -> standard range, mux at 48 kHz, -14 LUFS -> out/part1.mp4
```
Each part renders in under a minute on the 2-CPU box. All scene times live in `src/part<n>.json`, read by both the video and `audio<n>.py`.

**Narrator (from Part 4, 22 Nov 2026):** voice A via `kit/voice.py`. Write the lines first, `python3 ../../kit/voice.py measure "..."`, set the `part<n>.json` scene times so each line fits its scene, and call `narrate(m, cues)` last in `audio<n>.py`. Parts 1-3 were timed for silence and stay as they are. Upload with `isAiGenerated: true`.

## Suggested captions
- Part 1: "One load of laundry. 640 stairs. Which neighbour are you: 1, 2 or 3? (1 leaves it in, 2 moves it out, 3 writes the note) #laundry #apartmentlife #relatable #startupideas #isthisabusiness"
- Part 2: "A €10 sensor vs 640 stairs. Would you use it? YES or NO #laundry #smarthome #esp32 #startupideas #isthisabusiness"
- Part 3: "7 of 10 flats said yes. Would YOU pay €1 a month? Comment YES or NO. If YES wins, Jonas builds it. #startupideas #buildinpublic #laundry #apartmentlife #isthisabusiness"

Part 4 beats (voiced, A+): DAY 1, the box goes on the running washer, phone: NO SIGNAL (2.35 s) → the app said FREE, 4B walks down (WASTED STAIRS counter), "BUSY?!", walks back up: 160 stairs for nothing → Jonas walks down from 4A, the Wi-Fi bars die floor by floor, "Concrete eats it." (slabs flash) → a second €6 chip above the basement door, the signal hops up, bars back to 4, "+1 LOST SOCK FOUND" (Part 3 callback) → first ping goes to 1A, who voted NO → end card "NEXT · PART 5: The landlord found out." Loops into the basement.
Part 4 uses `LabelFont` = 'sans' everywhere (pill, tags, door/floor labels, washer display in JBMono, phone header): no pixel font (user rule 22 Nov). Parts 1-3 are unchanged (the context defaults to the pixel font).

## Part 4 (promised in Part 3; done 24 Nov as 030)
If the comments lean YES: "Jonas builds it": the box being put together (ESP32 + accelerometer), a test run, the first real ping, and the first month's numbers. Reuse `Washer` (sensor + QR props), `Phone` and the overview.

## Part 5 (promised in Part 4)
"The landlord found out." Story first: the landlord sees the box (stakes: rip it out, or "put one in all my houses"). Beat sheet before building; keep the 2D look (the 24 Nov A/B lean: 2D 022 beat Blender 028 on hold3, avg watch and full watch).
