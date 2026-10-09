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

Use Python 3.12 in a fresh virtual environment. This is an educational prototype;
independent staging and personalized treatment selection are future work.
