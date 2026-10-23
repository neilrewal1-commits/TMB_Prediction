from datetime import datetime, timezone
from urllib.parse import quote_plus

import streamlit as st
from openai import OpenAIError

from care_app.ai import find_centers, setting
from prototype_core import ROOT
from care_app.ui import api_error, header, words

st.caption('STEP 3 OF 4 · FIND CANCER CARE')
header('Where can I find cancer care?', 'Find Cancer Care')
st.html('<section class="gene-research"><span class="gene-eyebrow">TAKE THE NEXT STEP</span>'
        '<h2>You’ve explored your reports.<br>Now find cancer care near you.</h2>'
        '<p>Enter a city or ZIP code to explore nearby cancer treatment centers.</p></section>')

patient = st.session_state.portal_patient
with st.form('portal_care_location_' + str(st.session_state.portal_epoch)):
    st.subheader('FIND CARE NEAR YOU')
    left, right = st.columns([1.4, 1])
    city = left.text_input('City or ZIP / postal code', value=patient['city'], placeholder='e.g., 94526 or Danville', max_chars=100)
    country = right.text_input('Country', value=patient['country'] or 'United States', max_chars=80)
    submitted = st.form_submit_button('FIND CANCER CARE', type='primary', use_container_width=True)
    if submitted:
        if not city.strip() or not country.strip():
            st.error('Enter a city or postal code and country.')
        else:
            if (patient['city'], patient['country']) != (city.strip(), country.strip()):
                st.session_state.pop('portal_centers', None)
                st.session_state.pop('portal_centers_consent', None)
            patient.update(city=city.strip(), country=country.strip())
            st.session_state.portal_patient = patient

if patient['city'] and patient['country']:
    location = patient['city'] + ', ' + patient['country']
    st.subheader('EXPLORE CARE NEAR ' + patient['city'].upper())
    with st.container(border=True, key='care_card_centers'):
        st.write('**Find locations, contact details, and directions.**')
        query = quote_plus('cancer treatment centers near ' + location)
        st.link_button('OPEN CANCER CENTERS IN GOOGLE MAPS',
            'https://www.google.com/maps/search/?api=1&query=' + query,
            icon=':material/map:', type='primary', use_container_width=True)
        st.caption('Opens Google Maps results for ' + location + '.')
    if setting('OPENAI_API_KEY'):
        with st.expander('SEARCH CENTER DETAILS'):
            search_consent = st.checkbox('Allow OpenAI to search using this location.', key='portal_centers_consent')
            if st.button('SEARCH CENTER DETAILS', disabled=not search_consent, icon=':material/search:'):
                st.session_state.pop('portal_centers', None)
                try:
                    with st.spinner('Finding centers…'):
                        result = find_centers(patient['city'], patient['country'])
                        result['searched_at'] = datetime.now(timezone.utc).isoformat()
                        st.session_state.portal_centers = result
                except (OpenAIError, ValueError) as exc:
                    api_error(exc)

centers = st.session_state.get('portal_centers')
if centers:
    st.subheader('NEARBY CENTERS')
    st.markdown(centers['text'])
    with st.expander('Sources'):
        st.caption(centers['location'] + ' · ' + centers['searched_at'][:10])
        for source in centers['sources']:
            st.link_button(source['title'] or 'Official source', source['url'])

with st.expander(words('Optional · Your details', 'Optional · Patient demographics')):
    with st.form('portal_patient_form_' + str(st.session_state.portal_epoch)):
        left, right = st.columns(2)
        alias = left.text_input(words('Preferred name', 'Patient alias'), value=patient['alias'], max_chars=60)
        age = right.number_input('Age', value=patient['age'], min_value=0, max_value=120, step=1)
        diagnosis = st.text_input(words('Diagnosis', 'Documented diagnosis'), value=patient['diagnosis'], max_chars=200)
        if st.form_submit_button('SAVE OPTIONAL DETAILS', icon=':material/check:'):
            patient.update(alias=alias.strip(), age=age, diagnosis=diagnosis.strip())
            st.session_state.portal_patient = patient
            st.success('Your details are saved.')

st.divider()
if st.button('CONTINUE TO FIND SUPPORT →', use_container_width=True):
    st.switch_page(str(ROOT / 'app_pages/community.py'))
