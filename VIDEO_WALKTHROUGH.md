# Three-minute demonstration outline

This script describes the implemented prototype, with the full clinical vision identified as future work. Version 0.2 adds the experimental staging/pathway demonstration described below; distinguish it from clinical validation. Timing is approximate; rehearse against the actual screen recording. Contest-specific video requirements have not been verified in this document.

| Time | Screen action | Suggested narration |
|---|---|---|
| 0:00–0:20 | App title and three stages | “Cancer care involves many kinds of information, but patients often receive them in separate reports. My vision is an app that connects genomic, imaging and clinical evidence to support personalized cancer care.” |
| 0:20–0:45 | Patient A, gene CSV, model output | “I started with my own research: a 50-gene model that predicts a high or low mutation-burden category in stomach cancer. Here the original model is running. This study category is different from a clinical TMB measurement.” |
| 0:45–1:15 | Add A's reconstructed clinical summary, then upload its simulated radiology TXT | “I extended that starting point into a report workflow. This summary uses public TCGA research data. The radiology report is explicitly simulated because I have not established a matched original report. The app shows its source and asks me to review what was extracted.” |
| 1:15–1:40 | Upload A's simulated lab report; show combined view | “As I add clinical information, the combined view changes. Every finding has a source, and missing information stays visible. These laboratory values are also simulated; they are not measurements from this research patient.” |
| 1:40–2:00 | Brief prerecorded B walkthrough and combined view | “The second case has a different study-model result and a different clinical context. This illustrates why one genomic result cannot describe the whole patient. Clinical treatment selection is the next model-development step.” |
| 2:00–2:20 | Brief prerecorded C walkthrough; missing values | “The third case has an advanced historical cancer stage but a low mutation-burden study category. Stage and mutation burden describe different things. Here missing lab inputs also prevent the profile from being ready for the additional research model.” |
| 2:20–2:40 | Sources and unknowns; summary download | “The prototype already combines a working research model with source-traceable reports and three patient workflows. It does not independently diagnose, assign stage or prescribe treatment. Those capabilities need separate development and validation.” |
| 2:40–3:00 | Full-vision caption | “My next step is to work with oncologists to evaluate the workflow, select and validate the next clinical models, and develop understandable treatment comparisons. The goal is to make complex cancer information easier to use in personalized care.” |

Use screen recordings of the real app. Keep simulated-data labels visible. Do not present speeded-up or prerecorded case transitions as model performance measurements. Do not call internal test accuracy clinical accuracy, or a doctor's opinion clinical validation.

## Recording checklist

- Run `prototype.py` with the pinned prototype requirements.
- Download each case's example files before recording so the file chooser is ready.
- Use the simulated-extension mode for the complete workflow.
- Record each case separately: switching cases intentionally clears the workspace.
- Show source review and the combined view; avoid spending most of the video on CSV columns.
- Check the current Congressional App Challenge rules before final export and submission.

## Oncologist feedback to request

1. Are the distinctions between study TMB category, measured TMB and cancer stage clear?
2. What information is missing before a clinician could compare treatment options?
3. Are the fictional extensions medically coherent enough for an educational demonstration?
4. Does the source-review and uncertainty display help, and where could it mislead?
5. Which narrowly defined clinical task should we validate first within the full vision?

Record feedback accurately and obtain permission before using a clinician's name, image or quotation. Ask for a review of this specific prototype; do not imply endorsement of clinical effectiveness.

## Version 0.2 clinical demonstration update

At 1:40–2:20, show **4 · Staging & treatment**, load a fictional clinical scenario, review its inputs and confirm. Explain: “This next module calculates an AJCC 8 pathological stage from confirmed findings rather than copying a stage label. It then matches selected treatment discussion options to the entered setting and biomarkers. These clinical scenarios are fictional, the rule coverage is limited, and an oncologist has not validated the app.”

For the final 40 seconds, replace claims that staging and pathways are wholly unimplemented with: “The prototype now includes experimental staging and treatment-pathway rules. It does not interpret scan images or prescribe treatment. Clinical validation and broader coverage are the next steps.” Keep the original report sources and fictional clinical scenario visually distinct.
