import json

import pandas as pd
import streamlit as st

from care_app.ai import extract_genes
from care_app.model import STATUSES, predict, reviewed_features
from care_app.state import fingerprint
from care_app.ui import auto_analyze, clinician, header, image_input, patient_explanation, status_card, words
from prototype_core import GENES, ROOT

header('Your gene report', 'Genomic analysis')
left, right = st.columns([2.1, 1], gap='large')
with left, st.container(border=True, key='care_card_gene_upload'):
    st.subheader(words('Add a report', 'Upload genomic report'))
    source, state = image_input('genes', words('Gene report image', 'Molecular pathology report image'))
    if source:
        if auto_analyze('genes', source, state, extract_genes):
            st.session_state.portal_gene_rows = state['extraction']['genes']
            st.session_state.portal_gene_revision = st.session_state.get('portal_gene_revision', 0) + 1
    else:
        st.page_link(str(ROOT / 'integrated_report.py'), label='Explore a sample case', icon=':material/science:')
with right:
    report = state['extraction']
    status_card('Report status', 'Ready to review' if report else ('Image added' if source else 'No report added'), icon='task_alt' if report else 'description')
    with st.expander(words('What is TMB?', 'TMB and model specification')):
        st.write(words('TMB describes how many DNA changes a tumor has.', 'Tumor mutational burden quantifies somatic mutations. The classifier uses 50 binary gene features and a 50-tree random forest.'))
        st.link_button('National Cancer Institute', 'https://www.cancer.gov/publications/dictionaries/cancer-terms/def/tumor-mutational-burden', icon=':material/open_in_new:')

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
    rows = st.session_state.get('portal_gene_rows', report['genes'])
    indexed = {row['gene']: row for row in rows}
    frame = pd.DataFrame([indexed[gene] for gene in GENES])
    status_labels = {'Unknown': 'Not known', 'Mutated': 'Change found', 'Not mutated': 'No change found'}
    display = frame.copy()
    if not clinician():
        display['status'] = display['status'].map(status_labels)
    with st.expander(words('Check the 50 genes', '50-gene feature review'), expanded=True):
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
    st.session_state.portal_gene_rows = rows
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
    confirmed = st.checkbox(words('I checked all 50 genes against their sources.', 'I verified all 50 gene statuses and source evidence.'),
                            key='portal_gene_confirm_' + reviewed_id)
    if st.button(words('Get model result', 'Run TMB classifier'), type='primary', disabled=not (ready and confirmed)):
        try:
            state['prediction'] = predict(rows)
            state['prediction']['source'] = source['name']
        except (ValueError, OSError) as exc:
            st.error('The model could not run: ' + str(exc))
    if state['prediction']:
        status_card(words('TMB model category', 'TMB study classification'), state['prediction']['label'].replace(' study category', ''), icon='genetics')
        a, b = st.columns(2)
        a.download_button('Download gene data', features.to_csv(index=False), 'reviewed_gene_features.csv', 'text/csv', icon=':material/download:')
        b.download_button('Download result', json.dumps(state['prediction'], indent=2), 'tmb_research_prediction.json', 'application/json', icon=':material/download:')
st.page_link(str(ROOT / 'app_pages/radiology.py'), label=words('View imaging', 'Review radiology'), icon=':material/arrow_forward:')
