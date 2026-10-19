from datetime import datetime, timezone
from urllib.parse import quote_plus

import streamlit as st
from openai import OpenAIError

from care_app.ai import find_centers, setting
from prototype_core import ROOT
from care_app.state import clear_patient
from care_app.ui import api_error, clinician, header, status_card, words

if not clinician():
    from care_app.simple import care_page
    care_page()
    st.stop()

header('Your care', 'Patient profile')
patient = st.session_state.portal_patient
if patient['alias']:
    a, b, c = st.columns(3)
    with a:
        status_card(words('Name', 'Patient alias'), patient['alias'], icon='person')
    with b:
        status_card(words('Diagnosis', 'Documented diagnosis'), patient['diagnosis'] or 'Not added', icon='clinical_notes')
    with c:
        status_card('Location', ', '.join(filter(None, [patient['city'], patient['country']])) or 'Not added', icon='location_on')

with st.expander(words('Your details', 'Patient demographics'), expanded=not bool(patient['alias'])):
    with st.form('portal_patient_form_' + str(st.session_state.portal_epoch)):
        left, right = st.columns(2)
        alias = left.text_input(words('Preferred name', 'Patient alias'), value=patient['alias'], max_chars=60)
        age = right.number_input('Age', value=patient['age'], min_value=0, max_value=120, step=1)
        diagnosis = st.text_input(words('Diagnosis', 'Documented diagnosis'), value=patient['diagnosis'], max_chars=200)
        left, right = st.columns(2)
        city = left.text_input('City or postal code', value=patient['city'], max_chars=100)
        country = right.text_input('Country', value=patient['country'], max_chars=80)
        if st.form_submit_button('Save details', type='primary', icon=':material/check:'):
            if not alias.strip():
                st.error(words('Enter a preferred name.', 'Enter a patient alias.'))
            else:
                if patient['alias'] and patient['alias'] != alias.strip():
                    clear_patient()
                updated = dict(alias=alias.strip(), age=age, diagnosis=diagnosis.strip(), city=city.strip(), country=country.strip())
                if (patient['city'], patient['country']) != (updated['city'], updated['country']):
                    st.session_state.pop('portal_centers', None)
                    st.session_state.pop('portal_centers_consent', None)
                st.session_state.portal_patient = updated
                st.rerun()

patient = st.session_state.portal_patient
with st.container(border=True, key='care_card_centers'):
    st.subheader(words('Find cancer care', 'Cancer treatment centers'))
    has_location = bool(patient['city'] and patient['country'])
    if has_location:
        query = quote_plus('cancer treatment centers near ' + patient['city'] + ', ' + patient['country'])
        st.link_button('Find centers on Google Maps', 'https://www.google.com/maps/search/?api=1&query=' + query, icon=':material/map:', type='primary')
        if setting('OPENAI_API_KEY'):
            search_consent = st.checkbox('Allow OpenAI to search using this location.', key='portal_centers_consent')
            if st.button('Search center details', disabled=not search_consent, icon=':material/search:'):
                st.session_state.pop('portal_centers', None)
                try:
                    with st.spinner('Finding centers…'):
                        result = find_centers(patient['city'], patient['country'])
                        result['searched_at'] = datetime.now(timezone.utc).isoformat()
                        st.session_state.portal_centers = result
                except (OpenAIError, ValueError) as exc:
                    api_error(exc)
    else:
        st.write('Save your city and country to find nearby centers.')

centers = st.session_state.get('portal_centers')
if centers:
    st.subheader('Nearby centers')
    st.markdown(centers['text'])
    with st.expander('Sources'):
        st.caption(centers['location'] + ' · ' + centers['searched_at'][:10])
        for source in centers['sources']:
            st.link_button(source['title'] or 'Official source', source['url'])
st.page_link(str(ROOT / 'app_pages/community.py'), label='Find support', icon=':material/arrow_forward:')
