# "Is this a business?" (story series in cases, one new case a day since 26 Nov; case 1 = laundry, Parts 1-5; case 2 = the parcel; case 3 = locked out). Case list: `CASES.md`

Inspired by the format of an illustrated "would anyone pay for this?" story series the user sent on 20 Nov 2026. Our story, character, art and music are original.
How it works: Part 1 tells an everyday problem as a micro-story, Part 2 shows a small fix, Part 3 asks whether people would pay for it. Each part ends on a "Next · Part n" card.

**Story:** Jonas lives on floor 4. The house's only washing machine is in the basement (80 stairs each way, 16 per floor).

| Part | File | Length | Hook on frame 0 | Ends with |
|---|---|---|---|---|
| 1 | `videos/022-biz-part1-laundry-stairs.mp4` | 27.0 s | "How one load of laundry became 640 stairs." (counter 0 → 640) | Next · Part 2: "Could a tiny sensor end the stair trips?" |
| 2 | `videos/023-biz-part2-sensor.mp4` | 25.4 s | "A €10 box on the washer. It feels the shaking." | Next · Part 3: "Would 10 flats pay €1 a month for it?" |
| 3 | `videos/024-biz-part3-would-they-pay.mp4` | 22.8 s | "Would 10 flats pay €1 a month for this?" | "Comment YES or NO. If YES wins, Jonas builds it." (sets up a Part 4) |
| 4 | `videos/030-biz-part4-wifi.mp4` | 25.6 s | "Jonas built it. Day one: silence." (voiced A+) | Next · Part 5: "The landlord found out." |
| 5 | `videos/033-biz-part5-landlord.mp4` | 25.2 s | "The landlord found the box." (voiced A+) | CASE 1 · CLOSED: "Next: a new problem. Is THAT a business?" |
| C2 P1 | `videos/034-biz-case2-parcel.mp4` | 26.5 s | "How one parcel visited 7 flats." (voiced A+) | Next · Part 2: "One box by the front door?" |
| C3 | `videos/038-biz-case3-locked-out.mp4` | 26.7 s | "How one door click became €240." (voiced A+) | CASE 3 · YOUR CALL: "Is this a business? YES or NO?" + "New case tomorrow. Follow." |

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

## Part 5 (done 25 Nov as 033): finale of case 1
Beats (voiced A+, timing `src/part5.json`, code `src/Part5.tsx`, `audio5.py`): notice taped on the running washer, "BY FRIDAY!" stamp (1.95 s) → overview: STAIRS PER LOAD rolls 320 → 640, six neighbours at their doors ("NOT the stairs!", "Told you." from 1A who voted NO) → hallway: the landlord (`LANDLORD` look: bald, grey tufts, glasses, moustache) "Who said you could?!", Jonas's phone: 14 angry notes last month → 0 since the box → "I own 12 houses." → 12 houses each get a box (BOXES ORDERED 12; 12 × 10 flats × €1 = €120 a month) → the notice is crossed out, new note "Make me 12." → end card CASE 1 · CLOSED. Loops into the basement.

## Why cases (25 Nov data)
Part 1 got 7,066 TikTok views (hold3 69%); Part 2 290 (hold3 53%), Part 3 69 in its first hour (hold3 32%). With no followers, every part is a cold video, and only openings with a relatable problem hold strangers. So each case = a new everyday problem in the same house, and every part opens on a problem or conflict, never on the product or the maths.

## Case 2: the parcel (Part 1 done 25 Nov as 034)
Beats (voiced A+, `src/c2p1.json`, `src/Case2P1.tsx`, `audio_c2p1.py`): banner "Your parcel was delivered", 4A's door opens, empty doormat, "DELIVERED?" stamp (2.65 s) → delivery photo shows door 2A → overview: 2A > 3B > 1A > 0B > 2B > 3A > 4B (FLATS VISITED + stairs, dotted coral trail, one bubble per neighbour) → floor-4 landing: 4B (the pink neighbour from Part 1) opens: "Oh, that's yours? Since Tuesday!" → December: parcels pile up at every door → "Where does YOUR parcel end up?" → Next · Part 2 "One box by the front door?". Pill `SeriesPill label="CASE 2 · PART 1"`.
Part 2 idea: a shared parcel box at the entrance that pings the owner; open on a new problem (the box is full on day one / someone takes the wrong parcel), not on the box itself.

**Voice gotcha:** write numbers above 10 as digits ("640", "12", "160") and use US spelling ("neighbor") in the voice lines, or Whisper's word check burns 5 retakes per line.

## Case 3: locked out (done 27 Nov as 038, one-video case)
Beats (voiced A+, `src/c3p1.json`, `src/Case3P1.tsx`, `audio_c3p1.py`; composition `Case3`; `bash finish.sh c3` after copying `out/c3p1.wav` to `out/partc3.wav`): Jonas steps out in socks with the trash, the door falls shut behind him (keys visible on the hook while it is still open), LOCKED OUT stamp (2.85 s), x-ray of the keys inside → the call: "Door opening €120", "Saturday night × 2", TOTAL €240 (THE BILL counter 0 → 120 → 240) → 70 minutes on a parcel box on the landing, clock 23:10 → 00:20, battery 4% → 2% → 1% → DEAD → the locksmith (coral cap, `LOCKSMITH` look) opens it right away: NOT EVEN LOCKED, invoice €240, PAID → the kiosk downstairs (night street, KIOSK 24/7, SPARE KEYS board with 10 flat keys; owner `KIOSK` look) hands Jonas his spare key → receipt: Locksmith Sat night €240 | Kiosk keeps a key €2/mo | 1 lockout = 10 years → end card "CASE 3 · YOUR CALL: Is this a business? YES or NO? New case tomorrow. Follow." Loops back to the open door.
Facts (checked 27 Nov 2026): ADAC "Schlüsseldienst-Kosten" (June 2026): a simple door opening by day usually costs 80-150 euros incl. travel; night, weekend or holiday 150-250 euros, surcharges 50-100 % on the day price; a door that only fell shut can often be opened without damage. Stiftung Warentest (2019) found 65 to 415 euros for the same fallen-shut door. KeyNest (UK) already stores spare keys at 24/7 shops for £9 a month per key (ex VAT). The €2 kiosk price is Jonas's pitch (fiction).
Voice gotchas: "€240, please." became "240, euros please." (the comma is read into the number; write "240 euros, please."); Whisper heard "cost" as "costs" (used "became"); a sentence-initial "240 euros" was heard as "200 euros" (start with "That's").
