# 041 "This would END the modern world." P vs NP (made with the user, 27 Nov 2026)

The user asked for a P vs NP video (hook: proving it would destroy the modern world as we know it; clean mathematical style; origin, why it matters today, what proving it true would mean), saw the script first, then picked the **neon 3D** look out of three (A night grid, B notebook, C neon). v2 after the user's notes: narration in full sentences, the example (a sudoku) laid out step by step, no share prompt, a seamless loop. The user's verdict on v2: "Wow, it's so good." What made it work is written up as **"The 041 playbook" in VIEWS.md**.

Final file: `videos/041-p-vs-np.mp4` (44.4 s, voice A+, AI label on). Look C; looks A and B still render (`python3 render.py A|B`; A needs matplotlib's cmr10/cmb10/cmtt10/cmti10 copied into `fonts/`).

## Narration (v2, full sentences; the last line runs into the first on the loop)
1. Proving this would destroy the modern world as we know it.
2. In 1971, Stephen Cook asked: if an answer is easy to check, is it also easy to find?
3. Think of a sudoku.
4. Checking a finished one is easy: no number may repeat in a row, a column or a box.
5. But solving an empty one is hard, because you have to try number after number.
6. Make the grid bigger, and there are more ways to fill it than atoms in the universe.
7. That gap is what keeps your bank and your crypto wallet safe.
8. If P equals NP, there is a shortcut, and every lock opens.
9. But we'd also get perfect routes, smarter AI, and machines that write their own proofs.
10. The modern world would end, and a new one would begin.
11. Most experts bet it's false, and nobody has proven it, not even AI.
12. Just remember:  (loops into line 1)

## Build
- `python3 words.py`: voice A+ takes for every line through `vo.py` (pauses inside a line cut to 0.24 s, 10% faster with ffmpeg atempo, pitch kept), Whisper word timestamps -> `words.json`. `timing.py` turns those into scene times (`A[...]`, `wt(line, word)`), read by render and audio.
- `python3 render.py C stills <t> ...` for checks; full render in two halves: `python3 render.py C part 0 2 & python3 render.py C part 1 2`, concat (`ffmpeg -f concat -c copy`), then `python3 audio.py` and `./mux.sh C ""` (loudnorm -14, AAC 48 kHz).
- `common.py` = the director (scenes, data: sudoku grids, route, net), `styles.py` = the three looks (Base primitives; NightGrid, Notebook, Neon with bloom, perspective planes and loop-periodic stars/floor/camera).
- Loop: END = "Just remember:" + 0.32 s; the last 1.3 s glide back to the frame-0 picture; music bars tile END exactly (Am F C G, ends on G), riser into the frame-0 hit. Seam |last - frame 0| = 1.0 vs 0.7 for a normal frame step.
- hookcheck: all PASS (6 words, motion 4.7, peak -2.5 dB, reveal 2.4 s, contrast 69). Whisper on the final mix hears every line, and across the loop point "...not even AI. Just remember. Proving this would destroy the modern world as we know it."

## Facts (checked 27 Nov 2026)
- Cook 1971 ("The Complexity of Theorem-Proving Procedures", STOC), Levin 1973 independently, Godel's 1956 letter to von Neumann (Wikipedia P vs NP; ACM Turing award page).
- Clay Millennium Prize, $1,000,000 (Fortnow, CACM 2009).
- 88% of respondents believed P != NP in Gasarch's 2019 poll (61% in 2002, 83% in 2012).
- If P = NP: public-key cryptography impossible, optimisation, learning and short proofs become easy (Fortnow, CACM 2009, "What if P = NP?"); P = NP would not guarantee practical algorithms (same), hence the caveat in the caption.
- Sudoku counts = ways to fill the empty cells by brute force: 9x9 with 55 empty 9^55 = 10^52.5; 16x16 with 160 empty 10^192.7; 25x25 with 400 empty 10^559.2. Atoms in the observable universe ~10^80.
- Context in the caption only: OpenAI and Anthropic (26 Oct 2026) each published a Lean-checked refutation of the Exponential Time Hypothesis; under expert review; it does not settle P vs NP.
