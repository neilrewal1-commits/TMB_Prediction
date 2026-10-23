import json
from html import escape

import pandas as pd
import streamlit as st

from care_app.ai import extract_genes
from care_app.model import STATUSES, predict, reviewed_features
from care_app.state import fingerprint
from care_app.ui import auto_analyze, clinician, header, image_input, patient_explanation, status_card, words
from prototype_core import GENES, ROOT, genomic_csv

st.html("""<style>
.gene-change-strip{padding:1rem 1.25rem;border:1px solid #72b9aa;border-radius:14px;background:#edf9f4;margin:.3rem 0 1rem;}
.gene-change-strip strong{display:block;color:#155a4b;margin-bottom:.6rem;}
.gene-change-chip{display:inline-block;padding:.4rem .8rem;margin:.2rem .35rem .2rem 0;border-radius:8px;background:#c8f0dd;color:#124b3d;font-weight:800;font-size:1.05rem;border:1px solid #55a98a;}
.gene-result{text-align:center;padding:1.8rem 1rem 2rem;margin:1rem 0;border-radius:20px;background:#edf5fa;border:1px solid #b7cddd;}
.gene-result-label{font-size:.95rem;letter-spacing:.12em;font-weight:750;color:#365b70;}
.gene-result-value{font-size:clamp(3.5rem,8vw,5.5rem);font-weight:850;line-height:1.2;color:#123e56;margin:.35rem 0;}
.gene-result-sub{font-size:1.1rem;color:#365b70;}
</style>""")
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
<p class="gene-relevance"><strong>Why TMB? Understanding tumor mutation burden can help doctors explore treatment options—including whether to consider immunotherapy.</strong></p>
</section>""")
with st.expander('How the research works'):
    st.write('**Data:** I used cBioPortal / TCGA stomach-cancer data: 344 training samples and 87 test samples.')
    st.write('**Model:** A Random Forest uses mutation patterns across 50 genes to predict a high or low research category.')
    st.write('**Demo:** These two examples come from my original test dataset. Run the model to compare its prediction with the recorded label.')
    st.caption('High and low are research categories, not clinical TMB measurements. Sample A: original test row 1, recorded Low; Sample B: original test row 2, recorded High.')
    st.page_link(str(ROOT / 'app_pages/about_research.py'), label='MY RESEARCH & SOURCES', icon=':material/science:')
st.html('<h2 class="gene-action-title">TRY THE RESEARCH IN ACTION</h2>')
mode = st.segmented_control('Choose your input', ['TRY A SAMPLE', 'UPLOAD GENE CSV', 'UPLOAD REPORT IMAGE'], default='TRY A SAMPLE', key='portal_gene_input_mode', selection_mode='single', width='stretch')
source = None
report = None
state = None
if mode == 'TRY A SAMPLE':
    st.caption('FROM MY RESEARCH DATASET · Choose a sample, then run my model.')
    a, b = st.columns(2)
    if a.button('LOAD SAMPLE A', use_container_width=True, key='gene_sample_a'):
        st.session_state.portal_gene_sample = 'Neil_Test_Sample_A'
    if b.button('LOAD SAMPLE B', use_container_width=True, key='gene_sample_b'):
        st.session_state.portal_gene_sample = 'Neil_Test_Sample_B'
    case_id = st.session_state.get('portal_gene_sample')
    if case_id in ('Neil_Test_Sample_A', 'Neil_Test_Sample_B'):
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
    def highlight_mutations(row):
        changed = row['status'] in ('Mutated', 'Change found')
        return ['background-color: #c8f0dd; color: #124b3d; font-weight: bold' if changed else '' for _ in row]
    styled_display = display.style.apply(highlight_mutations, axis=1)
    with st.expander(words('Check the 50 genes', '50-gene feature review'), expanded=clinician()):
        edited = st.data_editor(styled_display, hide_index=True, disabled=True if mode == 'TRY A SAMPLE' else ['gene'], width='stretch',
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
    changed_genes = [r['gene'] for r in rows if r['status'] == 'Mutated']
    if changed_genes:
        chips = ''.join('<span class="gene-change-chip">' + escape(gene) + '</span>' for gene in changed_genes)
        st.html('<div class="gene-change-strip"><strong>GENE CHANGES FOUND · ' + str(len(changed_genes)) + ' OF 50</strong>' + chips + '</div>')
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
    if st.button('RUN TMB MODEL', key='gene_run_model', use_container_width=True, type='primary', disabled=not (ready and confirmed)):
        try:
            state['prediction'] = predict(rows)
            state['prediction']['source'] = source['name']
        except (ValueError, OSError) as exc:
            st.error('The model could not run: ' + str(exc))
    if state['prediction']:
        high = state['prediction']['label'].startswith('High')
        result_word = 'HIGH' if high else 'LOW'
        st.html('<section class="gene-result" aria-label="TMB model result"><div class="gene-result-label">TMB MODEL RESULT</div><div class="gene-result-value">' + result_word + '</div><div class="gene-result-sub">Predicted mutation-burden category</div></section>')
        if clinician():
            with st.container(border=True):
                st.subheader('MODEL & EVIDENCE REVIEW')
                a, b, c = st.columns(3)
                a.metric('Input features', '50 genes')
                b.metric('Internal test accuracy', '78.2%')
                c.metric('Correct / test samples', '68 / 87')
                st.caption('Reproduced using the saved model and original test.csv. Internal research evaluation; external clinical performance has not been established.')
                st.write('**Model:** Random Forest · 50 trees · maximum depth 7. **Training / test:** 344 / 87 stomach-cancer samples.')
                st.write('**Current source:** ' + source['name'])
                st.write('**Interpretation:** Study-defined HIGH/LOW classification. Clinical TMB in mutations/Mb is not estimated by this output.')
                st.write('**Review alongside:** pathology, clinically measured TMB, MSI/MMR and PD-L1 where relevant. Treatment eligibility is not established by this model.')
        bullets = [
            'The model predicts a **' + ('HIGH' if high else 'LOW') + ' mutation-burden research category.',
            'This result comes from patterns across **50 genes**.',
            'Higher clinically measured TMB can support considering **immunotherapy**.' if high else 'A low result **does not rule out immunotherapy**.',
            'Other biomarkers and the cancer diagnosis also shape treatment options.',
            'Bring this result to your doctor to discuss whether clinical biomarker testing would help.'
        ]

        doctor_questions = [
            'Could immunotherapy be an option for my cancer?',
            'Would clinical TMB testing help us decide?',
            'What do my MSI/MMR and PD-L1 results tell us?',
            'How do these findings fit with my other reports?',
            'What other treatment options should we discuss?'
        ]
        def card_items(items):
            import re
            return ''.join('<li>' + re.sub(r'[*][*](.+?)[*][*]', lambda match: '<strong>' + match.group(1) + '</strong>', escape(item)) + '</li>' for item in items)
        result_heading = 'RESEARCH OUTPUT & INTERPRETATION' if clinician() else 'WHAT THIS RESULT TELLS YOU'
        questions_heading = 'BIOMARKERS & REVIEW QUESTIONS' if clinician() else 'QUESTIONS FOR YOUR DOCTOR'
        if clinician():
            doctor_questions = ['Is clinically measured TMB available, with assay and units?', 'Are MSI/MMR and PD-L1 results available where relevant?', 'Does pathology confirm the cancer type?', 'Are these sources from the same patient and time point?', 'What additional evidence is required for a treatment discussion?']
        st.html('<div class="gene-results-grid"><section class="gene-result-card"><h3>' + result_heading + '</h3><ul>'
                + card_items(bullets) + '</ul></section><section class="gene-result-card gene-doctor-card"><h3>' + questions_heading + '</h3><ul>'
                + card_items(doctor_questions) + '</ul></section></div>')
        with st.container(key='gene_learn_link'):
            st.link_button('LEARN WHY TMB MATTERS · NATIONAL CANCER INSTITUTE', 'https://www.cancer.gov/publications/dictionaries/cancer-terms/def/tumor-mutational-burden')
        a, b = st.columns(2)
        a.download_button('Download gene data', features.to_csv(index=False), 'reviewed_gene_features.csv', 'text/csv', icon=':material/download:')
        b.download_button('Download result', json.dumps(state['prediction'], indent=2), 'tmb_research_prediction.json', 'application/json', icon=':material/download:')
st.divider()
if st.button('CONTINUE TO RADIOLOGY REPORT →', use_container_width=True):
    st.switch_page(str(ROOT / 'app_pages/radiology.py'))
