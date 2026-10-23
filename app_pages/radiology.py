"""Report-first radiology page with an explicit review action and bundled sample."""
import json
from html import escape

import streamlit as st

from care_app.imaging import imaging_input, analyze_files
from care_app.ui import auto_analyze, clinician, header
from prototype_core import ROOT

SAMPLE = ROOT / 'demo_data/Published_Gastric_CT_Summary.pdf'
SAMPLE_RESULT = {'summary': 'The initial CT showed abnormal stomach-wall thickening. Biopsy later confirmed a rare type of stomach cancer. Follow-up imaging after surgery showed new liver lesions, subsequently confirmed as metastases.', 'clinical_summary': 'Published case: initial contrast CT demonstrated antral/pyloric circumferential wall thickening up to 1.9 cm with progressive enhancement and no hepatic metastases or significant abdominal lymphadenopathy. Biopsy confirmed AFP-producing hepatoid gastric adenocarcinoma. Subsequent surveillance CT and histology documented liver metastases.', 'readable': True, 'patient_explanation': {'key_points': ['The initial scan showed thickening near the stomach outlet, measuring up to 1.9 cm.', 'The abnormal tissue became brighter after contrast, a finding the clinicians investigated further.', 'The initial scan did not show liver metastases or significantly enlarged abdominal lymph nodes.', 'Biopsy, rather than the scan alone, established the cancer diagnosis.', 'Later scans showed new liver lesions after surgery; tissue testing confirmed spread.']}, 'questions_for_clinician': ['What does the stomach-wall thickening mean?', 'Which findings require biopsy or other testing?', 'How do the latest findings compare with the earlier scan?', 'Which biomarker tests could inform treatment discussions?', 'What follow-up imaging and specialist appointments are needed?'], 'findings': [{'finding': 'Clinical context', 'evidence': 'A 68-year-old man underwent contrast-enhanced abdominal CT during investigation of anemia.', 'sources': [{'filename': 'Published_Gastric_CT_Summary.pdf', 'page': 1}]}, {'finding': 'Initial CT findings', 'evidence': 'The stomach antrum and pylorus had irregular circumferential wall thickening measuring up to 1.9 cm. The abnormal tissue enhanced progressively after contrast. The initial scan showed no liver metastases or significantly enlarged abdominal lymph nodes.', 'sources': [{'filename': 'Published_Gastric_CT_Summary.pdf', 'page': 1}]}, {'finding': 'Diagnostic confirmation', 'evidence': 'Endoscopic biopsy established AFP-producing hepatoid adenocarcinoma of the stomach. This diagnosis came from tissue examination, not CT alone.', 'sources': [{'filename': 'Published_Gastric_CT_Summary.pdf', 'page': 1}]}, {'finding': 'Later imaging', 'evidence': 'Follow-up CT after gastric surgery showed new lesions in the right liver. Subsequent tissue examination confirmed metastatic disease. These later findings belong to a different time point from the initial scan.', 'sources': [{'filename': 'Published_Gastric_CT_Summary.pdf', 'page': 1}]}], 'provenance': 'Prepared explanation of a source-linked summary of Zhong et al. (2026), not a live AI response.', 'source_url': 'https://doi.org/10.3389/fonc.2026.1768282'}

def render_cards(points, questions):
    def items(values):
        return ''.join('<li>' + escape(str(value)) + '</li>' for value in values)
    st.html('<div class="gene-results-grid"><section class="gene-result-card"><h3>WHAT YOUR REPORT TELLS YOU</h3><ul>'
            + items(points) + '</ul></section><section class="gene-result-card gene-doctor-card"><h3>QUESTIONS FOR YOUR DOCTOR</h3><ul>'
            + items(questions) + '</ul></section></div>')


st.caption('STEP 2 OF 4 · RADIOLOGY REPORT')
header('What does my radiology report mean?', 'Radiology Report · Findings & evidence')
st.html('<section class="gene-research"><span class="gene-eyebrow">FROM MEDICAL WORDS TO CLEARER ANSWERS</span>'
        '<h2>Read the report. Understand the findings.</h2>'
        '<p>Upload a report to see its key findings in everyday language and prepare questions for your doctor.</p></section>')
st.html('<style>.st-key-radiology_explain button,.st-key-radiology_sample_load button{min-height:60px;width:100%;}'
        '.st-key-radiology_explain button p,.st-key-radiology_sample_load button p{font-size:1.1rem;font-weight:800;}'
        '.st-key-radiology_mode button{min-height:54px;}.st-key-radiology_mode button p{font-weight:750;font-size:1rem;}</style>')
mode = st.segmented_control('Choose a report', ['TRY SAMPLE REPORT', 'UPLOAD YOUR REPORT'], default='TRY SAMPLE REPORT', key='radiology_mode', width='stretch')
result = None
files = []
if mode == 'TRY SAMPLE REPORT':
    st.caption('Published case · CT findings summary')
    if st.button('LOAD SAMPLE REPORT', key='radiology_sample_load'):
        st.session_state.portal_radiology_sample_loaded = True
    if st.session_state.get('portal_radiology_sample_loaded'):
        with st.expander('PREVIEW YOUR REPORT', expanded=True):
            st.pdf(SAMPLE.read_bytes(), height=480, key='radiology_sample_pdf')
        st.download_button('DOWNLOAD SAMPLE PDF', SAMPLE.read_bytes(), SAMPLE.name, 'application/pdf')
        if st.button('EXPLAIN MY REPORT', type='primary', key='radiology_explain'):
            st.session_state.portal_radiology_sample_explained = True
        if st.session_state.get('portal_radiology_sample_explained'):
            result = SAMPLE_RESULT
            st.caption('Prepared sample explanation')
            st.link_button('VIEW PUBLISHED SOURCE', SAMPLE_RESULT['source_url'])
else:
    # Keep the coach’s file handling and AI review, but start analysis on a deliberate click.
    # The existing helper's upload copy is replaced below without changing the API integration.
    files, state = imaging_input(auto_send=False)
    if files:
        if st.button('EXPLAIN MY REPORT', type='primary', key='radiology_explain'):
            state['attempted'] = False
            state['error'] = None
            auto_analyze('radiology', {'name':'Combined imaging upload', 'data':files}, state, analyze_files)
        result = state.get('extraction')

if result:
    st.subheader('YOUR REPORT, EXPLAINED')
    st.write(result.get('clinical_summary') if clinician() and result.get('clinical_summary') else result['summary'])
    if not result.get('readable', True):
        st.warning('This report could not be read reliably. Please try a clearer copy.')
    for conflict in result.get('conflicts', []):
        st.warning(conflict)
    points = (result.get('patient_explanation') or {}).get('key_points') or [result['summary']]
    questions = result.get('questions_for_clinician') or ['Which findings should we discuss first?', 'What follow-up do you recommend?']
    render_cards(points, questions)
    with st.expander('SEE THE SUPPORTING REPORT TEXT'):
        for finding in result.get('findings', []):
            st.markdown('**' + finding['finding'] + '**')
            st.write(finding['evidence'])
            for source in finding.get('sources', []):
                st.caption(source['filename'] + (' · page ' + str(source['page']) if source.get('page') else ''))
        for limitation in result.get('limitations', []):
            st.write(limitation)
    st.subheader('BUILDING A CLEARER PICTURE')
    gene_state = st.session_state.get('portal_genes' if st.session_state.get('portal_gene_input_mode') == 'UPLOAD REPORT IMAGE' else 'portal_gene_structured', {})
    prediction = gene_state.get('prediction')
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.markdown('**01 · GENE REPORT & TMB**')
        if prediction:
            st.write(prediction['label'].replace(' study category', '').upper() + ' · Model prediction')
            st.caption(prediction.get('source', 'Gene input'))
        else:
            st.write('Explore mutation patterns with Neil’s model.')
            st.page_link(str(ROOT / 'app_pages/genes.py'), label='GO TO GENE REPORT & TMB')
    with right, st.container(border=True):
        st.markdown('**02 · RADIOLOGY REPORT**')
        st.write('Understand the scan findings and recommended follow-up.')
        st.caption(SAMPLE.name if mode == 'TRY SAMPLE REPORT' else ', '.join(file['name'] for file in files))
    st.write('Gene information and scan findings answer different questions. Keeping both accessible can help patients prepare for a more informed conversation with their care team.')
    st.download_button('SAVE REPORT EXPLANATION', json.dumps(result, indent=2), 'radiology_explanation.json', 'application/json')
st.divider()
if st.button('CONTINUE TO FIND CANCER CARE →', use_container_width=True):
    st.switch_page(str(ROOT / 'app_pages/patient.py'))
