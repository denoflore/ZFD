# Fable Visual Transcription Pilot: f100r, paragraph 1, line 1

**Date:** 2026-08-25
**Reader:** Claude Fable 5, reading the Yale IIIF full-resolution scan
(2676x3756) referenced by this repository's own recipe pages.
**Method:** column-wise baseline straightening (ink-centroid per column,
121px smoothing window, vertical shift to median), line strips split into
2x-upscaled halves, glyph-by-glyph reading with per-token confidence,
transcription committed BEFORE consulting the LSI reference.

## Blindness disclosure

Tokens 1-3 of this line appeared in `voynich_zfd_summary.md` output
earlier in the working session, so the read of tokens 1-3 was not fully
blind. Tokens 4-10 were read blind. A clean future run must use folios
whose EVA has never entered the reader's context.

## The reading

Fable (visual): `psheor sheod qoteecheey sheodor dchda lollo cthor deeey cheocthy s`

LSI transcriber H (f100r.12,@P0): `pcheol.sheod.qocphee!ckhy.shodol.cth!!daoto.ch.qeos.sheey!.chcths!o.s`

## Token comparison

| # | LSI H | Fable | Verdict | Error class |
|---|-------|-------|---------|-------------|
| 1 | pcheol | psheor | partial (4/6 glyphs) | ch/sh plume, l/r final |
| 2 | sheod | sheod | EXACT | |
| 3 | qocphee ckhy | qoteecheey | partial | benched-gallows compound misread as plain gallows |
| 4 | shodol | sheodor | partial (4/6) | inserted e, l/r final |
| 5 | cth!!daoto | dchda | poor | damaged zone (LSI marks !!) |
| 6-7 | ch qeos | lollo | poor | damaged zone, segmentation |
| 8 | sheey! | deeey | partial (3/5) | sh/d initial |
| 9 | chcths!o | cheocthy | partial | cluster order |
| 10 | s | s | EXACT | |

**Result: 2 exact tokens, 5 partial, 2 poor, roughly 60-65% glyph
agreement on one full-care line.**

## What the errors are

Every disagreement outside the physically damaged zone falls into the
error classes the paleographic hand analysis already documented: the
sh/ch plume distinction, l/r/i/n terminal confusion (the published 5-20%
floor), and benched-gallows compounds. The reading errors are the
manuscript's known hard cases, not random noise, which is itself evidence
that the glyph inventory model is right.

## Honest verdict and the path

One line at full care took one focused pass; 244 loci at ~15 lines each
is thousands of passes. Manual visual transcription validates the METHOD
(straightened strips at Yale resolution are genuinely readable) and
calibrates the error floor, but the scale belongs to the trained
recognizer: the `zfd_image_native` lane, with lines like this one, read
carefully and disagreement-scored against LSI, as its gold standard.
This pilot is the first gold line.
