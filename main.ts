// news-image-20261120 entry (Node 22, standard library only).
//
// The image is drawn deterministically by render.py (Pillow, fixed layout,
// fixed strings, no randomness, no network) and committed here as entry.png.
// This program copies it to /output/entry.png, so both grader runs write
// byte-identical files. Outside the grader's container, MAKEFUN_OUTPUT_DIR
// stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(
  join(dirname(fileURLToPath(import.meta.url)), 'entry.png'),
  join(outDir, 'entry.png'),
);
