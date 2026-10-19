"""Short patient journeys. Clinical review stays on the professional pages."""
import json

import streamlit as st

from care_app import ai
from care_app.ui import auto_analyze, image_input


def home_link():
    from prototype_core import ROOT
    st.page_link(str(ROOT / 'app_pages/home.py'), label='Back to home', icon=':material/arrow_back:')


def report_page(kind, show_title=True):
    if show_title:
        home_link()
        st.title('Your gene report' if kind == 'genes' else 'Your imaging')
    st.write('Add a photo of your written report.')
    source, state = image_input(kind, 'Choose a report photo')
    if not source:
        return
    analyzer = ai.extract_genes if kind == 'genes' else ai.review_radiology
    if auto_analyze(kind, source, state, analyzer) and kind == 'genes':
        st.session_state.portal_gene_rows = state['extraction']['genes']
        st.session_state.portal_gene_revision = st.session_state.get('portal_gene_revision', 0) + 1
    result = state.get('extraction')
    if not result:
        return
    if not result['readable']:
        st.error('We could not read this photo. Try a clearer photo of the written report.')
        return
    st.subheader('Your results')
    explanation = result.get('patient_explanation')
    if explanation:
        st.write(explanation['overview'])
        points = [p for p in explanation['key_points'] if p != explanation['overview']]
        if points:
            with st.expander('More about these results'):
                for point in points:
                    st.write('• ' + point)
        if explanation['next_steps']:
            st.subheader('What to do next')
            for step in explanation['next_steps'][:3]:
                st.write('• ' + step)
        if explanation['terms']:
            with st.expander('Medical words explained'):
                for item in explanation['terms']:
                    st.write('**' + item['term'] + '** — ' + item['meaning'])
    elif result.get('summary'):
        st.write(result['summary'])
    if kind == 'genes' and result.get('measured_tmb'):
        st.write('**TMB listed in your report:** ' + result['measured_tmb'])
    with st.expander('Report details'):
        if kind == 'radiology':
            for item in result.get('findings', []):
                st.write(item.get('plain_language') or item['finding'])
                st.caption(item['evidence'])
        elif result.get('measured_tmb_evidence'):
            st.write(result['measured_tmb_evidence'])
        for item in result.get('limitations', []):
            st.write(item)
        st.download_button('Save these results', json.dumps(result, indent=2),
                           kind + '_review.json', 'application/json', icon=':material/download:')


def care_page():
    from urllib.parse import quote_plus
    home_link()
    st.title('Find cancer care')
    patient = st.session_state.portal_patient
    city = st.text_input('City or postal code', value=patient['city'], max_chars=100).strip()
    country = st.text_input('Country', value=patient['country'], max_chars=80).strip()
    ready = bool(city and country)
    if ready and (city, country) != (patient['city'], patient['country']):
        st.session_state.portal_patient = patient | {'city': city, 'country': country}
        st.session_state.pop('portal_centers', None)
    query = quote_plus('cancer treatment centers near ' + city + ', ' + country)
    st.link_button('Find nearby centers', 'https://www.google.com/maps/search/?api=1&query=' + query,
                   type='primary', icon=':material/map:', width='stretch', disabled=not ready)
