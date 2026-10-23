"""Public introduction and audience selection."""
import streamlit as st
import base64
from prototype_core import ROOT

st.html('<style>' + (ROOT / 'care_app/welcome.css').read_text(encoding='utf-8') + '</style>')
hero_image = base64.b64encode((ROOT / 'care_app/assets/cancer_ml.jpg').read_bytes()).decode('ascii')
st.html('''
<section class="welcome-hero" aria-labelledby="welcome-title">
  <div class="welcome-dna"><img src="data:image/jpeg;base64,''' + hero_image + '''" alt="Illustration of a cancer cell connecting to a machine-learning network" style="width:100%;height:auto;border-radius:22px;display:block;" /></div>
  <div class="welcome-eyebrow">NEIL REWAL · CONGRESSIONAL APP CHALLENGE</div>
  <h1 id="welcome-title">Cancer Care<span>It started with my grandmother.</span></h1>
  <p class="welcome-lead">When my grandmother was diagnosed with cancer, she felt lost. So did we.<br>We kept coming back to three questions.</p>
  <div class="welcome-questions">
    <article><span>01 / TREATMENT</span><h2>Which treatment would be right for her?</h2></article>
    <article><span>02 / REPORTS</span><h2>What do all these reports mean?</h2></article>
    <article><span>03 / SUPPORT</span><h2>Where can she find support?</h2></article>
  </div>
</section>
<section class="welcome-story">
  <h2>I wanted to help.</h2>
  <p class="welcome-research-lead">The first question led me to research how machine learning could predict tumor mutation burden—a clue that can help doctors consider immunotherapy. That research became the starting point for Cancer Care.</p>
  <p>I built Cancer Care to help my family—and other families facing cancer—find answers to those same three questions.</p>
</section>
''')
st.subheader('Choose your view to get started')
def choose_view(audience):
    st.session_state.care_audience = audience
    st.session_state.care_audience_picker = audience

patient, clinician = st.columns(2, gap='medium')
with patient:
    if st.button('EXPLORE AS A PATIENT', icon=':material/person:', type='primary', width='stretch', on_click=choose_view, args=('Patient',), key='welcome_patient'):
        st.switch_page(str(ROOT / 'app_pages/genes.py'))
    st.caption('For patients and families: clear explanations, care and support.')
with clinician:
    if st.button('EXPLORE AS A CLINICIAN', icon=':material/stethoscope:', width='stretch', on_click=choose_view, args=('Clinician',), key='welcome_clinician'):
        st.switch_page(str(ROOT / 'app_pages/genes.py'))
    st.caption('For clinicians: review the findings and supporting details.')
st.page_link(str(ROOT / 'app_pages/about_research.py'), label='My Research & Sources', icon=':material/science:')
st.caption('Built by Neil Rewal · Student research prototype. Review results with your care team.')
