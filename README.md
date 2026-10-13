# H&E Slide Harmonizer Agent

A research-oriented repository containing **two separate workflows**: a client-side H&E image-patch color normalization preview and Python numeric-rule audit demonstrations. The source code does **not** implement scanner-specific WSI import, Macenko/Vahadane stain-vector estimation, or a clinically validated stain-normalization pipeline.

## Browser image harmonization

Open the locally served page at `web/index.html`, upload an input image and a reference H&E image, select a normalization strength, and export a normalized PNG. A synthetic demo is provided for exploration.

The browser uses tissue-pixel **CIELAB mean/variance matching (Reinhard-style normalization)** and leaves near-white background unchanged. Input images are downsampled to a maximum of 1400 pixels on the longest side. Only PNG, JPEG and WebP raster images are supported, at most 20 MB each. The algorithm is a visual color-matching baseline: it does not perform stain unmixing, quantitative calibration, WSI tiling, DICOM decoding or morphology preservation validation.

All browser image processing happens locally. Images are not transmitted to the repository's Python API, and the browser application does not require a backend. Do not use the demo as evidence of scanner harmonization or for diagnostic decisions.

To run locally:

```bash
python -m http.server 8080 --directory web
```

Open http://localhost:8080 in a modern browser with JavaScript modules, Canvas and `createImageBitmap` support. Opening the HTML directly via `file://` may block module imports.

## Python audit demonstration

The Python CLI and FastAPI endpoints evaluate **numeric task metrics** against hard-coded demonstration thresholds and produce task dossiers. These heuristics are not derived from CAP H&E stain-calibration standards and are not diagnostic recommendations. The CLI/API are independent of the browser's image normalization.

Requires Python 3.9+; CI covers Python 3.10, 3.12 and 3.13.

```bash
python -m pip install -e ".[api,test]"
he-slide-harmonizer-agent audit --task-id TASK-001 --primary 28.5 --secondary 14.2
he-slide-harmonizer-agent batch -i sample.csv -o results.csv
he-slide-harmonizer-agent verify-audit
he-slide-harmonizer-agent serve --host 127.0.0.1 --port 8000
```

The CLI uses `cli.py` and the FastAPI application at `agents.api:app`. Its main routes are `/health`, `/api/audit`, `/api/chat`, `/metrics` (JSON), and `/api/audit/logs`. The older `he-slide-harmonizer-engine` command is also retained for compatibility with `he_slide_harmonizer_agent.cli`; the two CLIs have different payload schemas.

The CLI batch command reads a CSV with fields such as `task_id`, `target_identifier`, `primary_metric`, `secondary_metric`, `status_descriptor`, and `is_critical_flag` (explicit true/false values). The bundled `sample.csv` also works: `case_id`, `patient_synthetic_id`, `metric_primary`, `metric_secondary`, `status_flag`, and `is_stat` are recognized as aliases. Input and output paths must remain inside the current working directory.

For container use:

```bash
docker compose up --build
```

Optional `AUDIT_SECRET_KEY` can be supplied via your environment for a stable signing key. No production key is embedded. Audit logs are held in memory and **are not persistent**. The HMAC chain detects modifications to signed log entries, but it is not an external immutable ledger. There is no persistent database or authentication layer; do not expose the API on an untrusted network.

## Tests

```bash
python -m pytest -q
node --test tests/browser.test.mjs
```

The GitHub Actions workflow also verifies package installation, Python compilation, CLI entry points, and browser JavaScript syntax before attempting a Pages deployment from `web/`.

## Privacy and scope

The browser keeps raster images on the local device. The Python service processes request metadata in memory; its pattern-based identifier detector is incomplete and does **not** establish HIPAA compliance. Do not submit real patient information to publicly hosted services. No hosted LLM is used by the default CLI. Browser-Python runtimes such as Pyodide are not required; the image preview runs in standard JavaScript.

## Technology and license

Python, Pydantic v2, optional FastAPI/Uvicorn, vanilla JavaScript, Canvas API, and CIELAB color transforms. Licensed under [MIT](LICENSE).
