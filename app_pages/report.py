import streamlit as st

from care_app.simple import home_link, report_page

home_link()
st.title('Understand a report')
st.radio('What kind of report do you have?', ['Scan or X-ray report', 'Gene test report'],
         key='care_report_kind')
report_page('genes' if st.session_state.care_report_kind == 'Gene test report' else 'radiology', show_title=False)
