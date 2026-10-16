"""Public introduction; no uploads, external model calls, or patient data."""
import streamlit as st

from prototype_core import ROOT

st.html('<style>' + (ROOT / 'care_app/welcome.css').read_text(encoding='utf-8') + '</style>')
st.html('''
<section class="welcome-hero" aria-labelledby="welcome-title">
  <div class="welcome-eyebrow">NEIL REWAL · CONGRESSIONAL APP CHALLENGE</div>
  <h1 id="welcome-title">Cancer Care.<br><span>A clearer picture.<br>A more informed next step.</span></h1>
  <p class="welcome-lead">From a gene report to the bigger picture: a student-built prototype
  connecting original cancer research, understandable report explanations and resources for care.</p>
  <div class="welcome-tags"><span>Original TMB research</span><span>Public cancer data</span><span>Patient &amp; clinician views</span></div>
  <div class="welcome-orbit" aria-hidden="true"><div class="welcome-orbit-core">+</div><span>GENES</span><span>IMAGING</span><span>CARE</span></div>
</section>
''')
left, right = st.columns([1, 1], gap='medium')
with left, st.container(border=True, key='care_card_welcome_demo'):
    st.subheader('See the idea in action')
    st.write('Explore three sample journeys, starting with public cancer data. No report or sign-in needed.')
    st.page_link(str(ROOT / 'integrated_report.py'), label='Explore the demo', icon=':material/arrow_forward:', width='stretch')
with right, st.container(border=True, key='care_card_welcome_reports'):
    st.subheader('Explore the report tools')
    st.write('See how gene reports and written imaging reports can become easier to understand and review.')
    st.page_link(str(ROOT / 'app_pages/genes.py'), label='Open gene reports', icon=':material/genetics:', width='stretch')

st.html('''<section class="welcome-story">
<div class="welcome-eyebrow">THE QUESTION BEHIND THE APP</div>
<h2>What if separate reports could tell a more connected story?</h2>
<p>Cancer information arrives in pieces. A gene report offers one perspective. Imaging adds another.
Clinical history and blood results add context. Cancer Care explores how these pieces could become
more useful together—for patients, families and the clinicians supporting them.</p>
</section>''')

st.subheader('One place to start exploring')
st.html('''<div class="welcome-features">
<article><span class="welcome-number">01 / GENES</span><h3>Start with the science</h3><p>Review a gene report and explore Neil’s 50-gene model for high or low mutation-burden study categories.</p></article>
<article><span class="welcome-number">02 / IMAGING</span><h3>Make the words clearer</h3><p>Explore explanations of written radiology findings, with questions to bring to a care-team conversation.</p></article>
<article><span class="welcome-number">03 / CARE &amp; SUPPORT</span><h3>Look beyond the report</h3><p>Organize a care profile, explore nearby treatment centers and discover the app’s support features.</p></article>
</div>''')

st.html('''<section class="welcome-research">
<div class="welcome-eyebrow">FROM RESEARCH TO A WORKING PROTOTYPE</div>
<h2>Built by Neil Rewal.<br>Grounded in curiosity, code and public evidence.</h2>
<p>This project began with Neil’s research into predicting tumor mutation burden using machine learning.
He then investigated public TCGA/GDC cancer records and published tools, including NCI’s LORIS,
to explore how the idea could grow beyond one model.</p>
<div class="welcome-facts"><div><strong>50 genes</strong><span>Original classifier inputs</span></div><div><strong>3 sample cases</strong><span>Public-data research journeys</span></div><div><strong>Python + Streamlit</strong><span>Working interactive prototype</span></div></div>
</section>''')
with st.expander('What is working today—and what comes next?'):
    st.write('Today: the original TMB classifier, AI-assisted report-image explanations, patient and clinician views, care resources, and a research workspace with public cases and experimental staging/pathway demonstrations.')
    st.write('The sample journeys use public genomic and clinical data plus clearly labeled simulated report extensions. LORIS was investigated as a possible future layer; this app does not currently produce a LORIS response score.')
    st.write('The larger vision is integrated diagnosis, staging and personalized treatment support. Next steps include matched real-world reports, independent evaluation and refinement with oncologist feedback.')
    st.caption('Uploaded images in the report tools are sent to OpenAI for explanation. Use de-identified demonstration material when exploring the prototype.')
st.caption('Research prototype · Not for clinical use. AI explanations and experimental results are for review, not medical decisions.')
