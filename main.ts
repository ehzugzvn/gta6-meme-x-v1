// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is the X post named by POST.json; this program's only
// job is to hand that file to the grader: it reads POST.json from
// MAKEFUN_BOT_DIR (default /bot), checks that it parses as JSON with a
// string `url`, and copies it byte for byte to MAKEFUN_OUTPUT_DIR
// (default /output). Deterministic: no network, no clock, no randomness.
//
// Local check:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const SOURCE = join(BOT_DIR, 'POST.json');
const TARGET = join(OUTPUT_DIR, 'POST.json');

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

// Read and validate POST.json before copying anything.
let raw: string;
try {
  raw = readFileSync(SOURCE, 'utf8');
} catch (err) {
  fail(`cannot read ${SOURCE}: ${(err as Error).message}`);
}

let parsed: unknown;
try {
  parsed = JSON.parse(raw!);
} catch (err) {
  fail(`POST.json is not valid JSON: ${(err as Error).message}`);
}

if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
  fail('POST.json must be a JSON object with a non-empty string "url"');
}
const url = (parsed as { url?: unknown }).url;
if (typeof url !== 'string' || url.trim().length === 0) {
  fail('POST.json must be a JSON object with a non-empty string "url"');
}

// Create the output directory only after validation has passed, so a
// bad POST.json never leaves a stray partial hand-off behind.
mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(SOURCE, TARGET);
} catch (err) {
  fail(`cannot copy POST.json to ${TARGET}: ${(err as Error).message}`);
}
