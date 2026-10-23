"""Run with: streamlit run prototype.py."""
from html import escape
from pathlib import Path

import streamlit as st

from care_app.state import clear_patient, initialize
from care_app.ui import apply_theme

st.set_page_config(page_title='Cancer Care', page_icon=':material/ecg_heart:', layout='wide')
initialize()
apply_theme()
ROOT = Path(__file__).resolve().parent

pages = [
    st.Page(ROOT / 'app_pages/welcome.py', title='Welcome', icon=':material/home:', default=True),
    st.Page(ROOT / 'app_pages/genes.py', title='Gene report', icon=':material/genetics:', url_path='genes'),
    st.Page(ROOT / 'app_pages/radiology.py', title='Imaging', icon=':material/radiology:', url_path='radiology'),
    st.Page(ROOT / 'app_pages/patient.py', title='My care', icon=':material/local_hospital:', url_path='patient'),
    st.Page(ROOT / 'app_pages/community.py', title='Support', icon=':material/groups:', url_path='community'),
    st.Page(ROOT / 'app_pages/cancer_basics.py', title='Cancer Basics', icon=':material/menu_book:', url_path='cancer-basics'),
    st.Page(ROOT / 'app_pages/about_research.py', title='My Research & Sources', icon=':material/science:', url_path='about-research'),
    st.Page(ROOT / 'integrated_report.py', title='Research workspace', icon=':material/science:', url_path='research'),
]
navigation = st.navigation(pages, position='hidden')

if navigation.url_path != '':
    with st.sidebar:
        st.html('<div class="care-brand"><span class="care-mark" aria-hidden="true">+</span>Cancer Care</div>')
        st.session_state.setdefault('care_audience', 'Patient')
        def change_audience():
            st.session_state.care_audience = st.session_state.care_audience_picker or 'Patient'
        st.session_state.setdefault('care_audience_picker', st.session_state.care_audience)
        st.segmented_control('View', ['Patient', 'Clinician'],
            key='care_audience_picker',
            on_change=change_audience, selection_mode='single', width='stretch', label_visibility='collapsed')
        with st.container(key='sidebar_welcome'):
            st.page_link(pages[0], label='WELCOME', icon=pages[0].icon, width='stretch')
        st.html('<div class="sidebar-steps-heading">YOUR FOUR STEPS</div>')
        labels = ['1. GENE REPORT & TMB', '2. RADIOLOGY REPORT', '3. FIND CANCER CARE', '4. COMMUNITY & SUPPORT']
        with st.container(key='journey_steps'):
            for page, label in zip(pages[1:5], labels):
                st.page_link(page, label=label, icon=page.icon, width='stretch')
        st.divider()
        st.page_link(pages[5], label='Cancer Basics', icon=pages[5].icon, width='stretch')
        st.page_link(pages[6], label='My Research & Sources', icon=pages[6].icon, width='stretch')
        st.divider()
        patient = st.session_state.portal_patient
        name = patient['alias'] or 'My workspace'
        st.html('<div class="care-session"><span class="care-avatar">' + escape(name[0].upper()) + '</span>' + escape(name) + '</div>')
        st.button('Clear workspace', key='portal_clear', on_click=clear_patient, icon=':material/restart_alt:')
# Start the community page with choices only on each new visit.
if st.session_state.get('support_last_page') != navigation.url_path:
    if navigation.url_path == 'community':
        st.session_state.support_section = None
        st.session_state.pop('support_next_action', None)
    st.session_state.support_last_page = navigation.url_path
navigation.run()
