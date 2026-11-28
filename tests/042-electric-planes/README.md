# 042 "1 in 4 flights: going ELECTRIC." Electric planes on short hops (made with the user, 28 Nov 2026)

The user asked for a video on electric planes: how many flights are short enough for electric, how much CO2 that would save, energy use and cost against kerosene, and how they could change aviation. Two futuristic looks to choose from, a banger hook, a seamless loop, no asks. Built like "The 041 playbook" (VIEWS.md).

Looks: **C neon 3D** (the 041 look) and **H cockpit HUD** (new: green phosphor vector graphics, JetBrains Mono, speed/altitude/heading tapes, corner brackets, scanlines, bloom). Both share `common.py` (choreography) and `v042.wav`.

## Narration (full sentences; the last line runs into the first on the loop)
1. Electric planes are coming for one in four flights.
2. That's how many flights are shorter than 500 kilometers, like Munich to Vienna.
3. On a hop like that, a propeller plane turns only a quarter of its fuel into useful power.
4. An electric motor turns over 90 percent into power, so it needs up to three times less energy.
5. For each passenger on a 200 kilometer hop, the energy bill drops from about six dollars to about three.
6. If every flight under 500 kilometers went electric on clean power, we'd save up to 40 million tonnes of CO2 a year.
7. That's like taking nine million cars off the road.
8. A 36-seat airliner built to fly 200 kilometers on battery alone is planned for 2031.
9. Its maker promises 40 percent lower operating costs.
10. The catch is the battery: it's heavy, and it wears out.
11. But batteries get better every year, and that is why  (loops into line 1)

## Facts and the maths (checked 28 Nov 2026)
- **1 in 4:** flights under 500 km are 26.7% of all scheduled passenger flights worldwide but burn 5.2% of the fuel (2024 study of all scheduled flights, Journal of Transport Geography, S096669232400231X). Europe: 24.1% of flights, 3.8% of CO2 in 2019 (EUROCONTROL). Short-haul flights are the ones most likely to be electrified (EUROCONTROL, quoted by NASA EATS 2023).
- **Munich to Vienna:** 355 km great-circle (computed from coordinates).
- **A quarter vs 90%:** turboprop thermal efficiency about 27% on a typical 19-seat mission; electric motor 94%, with inverter 92% (Leeham News, "The true cost of electric aircraft", 2021).
- **Up to 3x less energy:** ICCT 2022 (regional electric aircraft): cruise energy per RPK 9-seat 0.83 vs 2.63 MJ (3.2x), 19-seat 0.45 vs 1.15 (2.6x), 90-seat 0.41 vs 0.84 (2.1x).
- **$6.60 vs ~$3 per passenger, 200 km** (our estimate from ICCT's 19-seat cruise figures): kerosene 1.15 MJ/RPK x 200 km = 230 MJ = 5.34 kg = 1.76 US gal x $3.76/gal (US Gulf Coast Jet A spot, 17 Nov 2026, EIA) = $6.63. Electric 0.45 MJ/RPK x 200 km = 25 kWh, +10% charging = 27.8 kWh x 8.62-13.41 cents/kWh (US 2025 industrial/commercial, EIA) = $2.39-3.73.
- **Up to 40 Mt CO2 a year:** 5.2% x passenger aviation CO2 (84.4% of ~950 Mt in 2023: IEA total, ICCT passenger share) = 41.7 Mt, assuming clean power. ICCT: electric aircraft cut CO2 82-88% on renewable power, 49-57% on today's US grid mix (well-to-wake incl. battery replacement).
- **9 million cars:** 41.7 Mt / 4.6 t per typical passenger vehicle per year (EPA) = 9.1 million.
- **36 seats, 200 km, 2031, -40%:** Heart Aerospace ES-36 (unveiled 23 Sep 2026): 36 seats, 200 km (125 mi) all-electric plus reserves, 1,200 km hybrid, 30 min charging, entry into service targeted 2031, "more than 40% lower aircraft operating costs" (the maker's target). Its X1 demonstrator first flew on 12 Aug 2026. No electric airliner is certified yet.
- **The catch:** batteries hold about 2% of jet fuel's energy per kg; replacement cost per flight can outweigh the fuel saved (Leeham 2021: $339-848 per flight vs $181 of fuel in its 19-seat example).

## Build
- `python3 words.py` (voice A+ through `vo.py`: inner pauses cut, 10% faster, pitch kept; the Whisper check treats km/kilometers, %/percent, $6/six dollars, tons/tonnes as the same words) -> `words.json` -> `timing.py`.
- `python3 render.py C|H stills <t> ...`; full render in two halves per look (`render.py C part 0 2` and `part 1 2`), concat, `python3 audio.py`, `./mux.sh C "-c-neon-3d"` / `./mux.sh H "-h-cockpit-hud"`.
- Loop: the globe turns exactly once per video, stars/floor/tapes are periodic over END, the music's bars tile END (F#m D A E), a riser lands on the frame-0 hit, the last line runs into the first.
