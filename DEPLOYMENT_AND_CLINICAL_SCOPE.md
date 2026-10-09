# Deployment and clinical scope — version 0.2

## Separate phone-accessible Streamlit app

In Streamlit Community Cloud, create a new app from the existing repository:

| Setting | Value |
|---|---|
| Repository | `neilrewal1-commits/TMB_Prediction` |
| Branch | `prototype/integrated-report-demo` |
| Main file | `cloud/app.py` |
| Python version (Advanced settings) | `3.12` |
| Secrets | None required for this public/simulated-data demo |

The `cloud/requirements.txt` file contains the tested dependencies. Community Cloud checks the entry point's directory before the repository root, so the original app's dependencies remain separate. Do not deploy the root `prototype.py` entry on Community Cloud with the existing root requirements. Do not replace the original app or merge merely to deploy this branch.

Source: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

Deployment was attempted on 2026-10-08. GitHub's browser sign-in returned a 500 error before Streamlit access was confirmed. A live URL has not been established. The code and deployment configuration are ready; a successful Community Cloud sign-in and deployment are still required. A GitHub PR URL is not a live app URL.

After deploying, verify that the landing page loads, all three demo cases run, report uploads work, and the new clinical scenarios produce IIA, IIIA and IV. On a phone, expand the sidebar to choose a patient and evidence mode; scroll the tab row to reach Staging & treatment. Mobile layout has not yet been visually verified on a hosted deployment.

## What changed

The new **4 · Staging & treatment** tab adds two deterministic, experimental capabilities:

1. Calculate an AJCC 8 pathological gastric stage group from human-confirmed invasion depth, positive/examined regional node counts and M category. It does not copy the historical stage label.
2. Match selected treatment discussion pathways to current setting, adult age, clinician-assessed fitness, biomarker results and immunotherapy risk review.

These are not validated clinical decisions. A rules-engine test suite is not a clinical validation study. The app does not independently interpret scans, establish a diagnosis, prescribe, dose medicines, rank options or estimate survival.

## Assessment inputs and provenance

Clinical assessment inputs are entered and reviewed explicitly. The app does not automatically transfer historical report values into current staging or treatment logic. The source/date field and episode confirmation are required; they are human assertions, not automated verification. Automatic reconciliation of reports, dates and treatment episodes remains future work.

In simulated-extension mode, **Load fictional clinical scenario** creates a separate illustrative assessment. Every clinical field in that scenario is fictional, including fitness and immune-risk review. These scenarios are not claims about the three TCGA individuals. Existing clinical records retain their historical AJCC 7 labels; the independent scenarios use AJCC 8. Never show the scenario result as a corrected stage for the real research patient.

Changing any assessment input requires confirmation again and clears the prior result. Case/mode changes clear the workspace. Exports retain provenance, rule version, blockers and source links.

## Implemented scope

| Capability | Included | Not included |
|---|---|---|
| Staging | Gastric adenocarcinoma under the stomach schema; AJCC 8 pathological groups; no neoadjuvant therapy | Clinical cTNM, ypTNM, automated GEJ schema selection, other cancers, scan interpretation |
| Postoperative pathways | Broad chemotherapy and chemoradiation discussion for calculated stage II/III | Choosing between those options; margin, D2 dissection or radiation planning algorithms |
| Perioperative pathway | Durvalumab + FLOT discussion for an explicitly entered adult, resectable, untreated context with fitness/immune review | Clinical staging, operative eligibility, dosing; an adjuvant-only substitute |
| Advanced first line | HER2-positive / CPS ≥1 pembrolizumab–trastuzumab–chemotherapy; HER2-negative / CLDN18.2-positive zolbetuximab–chemotherapy; general systemic and symptom-control discussions | Exhaustive biomarker algorithms, all HER2-negative PD-L1 options, later-line sequencing, MSI-specific regimen selection |

An absent option is not evidence that a patient is ineligible. A matching card is not evidence that a patient should receive it. Autoimmune disease/transplant concerns withhold immune-combination matching for review; they are not treated as universal contraindications. Age, weight, albumin, NLR and the research TMB category cannot independently select a therapy.

The FDA approval notices below are evidence snapshots, not a substitute for reviewing current full labels before clinical use. Source links and rule version are visible in the app. These sources were checked on 2026-10-08; this is not a comprehensive guideline update service.

## Evidence

- AJCC 8 pathological group mapping and broad treatment context: https://www.cancer.gov/types/stomach/hp/stomach-treatment-pdq
- HER2-positive/CPS ≥1 combination, FDA 2025-03-19: https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-pembrolizumab-her2-positive-gastric-or-gastroesophageal-junction-adenocarcinoma
- CLDN18.2-positive/HER2-negative combination, FDA 2024-10-18: https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-zolbetuximab-clzb-chemotherapy-gastric-or-gastroesophageal-junction-adenocarcinoma
- Perioperative durvalumab/FLOT, FDA 2025-11-25: https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-durvalumab-resectable-gastric-or-gastroesophageal-junction-adenocarcinoma

## Verification

21 automated tests pass. They cover original upload/model behavior plus selected AJCC reference groups, N-category boundaries, wrong-system and unknown-input rejection, biomarker gates, fitness and episode gates, treatment-setting distinctions, three UI clinical scenarios, and stale-output clearing. The deployment entry point is tested through Streamlit AppTest. No oncologist review or prospective clinical validation has occurred.
