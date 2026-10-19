import streamlit as st

from prototype_core import ROOT

st.title('How can we help?')
for title, description, page, icon in [
    ('Understand a report', 'Read your medical report in simple words.', 'app_pages/report.py', 'description'),
    ('Find cancer care', 'Find treatment centers near you.', 'app_pages/patient.py', 'local_hospital'),
    ('Find support', 'Talk with someone or find a support group.', 'app_pages/community.py', 'groups'),
]:
    with st.container(border=True, key='care_card_start_' + icon):
        st.page_link(str(ROOT / page), label=title, icon=':material/' + icon + ':', width='stretch')
        st.write(description)
