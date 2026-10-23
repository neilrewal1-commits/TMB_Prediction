from urllib.parse import quote_plus

import streamlit as st

from prototype_core import ROOT
from care_app.ui import header, words
import streamlit.components.v1 as components

st.caption('STEP 3 OF 4 · FIND CANCER CARE')
header('Where can I find cancer care?', 'Find Cancer Care')
st.html('<section class="gene-research"><span class="gene-eyebrow">TAKE THE NEXT STEP</span>'
        '<h2>You’ve explored your reports.<br>Now find cancer care near you.</h2>'
        '<p>Enter a city or ZIP code to explore nearby cancer treatment centers.</p></section>')

patient = st.session_state.portal_patient
with st.form('portal_care_location_' + str(st.session_state.portal_epoch)):
    st.subheader('FIND CARE NEAR YOU')
    left, right = st.columns([1.4, 1])
    city = left.text_input('City or ZIP / postal code', key='care_search_city', value=patient['city'], placeholder='e.g., 94526 or Danville', max_chars=100)
    country = right.text_input('Country', key='care_search_country', value=patient['country'] or 'United States', max_chars=80)
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

map_location = (patient['city'] + ', ' + patient['country']) if patient['city'] and patient['country'] else 'Danville, California'
search_types = {
    'ALL CANCER CARE': 'cancer treatment centers',
    'HOSPITALS': 'hospitals with cancer care',
    'CANCER SPECIALISTS': 'oncologists',
    'RADIATION CENTERS': 'radiation oncology centers',
}
st.subheader('WHAT KIND OF CARE ARE YOU LOOKING FOR?')
selected_type = st.segmented_control(
    'Care type', options=list(search_types), default='ALL CANCER CARE',
    key='care_facility_type', selection_mode='single', width='stretch')
search_term = search_types.get(selected_type, search_types['ALL CANCER CARE'])
map_query = quote_plus(search_term + ' near ' + map_location)
with st.container(border=True, key='care_card_centers'):
    st.subheader('EXPLORE CARE · ' + map_location.upper())
    st.write('**Choose a care type to update the map and directions.**')
    st.link_button('OPEN RESULTS IN GOOGLE MAPS',
        'https://www.google.com/maps/search/?api=1&query=' + map_query,
        icon=':material/map:', type='primary', use_container_width=True)
    st.caption('Searching for ' + search_term + ' near ' + map_location + '.')
    components.iframe(
        'https://maps.google.com/maps?q=' + map_query + '&output=embed',
        height=420, scrolling=False)
    st.caption('If the preview does not load, use the Google Maps button above.')

st.subheader('COMPARE CARE OPTIONS')
st.caption('Danville & East Bay reference guide · Selected examples from official provider websites, checked October 23, 2026. This guide stays fixed while the map follows your search.')
st.markdown("""
| Center | Facility type | Cancer services | Organization | Details |
| :--- | :--- | :--- | :--- | :--- |
| **Hofmann Cancer Center** · Walnut Creek | Hospital-campus cancer center | Medical oncology, radiation oncology, infusion | John Muir Health nonprofit / UCSF partnership | [Official site](https://www.johnmuirhealth.com/locations/walnut-creek-behring-pavilion) |
| **Contra Costa Regional Medical Center** · Martinez | Public hospital | Cancer program, clinical trials | Public · County health system | [Official site](https://www.cchealth.org/get-care/medical-center-services/cancer-program) |
| **UCSF–John Muir Cancer Center** · Berkeley | Outpatient specialty center | Chemotherapy, immunotherapy, radiation therapy | Public university / nonprofit partnership | [Official site](https://www.ucsfhealth.org/locations/cancer-center-berkeley) |
""")
st.caption('Ask each center about referrals, insurance and appointment availability. Public or nonprofit status does not determine your cost.')
with st.expander('About this comparison'):
    st.markdown('Facility type describes the setting; organization describes the health system. Partnerships are shown as partnerships rather than assigned a single ownership label.')
    st.markdown('Sources: [John Muir Health nonprofit status](https://www.johnmuirhealth.com/giving/the-foundation.html) · [County hospital](https://www.cchealth.org/get-care/healthcare-locations/contra-costa-regional-medical-center) · [UCSF public university](https://www.ucsf.edu/about). Service details are linked in the table.')

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
