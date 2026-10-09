# TMB_Prediction
Identifies Low and High TMB from Tumor Mutation Data

## Integrated research prototype

The separate `prototype.py` entry point combines the original TMB model with
reviewed report uploads and three public research cases with optional, explicitly
simulated radiology and laboratory extensions.

See [setup and data provenance](PROTOTYPE.md) and the
[three-minute video walkthrough](VIDEO_WALKTHROUGH.md).

```bash
python -m pip install -r requirements-prototype.txt
streamlit run prototype.py
```

Use Python 3.12 in a fresh virtual environment. Version 0.2 adds experimental
AJCC 8 pathological gastric staging from reviewed findings and treatment-pathway
matching. It does not diagnose from scans or prescribe treatment.

For a separate Community Cloud deployment, use branch
`prototype/integrated-report-demo`, entry point `cloud/app.py`, and Python 3.12.
See [deployment and clinical scope](DEPLOYMENT_AND_CLINICAL_SCOPE.md).
