// Small-image, reference-based Reinhard normalization in CIELAB.
// This is not Macenko/Vahadane stain-vector estimation or whole-slide processing.
const DELTA = 6 / 29;
const WHITE = [0.95047, 1, 1.08883];

function linearize(value) {
  const c = value / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}
function encode(value) {
  const c = Math.max(0, Math.min(1, value));
  return Math.round(255 * (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055));
}
function f(t) { return t > DELTA ** 3 ? Math.cbrt(t) : t / (3 * DELTA ** 2) + 4 / 29; }
function finv(t) { return t > DELTA ? t ** 3 : 3 * DELTA ** 2 * (t - 4 / 29); }

export function rgbToLab(r, g, b) {
  const R = linearize(r), G = linearize(g), B = linearize(b);
  const x = (0.4124564 * R + 0.3575761 * G + 0.1804375 * B) / WHITE[0];
  const y = (0.2126729 * R + 0.7151522 * G + 0.0721750 * B) / WHITE[1];
  const z = (0.0193339 * R + 0.1191920 * G + 0.9503041 * B) / WHITE[2];
  const fx = f(x), fy = f(y), fz = f(z);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

export function labToRgb(L, a, b) {
  const fy = (L + 16) / 116, fx = fy + a / 500, fz = fy - b / 200;
  const x = WHITE[0] * finv(fx), y = WHITE[1] * finv(fy), z = WHITE[2] * finv(fz);
  return [
    encode( 3.2404542 * x - 1.5371385 * y - 0.4985314 * z),
    encode(-0.9692660 * x + 1.8760108 * y + 0.0415560 * z),
    encode( 0.0556434 * x - 0.2040259 * y + 1.0572252 * z),
  ];
}
export function isTissue(pixels, offset) {
  return pixels[offset + 3] > 0 &&
    (pixels[offset] < 235 || pixels[offset + 1] < 235 || pixels[offset + 2] < 235);
}
export function analyze(pixels) {
  if (!pixels || pixels.length % 4 !== 0) throw new Error("Invalid RGBA pixel buffer");
  const mean = [0, 0, 0], m2 = [0, 0, 0];
  let count = 0;
  for (let i = 0; i < pixels.length; i += 4) {
    if (!isTissue(pixels, i)) continue;
    count += 1;
    const lab = rgbToLab(pixels[i], pixels[i + 1], pixels[i + 2]);
    for (let j = 0; j < 3; j++) {
      const d = lab[j] - mean[j];
      mean[j] += d / count;
      m2[j] += d * (lab[j] - mean[j]);
    }
  }
  if (!count) throw new Error("No stained tissue detected; choose a non-white image");
  return { count, mean, std: m2.map(v => Math.sqrt(v / count)) };
}
export function normalizeImageData(source, reference, strength = 1) {
  if (!Number.isFinite(strength) || strength < 0 || strength > 1) {
    throw new Error("Strength must be between 0 and 1");
  }
  const src = analyze(source), ref = analyze(reference);
  const out = new Uint8ClampedArray(source);
  if (strength === 0) return { pixels: out, source: src, reference: ref, output: src };
  const scales = src.std.map((s, i) =>
    Math.max(0.25, Math.min(4, ref.std[i] / Math.max(s, 1e-6))));
  for (let i = 0; i < source.length; i += 4) {
    if (!isTissue(source, i)) continue;
    const lab = rgbToLab(source[i], source[i + 1], source[i + 2]);
    const target = lab.map((v, j) =>
      v + strength * ((v - src.mean[j]) * scales[j] + ref.mean[j] - v));
    const rgb = labToRgb(target[0], target[1], target[2]);
    out[i] = rgb[0]; out[i + 1] = rgb[1]; out[i + 2] = rgb[2];
  }
  return { pixels: out, source: src, reference: ref, output: analyze(out) };
}
