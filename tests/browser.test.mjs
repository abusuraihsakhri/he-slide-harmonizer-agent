import assert from "node:assert/strict";
import test from "node:test";
import { analyze, labToRgb, normalizeImageData, rgbToLab } from "../web/harmonizer.mjs";

function patch(rgb, count = 8) {
  const arr = new Uint8ClampedArray(count * 4);
  for (let i = 0; i < count; i++) {
    const v = i % 2 === 0 ? 0 : 6;
    arr.set([rgb[0] + v, rgb[1] + v, rgb[2] + v, 255], i * 4);
  }
  return arr;
}
test("RGB to CIELAB round-trip retains colors", () => {
  for (const rgb of [[255, 255, 255], [0, 0, 0], [175, 82, 142], [70, 40, 140]]) {
    const converted = labToRgb(...rgbToLab(...rgb));
    converted.forEach((value, i) => assert.ok(Math.abs(value - rgb[i]) <= 1));
  }
});
test("reject empty and white-only inputs", () => {
  assert.throws(() => analyze(new Uint8ClampedArray([255, 255, 255, 255])), /tissue/);
  assert.throws(() => analyze(new Uint8ClampedArray(3)), /RGBA/);
});
test("zero strength leaves image colors unchanged", () => {
  const input = patch([150, 70, 125]);
  const reference = patch([110, 75, 95]);
  const result = normalizeImageData(input, reference, 0);
  for (let i = 0; i < input.length; i++) assert.ok(Math.abs(result.pixels[i] - input[i]) <= 1);
});
test("reference normalization changes mean toward target", () => {
  const src = patch([194, 145, 160]);
  const ref = patch([150, 85, 125]);
  const result = normalizeImageData(src, ref, 1);
  const distance = (a, b) => a.reduce((sum, v, i) => sum + (v - b[i]) ** 2, 0);
  assert.ok(distance(result.output.mean, result.reference.mean) < distance(result.source.mean, result.reference.mean));
});
test("white background and alpha are not recolored", () => {
  const src = new Uint8ClampedArray([...patch([140, 82, 114]), 255, 255, 255, 255, 10, 20, 30, 0]);
  const result = normalizeImageData(src, patch([205, 140, 160]), 1);
  assert.deepEqual(Array.from(result.pixels.slice(-8)), [255, 255, 255, 255, 10, 20, 30, 0]);
});
test("strength outside unit interval is rejected", () => {
  assert.throws(() => normalizeImageData(patch([130, 70, 120]), patch([175, 90, 150]), 2), /Strength/);
});
