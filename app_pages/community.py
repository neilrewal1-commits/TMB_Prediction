import streamlit as st

from care_app.ui import header, words

header('Support for you', 'Patient support resources')
resources = [
    ('groups', words('Find your community', 'Support programs'),
     words('Connect with support groups online or near you.', 'Patient, survivor, and caregiver support programs.'),
     'Find support', 'https://www.cancersupportcommunity.org/get-support'),
    ('forum', words('Talk to someone', 'Support navigation'),
     words('Speak with a Cancer Support Community navigator.', 'Cancer Support Community navigation and resource specialists.'),
     'Get in touch', 'https://www.cancersupportcommunity.org/cancer-support-helpline'),
    ('genetics', words('Understand your test results', 'Biomarker testing resources'),
     words('Learn about cancer tests from the National Cancer Institute.', 'NCI resources on tumor biomarkers and molecular testing.'),
     'Explore cancer tests', 'https://www.cancer.gov/about-cancer/treatment/types/biomarker-testing-cancer-treatment'),
]
for icon, title, description, label, url in resources:
    with st.container(border=True, key='care_card_support_' + icon):
        text, action = st.columns([2.5, 1], vertical_alignment='center')
        with text:
            st.subheader(title, anchor=False)
            st.write(description)
        action.link_button(label, url, icon=':material/arrow_outward:', width='stretch')

if st.toggle('Connect with peers in this app', key='portal_community_show'):
    from care_app.community_ui import render_community
    render_community()
