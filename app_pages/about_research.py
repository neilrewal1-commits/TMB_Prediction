"""Research history and evidence, separate from the guided care journey."""
import streamlit as st
from prototype_core import ROOT

st.title('My Research & Sources')
st.write('Cancer Care began with my research into predicting tumor mutation burden using machine learning. This page keeps the science, sources and earlier iterations together as the app develops.')
st.subheader('1. Original TMB research')
st.write('The original classifier uses mutation features from 50 genes to predict high or low study-defined mutation-burden categories. These research categories are not a clinical treatment recommendation.')
st.subheader('2. Public data and tools I investigated')
st.markdown('''- **cBioPortal and TCGA/GDC:** public cancer genomic and clinical records used in the research and earlier sample journeys.
- **NCI’s LORIS:** investigated as a possible future layer. Cancer Care does not currently calculate a LORIS response score.
- **Python and Streamlit:** the tools behind this interactive prototype.''')
st.subheader('3. Earlier prototype iterations')
st.write('The earlier research workspace contains three public-data sample journeys, simulated radiology and blood-report extensions, and experimental staging and pathway demonstrations. It remains available here to show how the project evolved.')
st.page_link(str(ROOT / 'integrated_report.py'), label='Explore the earlier research workspace', icon=':material/science:')
st.subheader('4. The current journey')
st.write('Gene report and TMB → Radiology report → Find cancer care → Find support. Patient and clinician views provide different ways to review the information.')
st.subheader('What comes next')
st.write('Matched real-world reports, independent evaluation and feedback from oncologists. The longer-term vision is to study how combined information could support more personalized cancer care.')
st.caption('Research prototype · Not for clinical use. Earlier report extensions are labeled as simulated; they are not matched real patient reports.')
