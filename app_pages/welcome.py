"""Public introduction and audience selection."""
import streamlit as st
from prototype_core import ROOT

st.html('<style>' + (ROOT / 'care_app/welcome.css').read_text(encoding='utf-8') + '</style>')
st.html('''
<section class="welcome-hero" aria-labelledby="welcome-title">
  <div class="welcome-dna"><svg viewBox="0 0 320 290" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><radialGradient id="dna-halo"><stop stop-color="#63ded0" stop-opacity=".22"/><stop offset="1" stop-color="#63ded0" stop-opacity="0"/></radialGradient></defs><circle cx="160" cy="145" r="140" fill="url(#dna-halo)"/><line x1="160.0" y1="25" x2="160.0" y2="25" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="195.8" y1="41" x2="124.2" y2="41" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="218.5" y1="57" x2="101.5" y2="57" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="219.7" y1="73" x2="100.3" y2="73" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="199.0" y1="89" x2="121.0" y2="89" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="164.0" y1="105" x2="156.0" y2="105" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="127.5" y1="121" x2="192.5" y2="121" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="103.0" y1="137" x2="217.0" y2="137" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="99.4" y1="153" x2="220.6" y2="153" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="118.0" y1="169" x2="202.0" y2="169" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="152.1" y1="185" x2="167.9" y2="185" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="189.0" y1="201" x2="131.0" y2="201" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="215.3" y1="217" x2="104.7" y2="217" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="221.3" y1="233" x2="98.7" y2="233" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="204.8" y1="249" x2="115.2" y2="249" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><line x1="171.9" y1="265" x2="148.1" y2="265" stroke="#b4f1e7" stroke-opacity=".5" stroke-width="4" stroke-linecap="round"/><polyline points="160.00,25 164.77,27 169.50,29 174.18,31 178.78,33 183.27,35 187.61,37 191.80,39 195.80,41 199.58,43 203.13,45 206.43,47 209.45,49 212.18,51 214.60,53 216.69,55 218.45,57 219.87,59 220.93,61 221.63,63 221.97,65 221.94,67 221.54,69 220.78,71 219.66,73 218.19,75 216.37,77 214.22,79 211.74,81 208.97,83 205.90,85 202.56,87 198.97,89 195.14,91 191.11,93 186.90,95 182.53,97 178.02,99 173.41,101 168.72,103 163.97,105 159.21,107 154.44,109 149.71,111 145.04,113 140.46,115 136.00,117 131.68,119 127.52,121 123.56,123 119.81,125 116.30,127 113.05,129 110.08,131 107.40,133 105.03,135 102.99,137 101.29,139 99.93,141 98.93,143 98.29,145 98.01,147 98.10,149 98.56,151 99.38,153 100.56,155 102.09,157 103.97,159 106.17,161 108.70,163 111.53,165 114.64,167 118.02,169 121.66,171 125.51,173 129.58,175 133.82,177 138.21,179 142.74,181 147.37,183 152.07,185 156.82,187 161.59,189 166.35,191 171.07,193 175.73,195 180.29,197 184.73,199 189.03,201 193.15,203 197.08,205 200.79,207 204.26,209 207.47,211 210.39,213 213.02,215 215.33,217 217.32,219 218.97,221 220.26,223 221.21,225 221.78,227 222.00,229 221.85,231 221.33,233 220.45,235 219.21,237 217.62,239 215.69,241 213.43,243 210.85,245 207.97,247 204.81,249 201.39,251 197.72,253 193.82,255 189.73,257 185.46,259 181.04,261 176.49,263 171.85,265 167.14,267 162.38,269" fill="none" stroke="#83e5d4" stroke-width="7" stroke-linecap="round"/><polyline points="160.00,25 155.23,27 150.50,29 145.82,31 141.22,33 136.73,35 132.39,37 128.20,39 124.20,41 120.42,43 116.87,45 113.57,47 110.55,49 107.82,51 105.40,53 103.31,55 101.55,57 100.13,59 99.07,61 98.37,63 98.03,65 98.06,67 98.46,69 99.22,71 100.34,73 101.81,75 103.63,77 105.78,79 108.26,81 111.03,83 114.10,85 117.44,87 121.03,89 124.86,91 128.89,93 133.10,95 137.47,97 141.98,99 146.59,101 151.28,103 156.03,105 160.79,107 165.56,109 170.29,111 174.96,113 179.54,115 184.00,117 188.32,119 192.48,121 196.44,123 200.19,125 203.70,127 206.95,129 209.92,131 212.60,133 214.97,135 217.01,137 218.71,139 220.07,141 221.07,143 221.71,145 221.99,147 221.90,149 221.44,151 220.62,153 219.44,155 217.91,157 216.03,159 213.83,161 211.30,163 208.47,165 205.36,167 201.98,169 198.34,171 194.49,173 190.42,175 186.18,177 181.79,179 177.26,181 172.63,183 167.93,185 163.18,187 158.41,189 153.65,191 148.93,193 144.27,195 139.71,197 135.27,199 130.97,201 126.85,203 122.92,205 119.21,207 115.74,209 112.53,211 109.61,213 106.98,215 104.67,217 102.68,219 101.03,221 99.74,223 98.79,225 98.22,227 98.00,229 98.15,231 98.67,233 99.55,235 100.79,237 102.38,239 104.31,241 106.57,243 109.15,245 112.03,247 115.19,249 118.61,251 122.28,253 126.18,255 130.27,257 134.54,259 138.96,261 143.51,263 148.15,265 152.86,267 157.62,269" fill="none" stroke="#85bfea" stroke-width="7" stroke-linecap="round"/></svg></div>
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
