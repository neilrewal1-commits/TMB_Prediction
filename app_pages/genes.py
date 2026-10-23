import json

import pandas as pd
import streamlit as st

from care_app.ai import extract_genes
from care_app.model import STATUSES, predict, reviewed_features
from care_app.state import fingerprint
from care_app.ui import auto_analyze, clinician, header, image_input, patient_explanation, status_card, words
from prototype_core import GENES, ROOT, genomic_csv

st.caption('STEP 1 OF 4 · GENE REPORT & TMB')
header('My research. Your starting point.', 'Gene Report & TMB · Research model')
st.html("""<section class="gene-research">
<span class="gene-eyebrow">NEIL’S ORIGINAL RESEARCH</span>
<h2>Could a small set of genes help reveal a bigger picture?</h2>
<p>I studied mutation patterns in stomach cancer and used a Random Forest model
 to predict high or low tumor mutation burden from 50 gene features.</p>
<div class="gene-stats"><div><strong>183,107</strong><span>mutation records</span></div>
<div><strong>431</strong><span>tumor samples</span></div>
<div><strong>50</strong><span>gene features</span></div></div>
<p class="gene-relevance">Why TMB? It is one clue doctors can use when considering immunotherapy.</p>
</section>""")
with st.expander('How the research works'):
    st.write('Source: cBioPortal / TCGA stomach adenocarcinoma data. Each gene is represented by a mutation-present or mutation-absent feature. The app runs the saved 50-tree Random Forest model.')
    st.write('The labels are study-defined high and low mutation-burden groups, not measured clinical TMB in mutations/Mb. These public cases demonstrate the model; they are not an independent validation set.')
    st.page_link(str(ROOT / 'app_pages/about_research.py'), label='MY RESEARCH & SOURCES', icon=':material/science:')
st.subheader('Try the research in action')
mode = st.radio('Choose your input', ['TRY A SAMPLE', 'UPLOAD GENE CSV', 'UPLOAD REPORT IMAGE'], horizontal=True, key='portal_gene_input_mode')
source = None
report = None
state = None
if mode == 'TRY A SAMPLE':
    st.caption('Real public research data · Choose a case, then run the model.')
    a, b = st.columns(2)
    if a.button('LOAD SAMPLE A', use_container_width=True, key='gene_sample_a'):
        st.session_state.portal_gene_sample = 'TCGA-VQ-A8DL'
    if b.button('LOAD SAMPLE B', use_container_width=True, key='gene_sample_b'):
        st.session_state.portal_gene_sample = 'TCGA-VQ-A8DU'
    case_id = st.session_state.get('portal_gene_sample')
    if case_id:
        path = ROOT / 'demo_data' / (case_id + '_genes.csv')
        source = {'name': path.name, 'bytes': path.read_bytes()}
        st.success('Sample ready: ' + case_id)
        st.download_button('DOWNLOAD SAMPLE GENE CSV', source['bytes'], path.name, 'text/csv')
elif mode == 'UPLOAD GENE CSV':
    st.caption('Upload one patient row with the 50 gene columns: 1 = mutation present, 0 = mutation absent.')
    upload = st.file_uploader('Gene feature CSV', type=['csv'], key='portal_gene_csv_' + str(st.session_state.portal_epoch), max_upload_size=5)
    if upload:
        source = {'name': upload.name, 'bytes': upload.getvalue()}
else:
    with st.container(border=True, key='care_card_gene_upload'):
        st.subheader('Upload your gene report')
        source, state = image_input('genes', words('Gene report image', 'Molecular pathology report image'))
        if source and auto_analyze('genes', source, state, extract_genes):
            st.session_state.portal_gene_rows = state['extraction']['genes']
            st.session_state.portal_gene_revision = st.session_state.get('portal_gene_revision', 0) + 1
        report = state['extraction']

if source and mode != 'UPLOAD REPORT IMAGE':
    try:
        frame = genomic_csv(source['bytes'], single_patient=True)
        digest = fingerprint([mode, source['name'], source['bytes']])
        old = st.session_state.get('portal_gene_structured')
        if old is None or old['digest'] != digest:
            rows = [{'gene': gene, 'status': 'Mutated' if int(frame.iloc[0][gene]) else 'Not mutated',
                     'evidence': source['name'] + ': ' + str(int(frame.iloc[0][gene]))} for gene in GENES]
            st.session_state.portal_gene_structured = {'digest': digest, 'prediction': None, 'rows': rows}
        state = st.session_state.portal_gene_structured
        report = {'genes': state['rows'], 'measured_tmb': None, 'readable': True, 'limitations': []}
    except ValueError as exc:
        st.error(str(exc))


if report:
    st.subheader(words('Check your report', 'Verify extracted variants'))
    if not clinician():
        patient_explanation(report.get('patient_explanation'))
    if report['measured_tmb']:
        st.metric(words('TMB listed in the report', 'Reported TMB · pending verification'), report['measured_tmb'])
        with st.expander('Source text'):
            st.write(report['measured_tmb_evidence'] or 'No source text found.')
    if not report['readable']:
        st.error('The report is hard to read. Upload a clearer image.')
        st.stop()
    if report['limitations']:
        with st.expander('Items to review', expanded=True):
            for item in report['limitations']:
                st.write(item)
    rows = st.session_state.get('portal_gene_rows', report['genes']) if mode == 'UPLOAD REPORT IMAGE' else state['rows']
    indexed = {row['gene']: row for row in rows}
    frame = pd.DataFrame([indexed[gene] for gene in GENES])
    status_labels = {'Unknown': 'Not known', 'Mutated': 'Change found', 'Not mutated': 'No change found'}
    display = frame.copy()
    if not clinician():
        display['status'] = display['status'].map(status_labels)
    with st.expander(words('Check the 50 genes', '50-gene feature review'), expanded=clinician()):
        edited = st.data_editor(display, hide_index=True, disabled=['gene'], width='stretch',
            key='portal_gene_editor_' + state['digest'] + '_' + str(st.session_state.get('portal_gene_revision', 0)) + '_' + str(clinician()),
            column_config={'gene': st.column_config.TextColumn('Gene'),
                           'status': st.column_config.SelectboxColumn('Status', options=STATUSES if clinician() else [status_labels[s] for s in STATUSES], required=True),
                           'evidence': st.column_config.TextColumn(words('Source text', 'Supporting evidence'), required=True)})
    rows = edited.to_dict('records')
    if not clinician():
        reverse_labels = {value: key for key, value in status_labels.items()}
        for row in rows:
            row['status'] = reverse_labels[row['status']]
    if mode == 'UPLOAD REPORT IMAGE':
        st.session_state.portal_gene_rows = rows
    else:
        state['rows'] = rows
    reviewed_id = fingerprint(rows)
    if state.get('reviewed_id') != reviewed_id:
        state['prediction'] = None
        state['reviewed_id'] = reviewed_id
    try:
        features = reviewed_features(rows)
        ready = True
    except ValueError as exc:
        ready = False
        st.warning(str(exc))
        unknown = [r['gene'] for r in rows if r['status'] == 'Unknown']
        if unknown:
            with st.expander(str(len(unknown)) + ' genes need review'):
                st.write(', '.join(unknown))
    confirmed = mode == 'TRY A SAMPLE' or st.checkbox(words('I checked all 50 genes against their sources.', 'I verified all 50 gene statuses and source evidence.'),
                            key='portal_gene_confirm_' + reviewed_id)
    if st.button('RUN TMB MODEL', type='primary', disabled=not (ready and confirmed)):
        try:
            state['prediction'] = predict(rows)
            state['prediction']['source'] = source['name']
        except (ValueError, OSError) as exc:
            st.error('The model could not run: ' + str(exc))
    if state['prediction']:
        status_card(words('TMB model category', 'TMB study classification'), state['prediction']['label'].replace(' study category', ''), icon='genetics')
        high = state['prediction']['label'].startswith('High')
        st.subheader('What does this result tell us?')
        st.write('This gene pattern was classified in the ' + ('higher' if high else 'lower') + ' mutation-burden group defined in Neil’s study.')
        st.write('In clinical testing, higher TMB can support considering immunotherapy. This research prediction is a reason to discuss confirmatory biomarker testing—not a treatment recommendation.' if high else 'A low research result does not rule out immunotherapy. Doctors also consider other biomarkers and the overall cancer diagnosis.')
        with st.expander('Questions to ask your doctor', expanded=True):
            st.write('• Would clinical TMB testing help clarify my options?')
            st.write('• What do my other biomarkers, such as MSI/MMR and PD-L1, tell us?')
        st.link_button('Learn why TMB matters · National Cancer Institute', 'https://www.cancer.gov/publications/dictionaries/cancer-terms/def/tumor-mutational-burden')
        a, b = st.columns(2)
        a.download_button('Download gene data', features.to_csv(index=False), 'reviewed_gene_features.csv', 'text/csv', icon=':material/download:')
        b.download_button('Download result', json.dumps(state['prediction'], indent=2), 'tmb_research_prediction.json', 'application/json', icon=':material/download:')
st.divider()
if st.button('CONTINUE TO RADIOLOGY REPORT →', use_container_width=True):
    st.switch_page(str(ROOT / 'app_pages/radiology.py'))
