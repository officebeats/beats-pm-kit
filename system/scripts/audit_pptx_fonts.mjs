#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import path from "node:path";

function usage() {
  console.error("Usage: audit_pptx_fonts.mjs <deck.pptx> --expected <Font Name>[,<Font Name>...]");
  process.exit(2);
}

const args = process.argv.slice(2);
const pptx = args[0];
const expectedIndex = args.indexOf("--expected");
if (!pptx || expectedIndex === -1 || !args[expectedIndex + 1]) {
  usage();
}

const expectedFonts = new Set(args[expectedIndex + 1].split(",").map((font) => font.trim()).filter(Boolean));
if (expectedFonts.size === 0) {
  usage();
}

function run(cmd, cmdArgs) {
  const result = spawnSync(cmd, cmdArgs, { encoding: "utf8", stdio: "pipe" });
  if (result.status !== 0) {
    throw new Error([`Command failed: ${cmd} ${cmdArgs.join(" ")}`, result.stdout, result.stderr].filter(Boolean).join("\n"));
  }
  return result.stdout;
}

const files = run("unzip", ["-Z1", pptx])
  .split(/\r?\n/)
  .filter((file) => file.endsWith(".xml") && file !== "[Content_Types].xml");

const seen = new Map();
const typefacePattern = /typeface="([^"]+)"/g;

for (const file of files) {
  const xml = run("unzip", ["-p", pptx, file]);
  for (const match of xml.matchAll(typefacePattern)) {
    const font = match[1];
    if (!seen.has(font)) {
      seen.set(font, new Set());
    }
    seen.get(font).add(file);
  }
}

const unexpected = [...seen.keys()].filter((font) => !expectedFonts.has(font)).sort();
if (unexpected.length > 0) {
  console.error(`Font audit failed for ${path.basename(pptx)}.`);
  console.error(`Expected: ${[...expectedFonts].join(", ")}`);
  for (const font of unexpected) {
    const sampleFiles = [...seen.get(font)].slice(0, 8).join(", ");
    console.error(`Unexpected font "${font}" in ${seen.get(font).size} XML file(s): ${sampleFiles}`);
  }
  process.exit(1);
}

console.log(`Font audit passed for ${path.basename(pptx)}: ${[...seen.keys()].sort().join(", ") || "no explicit fonts found"}`);
