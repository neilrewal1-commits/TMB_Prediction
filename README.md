# TMB_Prediction
Identifies Low and High TMB from Tumor Mutation Data

## Integrated research prototype

**Cancer Basics** appears immediately after Support in both app views. It offers
six illustrated reading chapters: what cancer is; causes, risk and prevention;
growth and spread; diagnosis and biomarkers; treatment and daily life; and stomach
cancer. The stomach chapter covers symptoms, H. pylori and other risks, biopsy,
staging, treatment biomarkers and nutrition. Each section links to NCI or American
Cancer Society sources. Readers can jump between chapters, use Previous/Next, or
download the complete guide. The illustrations are original explanatory SVGs;
this section works without an OpenAI key or uploading patient information.


The app uses `st.navigation` and `st.Page` for its main workspaces:

1. **Gene report & TMB** — upload a PNG/JPEG/WebP report image, extract with OpenAI,
   review the 50 gene statuses and run the original random-forest classifier.
   A printed measured TMB value is transcribed separately. Missing genes remain
   unknown and block model prediction; no numeric TMB is calculated from the image.
2. **Radiology review** — upload multiple PDF reports and/or PNG/JPEG/WebP images
   together for one combined review. Findings link to filenames and PDF pages;
   contradictions and unreadable documents remain visible. Written report screenshots
   provide documented findings; raw scans receive a limited, non-diagnostic description.
   Limits: 10 files, 10 MB per file, 30 MB combined, 30 pages per PDF and 60 total
   pages/images. Scanned PDFs are supported through native PDF input to OpenAI.
   Adding/removing a file starts a fresh combined review; ordinary reruns do not
   re-submit the same batch. Password-protected or invalid PDFs are rejected before
   an API request. Patient and Clinician views share this workflow.
3. **Patient & treatment centers** — maintain a session-only patient overview and
   search official center information near a city/postal code and country.
4. **Community** — publish an optional alias profile, find similar experiences,
   request connections and exchange messages after acceptance. Local SQLite demo
   storage is separate from uploaded reports. No profiles are pre-populated.
   Open **Support** and turn on **Connect with peers in this app** to use it.
5. **Full research workspace** — the original integrated application, including
   the three public cases, report review, experimental staging and exports.
   Use **Clinician** view to open the experimental staging and pathway tools.

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and provide
`OPENAI_API_KEY`, or set it in Streamlit Community Cloud Secrets. Never commit
your key. Optional `OPENAI_VISION_MODEL` and `OPENAI_SEARCH_MODEL` default to
`gpt-4.1-mini`. New images are sent automatically on upload, with a visible notice
above the upload control. Each image is analyzed once in its session; page reruns
do not repeat the API request. A failed attempt can be retried explicitly.
Requests use `store=False` and are not globally cached.
The center search sends location only, with live web search and clickable sources.

Image results in Patient view include an everyday-language overview, short key
points, a glossary of terms from the report, and next-step questions for the care
team. Clinician view retains precise terminology and exact source passages.
Raw scan images cannot produce diagnostic findings: the app explains the limitation
and suggests uploading the written radiology report. Authentication, quota and
timeout failures display actionable messages without exposing credentials.

Run on Python 3.12 using `requirements-prototype.txt`. The fixed original
classifier requires scikit-learn 1.6.1. The original Google-login application
remains accessible through `streamlit run Login.py`.

`COMMUNITY_DB_PATH` can point to a writable SQLite location; it defaults to
`.local/community.sqlite3`. Profiles and messages survive sessions on the same
server, but local Streamlit Cloud files are not durable across redeployments.
The generated private access code is needed to sign back in; there is no account
recovery. Users can decline/block connections or delete their profile and its
associated messages. Set `COMMUNITY_ENABLED = false` to disable the directory.
This is a single-host, unmoderated community demo, not a production patient network.
Production use needs durable storage, verified authentication, moderation and
appropriate privacy controls. Use de-identified/simulated records and fictional
community profiles for the prototype.

New image-page results are session-scoped and independent of the final page's
historical TCGA examples. Changing a saved patient alias clears those results;
changing/removing an image clears its extraction and prediction. Changing the
historical demo case does not erase the other pages or community sign-in.

Implementation references: [Streamlit navigation](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation),
[OpenAI image inputs](https://developers.openai.com/api/docs/guides/images-vision),
[structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
and [web search](https://developers.openai.com/api/docs/guides/tools-web-search).

The separate `prototype.py` entry point combines the original TMB model with
reviewed report uploads and three public research cases with optional, explicitly
simulated radiology and laboratory extensions.

See [setup and data provenance](PROTOTYPE.md) and the
[three-minute video walkthrough](VIDEO_WALKTHROUGH.md).

```bash
python -m pip install -r requirements-prototype.txt
streamlit run prototype.py
```

Use Python 3.12 in a fresh virtual environment. Version 0.3 adds experimental
AJCC 8 pathological gastric staging from reviewed findings and treatment-pathway
matching. It does not diagnose from scans or prescribe treatment.

For a separate Community Cloud deployment, use branch
`prototype/integrated-report-demo`, entry point `cloud/app.py`, and Python 3.12.
See [deployment and clinical scope](DEPLOYMENT_AND_CLINICAL_SCOPE.md).
