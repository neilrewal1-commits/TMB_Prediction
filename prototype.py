"""Run with: streamlit run prototype.py."""
from pathlib import Path

import streamlit as st

from care_app.state import clear_patient, initialize
from care_app.ui import apply_theme, clinician, interaction_controls

st.set_page_config(page_title='Cancer Care', page_icon=':material/ecg_heart:', layout='wide')
initialize()
apply_theme()
ROOT = Path(__file__).resolve().parent

pages = [
    st.Page(ROOT / 'app_pages/home.py', title='Home', icon=':material/home:', default=True),
    st.Page(ROOT / 'app_pages/report.py', title='Understand a report', icon=':material/description:', url_path='report'),
    st.Page(ROOT / 'app_pages/genes.py', title='Gene report', icon=':material/genetics:', url_path='genes'),
    st.Page(ROOT / 'app_pages/radiology.py', title='Imaging', icon=':material/radiology:', url_path='radiology'),
    st.Page(ROOT / 'app_pages/patient.py', title='My care', icon=':material/local_hospital:', url_path='patient'),
    st.Page(ROOT / 'app_pages/community.py', title='Support', icon=':material/groups:', url_path='community'),
    st.Page(ROOT / 'integrated_report.py', title='Research workspace', icon=':material/science:', url_path='research'),
]
navigation = st.navigation(pages, position='hidden')

with st.sidebar:
    st.html('<div class="care-brand"><span class="care-mark" aria-hidden="true">+</span>Cancer Care</div>')
    st.session_state.setdefault('care_audience', 'Patient')
    def change_audience():
        st.session_state.care_audience = st.session_state.care_audience_picker or 'Patient'
    visible = [0, 2, 3, 4, 5, 6] if clinician() else [0, 1, 4, 5]
    for index in visible:
        page = pages[index]
        label = {4: 'Find cancer care', 5: 'Find support'}.get(index, page.title) if not clinician() else page.title
        st.page_link(page, label=label, icon=page.icon, width='stretch')
    with st.expander('Settings'):
        st.segmented_control('View', ['Patient', 'Clinician'],
            default=st.session_state.care_audience, key='care_audience_picker',
            on_change=change_audience, selection_mode='single', width='stretch')
        interaction_controls()
        st.button('Clear workspace' if clinician() else 'Start over', key='portal_clear', on_click=clear_patient, icon=':material/restart_alt:')

navigation.run()
