"""Source-linked public cases and sample reports."""
import hashlib
import json
import pickle

import pandas as pd
import streamlit as st

from prototype_core import (ROOT, FIELDS, genomic_csv, inspect_report,
                            current_facts, commit_report, loris_readiness, export_summary)
from clinical_ui import clinical_panel
from care_app.ui import badge, clinician, field_label, header, words

CASES = json.loads((ROOT / 'demo_data' / 'cases.json').read_text())
PUBLIC = 'Public research case'
SIMULATED = 'Public case + explicitly simulated extension'


@st.cache_resource
def load_model():
    with (ROOT / 'Best_Model_RF_50Trees_7Depth').open('rb') as handle:
        return pickle.load(handle)


def reset_case():
    keep = {k: st.session_state[k] for k in ['case_selector', 'mode_selector'] if k in st.session_state}
    for key in list(st.session_state):
        if key not in keep and not key.startswith(('portal_', 'care_', '_')):
            del st.session_state[key]
    st.session_state.update(keep)


def append_document(doc):
    updated, changes = commit_report(st.session_state.documents, doc)
    st.session_state.documents = updated
    st.session_state.latest_changes = changes
    st.session_state.history.append({'source': doc['filename'], 'changes': changes})


def choose_patient(index):
    st.session_state.case_selector = index
    reset_case()


header('Explore a sample case', 'Research workspace')
selection = st.session_state.setdefault('case_selector', 0)
for i, col in enumerate(st.columns(3)):
    with col, st.container(border=True, key='care_card_case_' + str(i)):
        st.subheader('Case ' + ['A', 'B', 'C'][i], anchor=False)
        st.write(str(CASES[i]['age']) + ' years · ' + words('Stomach cancer', 'Gastric adenocarcinoma'))
        st.button('Selected' if i == selection else 'Open case', key='journey_' + str(i),
                  on_click=choose_patient, args=(i,), type='primary' if i == selection else 'secondary', width='stretch')
mode = st.radio('Case data', [SIMULATED, PUBLIC],
    format_func=lambda value: 'Public + sample reports' if value == SIMULATED else 'Public records',
    key='mode_selector', on_change=reset_case, horizontal=True)
case = CASES[selection]
for key, default in [('documents', []), ('history', []), ('latest_changes', []), ('genomic', None)]:
    st.session_state.setdefault(key, default)
with st.expander('Case sources'):
    st.write(case['id'] + ' · ' + case['historical_stage'] + ' · AJCC 7 historical record')
    if mode == SIMULATED:
        st.write('Imaging and blood reports use simulated data. Clinical scenarios are fictional and separate from the historical record.')
    st.link_button('Public case source', case['source'], icon=':material/open_in_new:')
    st.button('Reset case', on_click=reset_case, icon=':material/restart_alt:')

cols = st.columns(3)
cols[0].metric(words('Gene model', 'TMB classification'), st.session_state.genomic['label'].replace(' study category', '') if st.session_state.genomic else '—')
cols[1].metric(words('Imaging reports', 'Imaging / pathology'), str(sum(d['stage'] == 'imaging' for d in st.session_state.documents)))
cols[2].metric(words('Blood reports', 'Laboratory / history'), str(sum(d['stage'] == 'labs' for d in st.session_state.documents)))
tabs = st.tabs([words('Genes', 'Genomics'), 'Imaging', words('Blood tests', 'Laboratory'), words('Stage', 'Staging'), words('Summary', 'Findings'), 'Research'])

with tabs[0]:
    st.subheader(words('Gene report', '50-gene TMB classifier'))
    file = ROOT / 'demo_data' / (case['id'] + '_genes.csv')
    a, b = st.columns(2)
    with a:
        use_example = st.button('Load sample genes', key='load_genes', type='primary', icon=':material/genetics:')
        with st.expander('Sample file'):
            st.download_button('Download gene CSV', file.read_bytes(), file.name, 'text/csv', icon=':material/download:')
    with b:
        uploaded = st.file_uploader('Upload a 50-gene CSV', type=['csv'], key='gene_upload', max_upload_size=5)
    if use_example:
        st.session_state.gene_candidate = (file.name, file.read_bytes())
        st.session_state.genomic = None
    if uploaded is not None:
        digest = hashlib.sha256(uploaded.getvalue()).hexdigest()
        if st.session_state.get('gene_upload_seen') != digest:
            st.session_state.gene_candidate = (uploaded.name, uploaded.getvalue())
            st.session_state.gene_upload_seen = digest
            st.session_state.genomic = None
    if st.session_state.get('gene_candidate'):
        name, data = st.session_state.gene_candidate
        try:
            frame = genomic_csv(data, single_patient=True)
            with st.expander(words('Check the 50 genes', 'Review feature matrix')):
                st.caption(name)
                if clinician():
                    st.dataframe(frame, hide_index=True)
                else:
                    st.dataframe(pd.DataFrame({'Gene': frame.columns, 'Status': ['Change found' if value else 'No change found' for value in frame.iloc[0]]}), hide_index=True, width='stretch')
            confirmed = st.checkbox(words('I checked all 50 genes for this case.', 'I verified case identity and all 50 gene statuses.'), key='gene_confirm_' + hashlib.sha256(data).hexdigest())
            if st.button('Run TMB model', disabled=not confirmed, type='primary', key='run_model'):
                prediction = int(load_model().predict(frame.to_numpy())[0])
                st.session_state.genomic = {'label': ['Low study category', 'High study category'][prediction], 'source': name, 'experimental': True, 'case_id': case['id']}
                st.session_state.latest_changes = ['TMB model classification added.']
                st.session_state.history.append({'source': name, 'changes': st.session_state.latest_changes})
                st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    if st.session_state.genomic:
        st.success('TMB model category: ' + st.session_state.genomic['label'].replace(' study category', ''))


def report_panel(stage):
    imaging = stage == 'imaging'
    st.subheader(words('Imaging report', 'Imaging / pathology findings') if imaging else words('Blood tests and health history', 'Laboratory and clinical history'))
    example_names = [case['id'] + '_clinical.txt'] if imaging else []
    if mode == SIMULATED:
        example_names += [case['id'] + ('_simulated_radiology.txt' if imaging else '_simulated_labs.txt')]
    if example_names:
        example = st.selectbox('Report', example_names, key=stage + '_example',
            format_func=lambda name: 'Public clinical record' if name.endswith('_clinical.txt') else ('Simulated radiology report' if 'radiology' in name else 'Simulated blood report'))
        example_bytes = (ROOT / 'demo_data' / example).read_bytes()
        a, b = st.columns(2)
        with b.expander('Sample file'):
            st.download_button('Download report', example_bytes, example, 'text/plain', key=stage + '_download', icon=':material/download:')
        if a.button('Load sample report', key=stage + '_load', type='primary'):
            st.session_state[stage + '_candidate'] = (example, example_bytes)
    elif not imaging:
        st.info('No public blood report is available for this case.')
    up = st.file_uploader('Upload a PDF or text report', type=['pdf', 'txt'], key=stage + '_upload', max_upload_size=5)
    if up is not None:
        digest = hashlib.sha256(up.getvalue()).hexdigest()
        if st.session_state.get(stage + '_upload_seen') != digest:
            st.session_state[stage + '_candidate'] = (up.name, up.getvalue())
            st.session_state[stage + '_upload_seen'] = digest
    candidate = st.session_state.get(stage + '_candidate')
    if not candidate:
        added = [d for d in st.session_state.documents if d['stage'] == stage]
        if added:
            st.success(str(len(added)) + ' reports added')
        return
    name, data = candidate
    try:
        doc = inspect_report(data, name, case['id'], stage)
        if doc['simulated'] and mode == PUBLIC:
            st.error('Select public + sample reports to add simulated data.')
            return
    except ValueError as exc:
        st.error(str(exc))
        return
    if data == (ROOT / 'demo_data' / (case['id'] + '_clinical.txt')).read_bytes():
        doc['provenance'] = 'Reconstructed public clinical data (not an original report)'
    badge('Simulated report' if doc['simulated'] else 'Public / uploaded source')
    with st.expander('Source text'):
        for page, text in enumerate(doc['pages'], 1):
            st.caption('Page ' + str(page))
            st.text(text)
    rows = pd.DataFrame(doc['fields'], columns=['field', 'value', 'page', 'excerpt'])
    labels = {field_label(key): key for key in FIELDS}
    rows['field'] = rows['field'].map(field_label)
    edited = st.data_editor(rows, num_rows='dynamic', hide_index=True, width='stretch',
        column_config={'field': st.column_config.SelectboxColumn('Field', options=list(labels), required=True),
                       'value': st.column_config.TextColumn('Value', required=True),
                       'page': st.column_config.NumberColumn('Page', min_value=1, max_value=len(doc['pages']), step=1, required=True),
                       'excerpt': st.column_config.TextColumn('Source text', required=True)}, key=stage + '_editor_' + doc['id'] + '_' + str(clinician()))
    source_ok = st.checkbox(words('I checked these values and confirmed this case.', 'I verified values, source passages, and case identity.'), key=stage + '_confirm_' + doc['id'])
    provenance = st.selectbox('Report origin', list(dict.fromkeys([doc['provenance'], 'Simulated report'])), key=stage + '_origin_' + doc['id'])
    if st.button('Add report', key=stage + '_add', type='primary', disabled=not source_ok):
        try:
            if provenance == 'Simulated report' and mode == PUBLIC:
                raise ValueError('Select public + sample reports to add simulated data.')
            cleaned = []
            for row in edited.to_dict('records'):
                row['field'] = labels.get(row['field'])
                if row['field'] not in FIELDS or pd.isna(row['value']) or not str(row['value']).strip():
                    raise ValueError('Each row needs a supported field and a value.')
                if pd.isna(row['page']) or float(row['page']) != int(row['page']):
                    raise ValueError('Enter a whole source page number.')
                page = int(row['page'])
                if page < 1 or page > len(doc['pages']):
                    raise ValueError('The source page is outside this report.')
                excerpt = str(row['excerpt'])
                if not excerpt.strip() or excerpt not in doc['pages'][page - 1]:
                    raise ValueError('Source text must match the source page exactly.')
                cleaned.append({'field': row['field'], 'value': str(row['value']).strip(), 'page': page, 'excerpt': excerpt})
            if not cleaned:
                raise ValueError('Add a field and its source text.')
            if len({r['field'] for r in cleaned}) != len(cleaned):
                raise ValueError('Use each field once per report.')
            if cleaned != doc['fields']:
                provenance += '; user-reviewed edits'
            doc.update(fields=cleaned, provenance=provenance)
            append_document(doc)
            del st.session_state[stage + '_candidate']
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


with tabs[1]:
    report_panel('imaging')
with tabs[2]:
    report_panel('labs')
with tabs[3]:
    if clinician():
        clinical_panel(case, mode == SIMULATED)
    else:
        st.session_state.clinical_result = None
        st.subheader('Recorded cancer stage')
        st.metric('Historical record · AJCC 7', case['historical_stage'])
        st.link_button('Learn about stomach cancer stages', 'https://www.cancer.gov/types/stomach/stages', icon=':material/open_in_new:')
        with st.expander('Clinical assessment'):
            st.write('Use the Clinician view to review staging inputs and treatment pathways.')

with tabs[4]:
    st.subheader(words('Your case summary', 'Integrated findings'))
    facts, conflicts = current_facts(st.session_state.documents)
    if conflicts:
        st.error('Conflicting sources: ' + ', '.join(FIELDS[k] for k in conflicts))
    if not facts and not st.session_state.genomic:
        st.write('Add a report to build the summary.')
    if st.session_state.genomic:
        st.metric('TMB model category', st.session_state.genomic['label'].replace(' study category', ''))
    for key, row in facts.items():
        with st.expander(field_label(key) + ': ' + row['value'], expanded=key in ['diagnosis', 'stage']):
            st.caption(f"{row['filename']} · page {row['page']} · {row['provenance']}")
            st.text(row['excerpt'])
    assessment = st.session_state.get('clinical_result')
    if assessment and clinician():
        with st.container(border=True):
            badge(assessment['provenance'])
            st.subheader('Calculated stage: ' + str(assessment['staging']['stage'] or 'Unresolved'))
            for card in assessment['treatment']['cards']:
                st.write('• ' + card['title'])
    if clinician():
        with st.expander('LORIS input readiness'):
            readiness = loris_readiness(facts, conflicts)
            for item in readiness['missing']:
                st.write('Missing: ' + item)
            for item in readiness['errors']:
                st.warning(item)
            if readiness['fields_present']:
                st.success('Six input fields are populated.')
            st.link_button('NCI LORIS', 'https://loris.ccr.cancer.gov/')
    st.download_button('Download summary', export_summary(case, mode, st.session_state.genomic, st.session_state.documents, st.session_state.get('clinical_result')), case['id'] + '_summary.txt', 'text/plain', icon=':material/download:')
    with st.expander('Reports and history'):
        for doc in list(st.session_state.documents):
            a, b = st.columns([4, 1])
            a.write(doc['filename'])
            if b.button('Remove', key='remove_' + doc['id']):
                st.session_state.documents = [d for d in st.session_state.documents if d['id'] != doc['id']]
                st.session_state.latest_changes = ['Removed ' + doc['filename'] + '.']
                st.session_state.history.append({'source': doc['filename'], 'changes': st.session_state.latest_changes})
                st.rerun()
        for event in st.session_state.history:
            st.write(event['source'])
            st.caption(' | '.join(event['changes']))

with tabs[5]:
    st.subheader('The research')
    with st.container(border=True, key='care_card_model'):
        st.subheader('TMB model', anchor=False)
        st.write(words('Neil Rewal’s model uses 50 genes to predict a high or low research category.', 'Neil Rewal’s random-forest classifier uses 50 binary gene features, 50 estimators, and a maximum depth of seven.'))
    with st.container(border=True, key='care_card_data'):
        st.subheader('Public cancer data', anchor=False)
        st.write('Three TCGA cases connect public mutation data with clinical records.')
        st.link_button('NCI Genomic Data Commons', 'https://portal.gdc.cancer.gov/', icon=':material/open_in_new:')
    with st.expander('Data and methods'):
        st.write('Historical stages use AJCC 7. Separate fictional scenarios use AJCC 8 pathological gastric staging.')
        st.write('Imaging and blood extensions are simulated. The TMB output is a study category. LORIS input readiness is available in Clinician view.')
        st.link_button('NCI LORIS research', 'https://loris.ccr.cancer.gov/', icon=':material/open_in_new:')
