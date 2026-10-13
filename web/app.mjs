import { normalizeImageData } from "./harmonizer.mjs";

const byId = id => document.getElementById(id);
const sourceInput = byId("sourceFile"), referenceInput = byId("referenceFile");
const processButton = byId("processBtn"), demoButton = byId("demoBtn");
const downloadButton = byId("downloadBtn"), strengthSlider = byId("strength");
const status = byId("status"), metrics = byId("metrics");
const canvasFor = kind => byId(kind + "Canvas");
const state = { source: null, reference: null, output: null, busy: false };

function report(message) { status.textContent = message; }
function render(kind, data) {
  const canvas = canvasFor(kind);
  canvas.width = data.width; canvas.height = data.height;
  canvas.getContext("2d", { willReadFrequently: true }).putImageData(data, 0, 0);
}
function clearOutput() {
  state.output = null; downloadButton.disabled = true;
  const canvas = canvasFor("output");
  canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
  metrics.textContent = "No image processed.";
}
function updateReady() {
  processButton.disabled = state.busy || !state.source || !state.reference;
}
async function decodeImage(file) {
  if (!["image/png", "image/jpeg", "image/webp"].includes(file.type)) {
    throw new Error("Unsupported image format; use PNG, JPEG, or WebP");
  }
  if (file.size > 20 * 1024 * 1024) throw new Error("Image exceeds the 20 MB file limit");
  let bitmap;
  try {
    bitmap = await createImageBitmap(file);
    const scale = Math.min(1, 1400 / Math.max(bitmap.width, bitmap.height));
    const width = Math.max(1, Math.round(bitmap.width * scale));
    const height = Math.max(1, Math.round(bitmap.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width; canvas.height = height;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(bitmap, 0, 0, width, height);
    return ctx.getImageData(0, 0, width, height);
  } finally { bitmap?.close(); }
}
function setImage(kind, data) {
  state[kind] = data;
  render(kind, data);
  clearOutput(); updateReady();
  report("Images ready. Select Normalize image.");
}
async function onUpload(kind, file) {
  if (!file) { state[kind] = null; clearOutput(); updateReady(); return; }
  state[kind] = null; clearOutput(); updateReady();
  report("Reading " + kind + " image...");
  try {
    setImage(kind, await decodeImage(file));
  } catch (error) {
    report(kind + ": " + error.message);
    updateReady();
  }
}
sourceInput.addEventListener("change", () => onUpload("source", sourceInput.files?.[0]));
referenceInput.addEventListener("change", () => onUpload("reference", referenceInput.files?.[0]));
strengthSlider.addEventListener("input", () => {
  byId("strengthValue").textContent = strengthSlider.value + "%";
  if (state.output) { clearOutput(); report("Strength changed. Normalize again to update."); }
});
processButton.addEventListener("click", async () => {
  if (!state.source || !state.reference || state.busy) return;
  state.busy = true; updateReady(); demoButton.disabled = true;
  report("Normalizing tissue colors locally...");
  await new Promise(resolve => requestAnimationFrame(resolve));
  try {
    const result = normalizeImageData(
      state.source.data, state.reference.data, Number(strengthSlider.value) / 100
    );
    const output = new ImageData(result.pixels, state.source.width, state.source.height);
    render("output", output);
    state.output = output; downloadButton.disabled = false;
    const fmt = arr => arr.map(x => x.toFixed(2)).join(", ");
    metrics.textContent = [
      "Input tissue pixels: " + result.source.count,
      "Reference tissue pixels: " + result.reference.count,
      "Input mean [L*, a*, b*]: " + fmt(result.source.mean),
      "Reference mean [L*, a*, b*]: " + fmt(result.reference.mean),
      "Output mean [L*, a*, b*]: " + fmt(result.output.mean),
      "Output resolution: " + output.width + " x " + output.height + " pixels"
    ].join("\n");
    report("Normalization complete. Export the processed patch as PNG.");
  } catch (error) {
    clearOutput();
    report("Processing error: " + error.message);
  } finally { state.busy = false; updateReady(); demoButton.disabled = false; }
});
downloadButton.addEventListener("click", () => {
  if (!state.output) return;
  canvasFor("output").toBlob(blob => {
    if (!blob) { report("PNG encoding failed"); return; }
    const url = URL.createObjectURL(blob), link = document.createElement("a");
    link.href = url; link.download = "he-harmonized-preview.png";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }, "image/png");
});
function syntheticPatch(reference) {
  const width = 360, height = 250;
  const pixels = new Uint8ClampedArray(width * height * 4);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const i = 4 * (y * width + x);
    const h = (Math.sin(x * 0.14 + y * 0.09) + Math.cos(y * 0.18)) / 2;
    const e = (Math.sin(x * 0.06 - y * 0.15) + Math.cos(x * 0.23)) / 2;
    const tissue = x > 12 && y > 12 && x < width - 12 && y < height - 12;
    if (tissue) {
      pixels[i] = Math.max(10, Math.min(255, (reference ? 203 : 229) + h * 31 + e * 15));
      pixels[i + 1] = Math.max(10, Math.min(255, (reference ? 148 : 165) + h * 22 + e * 12));
      pixels[i + 2] = Math.max(10, Math.min(255, (reference ? 187 : 203) + h * 26 + e * 9));
    } else {
      pixels[i] = pixels[i + 1] = pixels[i + 2] = 255;
    }
    pixels[i + 3] = 255;
  }
  return new ImageData(pixels, width, height);
}
demoButton.addEventListener("click", () => {
  if (state.busy) return;
  sourceInput.value = ""; referenceInput.value = "";
  state.source = syntheticPatch(false); state.reference = syntheticPatch(true);
  render("source", state.source); render("reference", state.reference);
  clearOutput(); updateReady();
  report("Synthetic examples loaded (not clinical images). Choose Normalize image.");
});
