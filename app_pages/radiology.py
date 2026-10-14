import json

import streamlit as st

from care_app.ai import review_radiology
from prototype_core import ROOT
from care_app.ui import auto_analyze, clinician, header, image_input, patient_explanation, status_card, words

header('Your imaging', 'Radiology review')
st.caption('For the most helpful explanation, upload a readable photo of the written radiology report. '
           'Scan pictures receive limited guidance and require a radiologist’s interpretation.')
left, right = st.columns([2.1, 1], gap='large')
with left, st.container(border=True, key='care_card_radiology_upload'):
    st.subheader(words('Add an image', 'Upload radiology image'))
    source, state = image_input('radiology', words('Scan or written report image', 'Radiograph, scan slice, or report screenshot'))
    if source:
        auto_analyze('radiology', source, state, review_radiology)
    else:
        st.page_link(str(ROOT / 'integrated_report.py'), label='Explore a sample case', icon=':material/science:')
with right:
    review = state['extraction']
    status_card('Image status', 'Ready to review' if review else ('Image added' if source else 'No image added'), icon='radiology')

if review:
    st.subheader(words('What the image shows', 'Documented findings'))
    st.write(words(review['summary'], review.get('clinical_summary') or review['summary']))
    if not clinician():
        patient_explanation(review.get('patient_explanation'))
    if review['readable']:
        for item in review['findings']:
            with st.expander(item['finding'] if clinician() else (item.get('plain_language') or item['finding'])):
                if clinician() and item.get('plain_language'):
                    st.write(item['plain_language'])
                st.caption('Exact words from the report')
                st.write(item['evidence'])
    else:
        st.warning('The image is hard to read. Upload a clearer image or written report.')
    if review['limitations']:
        with st.expander('Items to review'):
            for item in review['limitations']:
                st.write(item)
    if review['questions_for_clinician']:
        with st.expander(words('Questions for your care team', 'Follow-up questions'), expanded=not clinician()):
            for question in review['questions_for_clinician']:
                st.write('• ' + question)
    st.caption('AI explanation for review with your care team. It does not establish a diagnosis or treatment plan.')
    st.download_button('Download review', json.dumps(review, indent=2), 'radiology_image_review.json', 'application/json', icon=':material/download:')
st.page_link(str(ROOT / 'app_pages/patient.py'), label=words('Find care', 'Open patient profile'), icon=':material/arrow_forward:')
