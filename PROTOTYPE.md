# Cancer Care research prototype

The main entry point now opens a five-page navigation shell. The complete
workflow documented below is preserved on the final **Full research workspace**
page (`integrated_report.py`). See README.md for the new image, nearby-center
and community pages, Streamlit secrets, and their separate session/storage scope.

This is a working first increment of Neil Rewal's vision: combine genomic, imaging, pathology, laboratory and patient-history evidence to support personalized cancer care. The current build runs Neil's existing TMB research model and implements the report-upload and evidence-review workflow. Version 0.3 also adds an experimental pathological staging calculator and selected treatment-pathway matching; see `DEPLOYMENT_AND_CLINICAL_SCOPE.md` for the implemented boundaries. Diagnosis inference and validated clinical decision-making remain future work.

## Run locally

Use Python 3.12, starting from this branch:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-prototype.txt
streamlit run prototype.py
```

On Windows, activate with `.venv\Scripts\activate`.

The separate `prototype.py` entry point is for public research and simulated cases. It does not require the original app's Google authentication configuration. `Login.py` and its authentication remain unchanged. Do not upload private medical records to this build. The original deployment's `requirements.txt` is unchanged; use the prototype requirements for this entry point. The final research workspace needs no external API; the new image and nearby-center pages require an OpenAI API key in Streamlit secrets and incur charges when explicitly used.

## What works now

| Step | Input | What the user sees |
|---|---|---|
| 1. Genomics | One-row CSV with the exact 50 gene names and binary values | Validated, correctly ordered features and the original model's high/low study category |
| 2. Imaging and pathology | Text-based PDF or TXT | Source text, suggestions for explicitly labeled fields, editable values with supporting passages, documented diagnosis/stage and imaging findings |
| 3. Labs and history | Text-based PDF or TXT | Reviewed age, weight, albumin, NLR, measured TMB, prior therapy and other history when present |
| Combined view | Confirmed reports | Source-linked facts, missing inputs, conflicting evidence, a change history and downloadable summary |

The report reader recognizes a small set of `Label: value` fields. It does not interpret arbitrary medical prose, analyze images or infer a diagnosis. Users can add a supported field manually and must supply an exact passage and page. This manual review does not constitute clinical validation. PDF uploads are limited to 5 MB and 30 pages; scanned images need an OCR capability that is not implemented.

Changing patient or evidence mode clears the workspace. Removing a report recalculates the combined view. Explicit case-ID mismatches are rejected. Reports without a supported `Case ID:` label require human identity confirmation; this is not a general patient-identity matching system. The app does not maintain a longitudinal database, distinguish new disease progression from older staging, or resolve competing reports automatically. Conflicting values are excluded from structured research inputs.

## Three-case demonstration

Choose **Public case + explicitly simulated extension** to show all three stages. For each case:

1. Load its gene CSV, confirm the case and feature information, and run the model.
2. Load its reconstructed clinical summary, inspect the source and extracted fields, confirm, and add it.
3. Select its simulated radiology report in the imaging tab, review, confirm, and add it.
4. Load its simulated lab report in the labs tab, review, confirm, and add it.
5. Open the combined view and download the summary.

To record an actual upload, first use **Download example report**, then select that file with the upload control. The load-example button passes the same bytes through the report reader.

| Case | Real historical pathology stage | Experimental model result | Simulated extension demonstrates |
|---|---|---|---|
| A: TCGA-VQ-A8DL | IIA, AJCC 7th edition | Low study category | A more complete clinical profile, with all six LORIS input fields populated |
| B: TCGA-VQ-A8DU | IIIA, AJCC 7th edition | High study category | Different imaging and laboratory context despite the same fictional measured TMB as A |
| C: TCGA-VQ-A8DZ | IV, AJCC 7th edition | Low study category | Advanced historical stage does not imply a high mutation category; missing research inputs prevent readiness |

These are demonstrations, not independent model-validation cases. Historical pathology stages were imported from public research data; the app did not calculate them. All added radiology and laboratory narratives are fictional and remain labeled in the UI and exports. They are not claimed to belong to the underlying TCGA individuals and have not been clinically reviewed for coherence. This demo does not show three fully matched, real clinical histories.

## Research integrity and source data

- The original model predicts a category defined using the training cohort's median nonsynonymous mutation count. It does not output clinical TMB in mutations/Mb, tumor volume, cancer stage or treatment benefit.
- The fixed pickle was trained with scikit-learn 1.6.1. The prototype pins that version and loads only that repository file; uploaded model files are never executed.
- Gene order comes from the approved training and testing CSV headers. The serialized model does not retain gene names. The original sample upload had `DNAH9` where `MUC6` was required, plus reordered columns. The new validator rejects that sample and safely reorders a correct gene set. Unknown genes cannot be silently filled with zero.
- Original research test data reproduced 68/87 correct predictions (78.16%) with the pinned runtime. This is a reproduction of the original internal test, not new clinical validation. Source notebooks and private Drive files are not copied into this branch.
- The three demonstration gene vectors were derived from current open GDC masked somatic MAF files using the study's nonsynonymous variant categories. This mapping is experimental; equivalence to the original variant-calling pipeline is not established. Model-development overlap is possible.
- The reconstructed clinical TXT files use TCIA's historical TCGA-STAD clinical metadata and GDC diagnosis metadata. They are not original medical reports. Original pathology PDFs were located and successfully read during development, but are not redistributed here.
- CT metadata exists for the selected cases. CT pixels have not been downloaded or interpreted, and original written radiology reports and matched blood reports have not been established.
- See `demo_data/source_manifest.json` for file IDs, source hashes and derived-input hashes. The TCGA/GDC research participants and contributing researchers made these public resources possible.

Primary sources: [TCIA TCGA-STAD](https://www.cancerimagingarchive.net/collection/tcga-stad/), [GDC](https://portal.gdc.cancer.gov/), [LORIS repository](https://github.com/rootchang/LORIS), [NCI LORIS](https://loris.ccr.cancer.gov/), [NCI stomach cancer treatment](https://www.cancer.gov/types/stomach/treatment/by-stage).

## LORIS and further clinical development

The current UI checks whether diagnosis, age, albumin, NLR, measured TMB and prior systemic-therapy information are present and suitably formatted. It does not map free text into a cancer category or issue a LORIS score. The original research model's binary output cannot replace measured TMB.

The LORIS repository and NCI web calculator expose different coefficients. The website also distinguishes its logistic score from its mapped response-rate estimate. Version selection, score calibration, intended population, licensing and clinical review must be resolved before integrating a prediction. No LORIS source implementation is bundled in this branch.

The broader app can develop toward clinically validated diagnosis, staging and treatment support. Beyond the version 0.3 rules described in `DEPLOYMENT_AND_CLINICAL_SCOPE.md`, the next clinical increment needs a defined cancer-specific scope for validation, a reviewed staging schema, structured biomarker and treatment-history inputs, guideline-linked treatment alternatives, and an evaluation set independent of training. Starting validation with gastric cancer follows the current research base; it does not limit the eventual multi-cancer vision.

Before accepting real clinical records, the app also needs authentication for this entry point, secure storage and deletion, access controls, a privacy review, robust patient/date reconciliation and deployment monitoring. This branch is a prototype, not a production clinical product.

## Verification

```bash
python -m unittest discover -s tests -v
```

Tests cover incorrect gene schemas, reordered inputs, invalid values, malformed rows, expected research predictions, patient-ID mismatches, absence of invented prose extraction, source conflicts, duplicate reports, units, missing LORIS inputs, export labeling, and all three Streamlit walkthroughs with workspace reset. Actual upload parsing is exercised separately from the Streamlit file chooser; AppTest does not emulate the operating-system upload dialog.

See `VIDEO_WALKTHROUGH.md` for a three-minute recording outline and suggested oncologist review questions.
