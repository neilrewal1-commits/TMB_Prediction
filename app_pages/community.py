import streamlit as st

from care_app.ui import header, words
from html import escape

st.caption('STEP 4 OF 4 · COMMUNITY & SUPPORT')
header('You’re not alone.', 'Community & patient support')
st.html('<section class="gene-research"><span class="gene-eyebrow">FIND YOUR COMMUNITY</span>'
        '<h2>There are people you can turn to.</h2>'
        '<p>Meet others facing cancer, talk with a support navigator, or get help understanding cancer tests. For you and the people who care about you.</p></section>')


st.html("""<style>
[class*="st-key-support_choice_"] {
    background: linear-gradient(145deg, #ffffff, #eaf4f7);
    border: 1px solid #bed4de !important;
    border-top: 5px solid #078480 !important;
    border-radius: 20px !important;
    padding: 24px 18px !important;
}
.support-card-title {
    text-align: center; color: #163d50; font-size: 1.65rem !important;
    font-weight: 850 !important; line-height: 1.2 !important;
    min-height: 4rem; display: flex; align-items: center; justify-content: center;
    margin: 0 0 14px !important;
}
.support-card-copy { text-align: center; color: #345365; font-size: 1.08rem;
    line-height: 1.5; min-height: 5rem; margin: 0 0 10px; }
[class*="st-key-support_choice_"] button { min-height: 58px; }
[class*="st-key-support_choice_"] button p { font-size: 1rem !important; font-weight: 800 !important; }
.support-section-title { text-align: center; font-size: 1.7rem !important;
    font-weight: 850 !important; color: #163d50; margin: 24px 0 !important; }
@media(max-width:700px) {
    .support-card-title,.support-card-copy { min-height: 0; }
}
</style>""")

st.session_state.setdefault('support_section', 'CONNECT WITH OTHERS')
choices = [
    ('CONNECT WITH OTHERS', 'A shared experience', 'Explore connections with patients, caregivers and families.', ':material/groups:'),
    ('FIND SUPPORT', 'Someone to talk to', 'Find a support group or speak with a community navigator.', ':material/support_agent:'),
    ('UNDERSTAND RESULTS', 'Make sense of the words', 'Learn about cancer tests and prepare your questions.', ':material/menu_book:'),
]
for col, (label, title, description, icon) in zip(st.columns(3), choices):
    with col, st.container(border=True, key='support_choice_' + label.split()[0].lower()):
        st.html('<h3 class="support-card-title">' + escape(title) + '</h3><p class="support-card-copy">' + escape(description) + '</p>')
        if st.button(label, key='support_nav_' + label, icon=icon, width='stretch',
                     type='primary' if st.session_state.support_section == label else 'secondary'):
            st.session_state.support_section = label
            st.rerun()

section = st.session_state.support_section
if section == 'CONNECT WITH OTHERS':
    st.subheader('FIND PEOPLE WHO CAN RELATE')
    st.caption('Connection preview · Fictional profiles for the demo. No messages are sent.')
    left, right = st.columns(2)
    experience = left.selectbox('Connect with', ['Everyone', 'Patients', 'Caregivers & family'], key='support_experience')
    scope = right.selectbox('Community', ['Local · East Bay demo', 'National · United States', 'Global · Online'], key='support_scope')
    profiles = [
        ('maya', 'Maya', 'Caregivers & family', 'East Bay, California', 'Local', 'Caring for a patient', 'I’d like to share ways to support a parent and make time for myself.'),
        ('alex', 'Alex', 'Patients', 'East Bay, California', 'Local', 'Living with cancer', 'Looking for people to talk with about the everyday parts of treatment.'),
        ('jordan', 'Jordan', 'Caregivers & family', 'Chicago, United States', 'National', 'Supporting a partner', 'Hoping to connect with other families and share questions for appointments.'),
        ('sam', 'Sam', 'Patients', 'London, United Kingdom', 'Global', 'Life after treatment', 'Interested in sharing experiences and finding encouragement along the way.'),
    ]
    allowed = {'Local · East Bay demo': {'Local'}, 'National · United States': {'Local', 'National'}, 'Global · Online': {'Local', 'National', 'Global'}}[scope]
    matches = [p for p in profiles if p[4] in allowed and (experience == 'Everyone' or p[2] == experience)]
    for i, profile in enumerate(matches):
        ident, name, role, region, level, title, story = profile
        with st.container(border=True, key='care_card_demo_' + ident):
            text, action = st.columns([3, 1], vertical_alignment='center')
            with text:
                st.subheader(name + ' · ' + title)
                st.caption(role + ' · ' + region + ' · Sample profile')
                st.write(story)
            with action:
                request_key = 'support_demo_request_' + ident
                if st.button('REQUEST TO CONNECT', key='request_' + ident, width='stretch', disabled=st.session_state.get(request_key, False)):
                    st.session_state[request_key] = True
                    st.rerun()
            if st.session_state.get(request_key):
                st.success('Demo request saved. In a member community, the other person would choose whether to accept.')
                if st.button('UNDO DEMO REQUEST', key='undo_' + ident):
                    st.session_state.pop(request_key, None)
                    st.rerun()
    st.caption('The local preview uses East Bay examples, not your location. Member connections depend on people choosing to join and share their profiles.')
    with st.expander('Explore the existing member community'):
        st.write('The prototype also has opt-in profiles and connection requests. Use sample details while testing.')
        if st.toggle('Open member sign-in', key='portal_community_show'):
            from care_app.community_ui import render_community
            render_community()

elif section == 'FIND SUPPORT':
    st.html('<h2 class="support-section-title">You don’t have to figure it out by yourself.</h2>')
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader('Talk with a navigator')
        st.write('Cancer Support Community SF Bay Area offers navigation to help patients and families find counseling, support groups and practical resources.')
        st.link_button('SPEAK WITH A NAVIGATOR', 'https://cancersupport.net/services/navigation/', type='primary', width='stretch')
        st.caption('SF Bay Area · Request contact through the navigation interest form')
        st.markdown('**National CSC helpline:** [888-793-9355](tel:+18887939355)')
        with st.expander('Website not opening?'):
            st.write('Copy this address into Safari or Chrome:')
            st.code('https://cancersupport.net/services/navigation/', language=None)
    with right, st.container(border=True):
        st.subheader('Find your support group')
        st.write('Explore in-person and online programs for people with cancer, survivors, caregivers and families.')
        st.link_button('EXPLORE SUPPORT GROUPS', 'https://www.cancersupportcommunity.org/find-location-near-you', type='primary', width='stretch')
        st.caption('Cancer Support Community · Find a local center and its programs')
        st.markdown('[Bay Area support programs](https://cancersupport.net/services/)')
        with st.expander('Website not opening?'):
            st.write('Copy this address into Safari or Chrome:')
            st.code('https://www.cancersupportcommunity.org/find-location-near-you', language=None)
    with st.container(border=True):
        st.subheader('Looking for professional emotional support?')
        st.write('Ask your care team or a navigator to help you find an oncology social worker, counselor, psychologist or psychiatrist. Peer groups offer connection; professional care offers individual support.')

else:
    st.subheader('UNDERSTAND MORE. ASK WITH CONFIDENCE.')
    st.write('Use these National Cancer Institute resources to understand terms from your reports and prepare for a conversation with your care team.')
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader('What do cancer tests tell us?')
        st.write('Learn how biomarkers can inform treatment discussions and why different tests answer different questions.')
        st.link_button('EXPLORE BIOMARKER TESTING', 'https://www.cancer.gov/about-cancer/treatment/types/biomarker-testing-cancer-treatment', type='primary', width='stretch')
    with right, st.container(border=True):
        st.subheader('Ask a cancer information specialist')
        st.write('Contact NCI for understandable information about cancer, treatments and clinical trials.')
        st.link_button('CONTACT NCI', 'https://www.cancer.gov/contact', type='primary', width='stretch')
    st.caption('These links open educational resources. Your reports are not uploaded or sent to these organizations.')
    with st.container(border=True):
        st.subheader('TAKE THESE QUESTIONS TO YOUR CARE TEAM')
        st.markdown('- What does this finding mean for me?\n- How do my gene and scan findings fit together?\n- What other information do we need before deciding on treatment?\n- Who can help my family with emotional and practical support?')

st.divider()
st.markdown('### Clearer information. Care you can reach. People you can turn to.')
