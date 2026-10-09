"""Run separately: streamlit run prototype.py. Research/simulated records only."""
import hashlib
import json
import pickle

import pandas as pd
import streamlit as st

from prototype_core import (ROOT, GENES, FIELDS, genomic_csv, inspect_report,
                            current_facts, commit_report, loris_readiness, export_summary)
from clinical_ui import clinical_panel

st.set_page_config(page_title='Cancer Care | From research to possibility', page_icon='◈', layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2rem;}
.hero {padding:2rem;border:1px solid #33586b;border-radius:22px;background:linear-gradient(120deg,#102b40,#132238 65%,#183e43);color:#edf7fc;margin-bottom:1.5rem;}
.hero .eyebrow {color:#77e5d4;font-size:.78rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;}
.hero h1 {color:#f4f8fc !important;font-size:2.65rem;line-height:1.12;margin:.6rem 0;max-width:800px;}
.hero p {color:#cbdce7;max-width:760px;font-size:1.05rem;}
.hero .pill {display:inline-block;padding:.35rem .7rem;border:1px solid #456170;border-radius:30px;font-size:.76rem;color:#cbdce7;margin-top:.5rem;}
div[data-testid="stMetric"] {background:rgba(128,128,128,.06);padding:16px;border-radius:14px;border:1px solid rgba(128,128,128,.28);}
button[role="tab"] {min-height:48px;}
@media (max-width:640px) {
 .block-container {padding:1rem;}
 .hero {padding:1.25rem;border-radius:16px;}
 .hero h1 {font-size:2rem !important;}
 div[data-testid="stMetric"] {padding:10px;}
}
</style>''', unsafe_allow_html=True)
CASES = json.loads((ROOT/'demo_data'/'cases.json').read_text())
PUBLIC = 'Public research case'
SIMULATED = 'Public case + explicitly simulated extension'

@st.cache_resource
def load_model():
    # Only the repository's trusted, fixed model is loaded. Never unpickle uploads.
    with (ROOT/'Best_Model_RF_50Trees_7Depth').open('rb') as handle:
        return pickle.load(handle)

def reset_case():
    keep = {k:st.session_state[k] for k in ['case_selector','mode_selector'] if k in st.session_state}
    for key in list(st.session_state):
        if key not in keep: del st.session_state[key]
    st.session_state.update(keep)

def append_document(doc):
    updated, changes = commit_report(st.session_state.documents, doc)
    st.session_state.documents = updated
    st.session_state.latest_changes = changes
    st.session_state.history.append({'source':doc['filename'],'changes':changes})

with st.sidebar:
    st.title('◈ Cancer Care')
    st.caption('BY NEIL REWAL · DEMO 0.4')
    st.markdown('**From one research question to a connected care vision.**')
    st.write('Start with the genes. Add the reports. Explore the bigger picture.')
    st.button('Start over', on_click=reset_case, width='stretch')
    with st.expander('About the evidence'):
        st.write('Research prototype—not for clinical use. The first clinical module covers gastric cancer; the broader vision extends beyond it.')
        st.write('TCGA/GDC supplies public mutation and clinical data. Original matched radiology and blood reports were not located; demo extensions are explicitly simulated. Clinical scenarios are separate from the historical patients.')
        st.write('The TMB classifier predicts the study category, not clinical mutations per megabase. These cases may overlap model development data. Staging and care pathways are experimental rules, with partial coverage.')
        st.write('Use public or simulated files only. This deployment is not prepared for private medical records. Files are processed in the app session without an external AI service.')
    st.link_button('Explore the original TMB app', 'https://tmbprediction-vmbvabws9cd5mbng4gftvp.streamlit.app/predictionapp')

st.markdown('''<section class="hero">
<div class="eyebrow">Neil Rewal · Congressional App Challenge prototype</div>
<h1>Three reports.<br>One connected picture of cancer care.</h1>
<p>A vision built from original TMB research, public cancer data and an exploration of published tools: connect the genes, the scans and the clinical context.</p>
<span class="pill">Research prototype · Not for clinical use</span>
</section>''', unsafe_allow_html=True)
st.subheader('Choose a patient journey')
st.caption('Three public research cases. Three opportunities to see how additional information changes the picture.')

def choose_patient(index):
    st.session_state.case_selector=index
    reset_case()

selection=st.session_state.setdefault('case_selector',0)
for i,col in enumerate(st.columns(3)):
    with col, st.container(border=True):
        st.markdown('### Patient '+['A','B','C'][i])
        st.write(str(CASES[i]['age'])+' years · Stomach cancer')
        st.caption(CASES[i]['historical_stage']+' in the historical record')
        st.button('Exploring this journey' if i==selection else 'Explore patient '+['A','B','C'][i],
                  key='journey_'+str(i),on_click=choose_patient,args=(i,),
                  type='primary' if i==selection else 'secondary',width='stretch')
mode = st.radio('Choose the experience', [SIMULATED,PUBLIC],
    format_func=lambda value:'Full demo · includes simulated reports' if value==SIMULATED else 'Public records only',
    key='mode_selector',on_change=reset_case,horizontal=True)
case = CASES[selection]
for key, default in [('documents',[]),('history',[]),('latest_changes',[]),('genomic',None)]:
    if key not in st.session_state: st.session_state[key] = default
st.caption('Public case: '+case['id']+' · Historical stage: AJCC 7'+
           (' · Added radiology/labs and the separate clinical scenario are simulated.' if mode==SIMULATED else ' · Missing reports remain unfilled.'))
with st.expander('Your 3-minute walkthrough'):
    st.write('**1 · Genes:** load the public gene CSV, review it and run Neil’s TMB model.')
    st.write('**2 · Imaging:** select a public clinical extract or a simulated radiology report; review and add it.')
    st.write('**3 · Labs:** add the simulated blood/history report to reveal more patient context.')
    st.write('**4 · Stage & care:** explore the separate fictional clinical scenario, review its inputs and see the reasoning behind matched pathways.')
    st.write('**5 · The full picture:** revisit the findings, their sources and the remaining questions. Explore **The research** to see what powers the prototype.')
    st.caption('Use Full demo for all steps. Changing patient or experience clears the workspace. On a phone, swipe the tab row.')

facts, conflicts = current_facts(st.session_state.documents)
cols = st.columns(3)
cols[0].metric('01 · Genomic signal', st.session_state.genomic['label'].replace(' study category','') if st.session_state.genomic else 'Not added')
cols[1].metric('02 · Disease context', str(sum(d['stage']=='imaging' for d in st.session_state.documents))+' reports added')
cols[2].metric('03 · Patient context', str(sum(d['stage']=='labs' for d in st.session_state.documents))+' reports added')
completed=sum([bool(st.session_state.genomic),any(d['stage']=='imaging' for d in st.session_state.documents),any(d['stage']=='labs' for d in st.session_state.documents)])
st.progress(completed/3,text=str(completed)+' of 3 evidence steps added')
tabs = st.tabs(['1 · Genes','2 · Imaging','3 · Labs','4 · Stage & care','5 · The full picture','The research'])

with tabs[0]:
    st.subheader('Start with the genomic signal')
    st.caption('ORIGINAL RESEARCH · 50-GENE TMB CLASSIFIER')
    st.write('Run Neil’s original random-forest model on a public mutation profile to reveal its high/low study category. This is a research classification, not measured clinical TMB.')
    file = ROOT/'demo_data'/(case['id']+'_genes.csv')
    a,b = st.columns([1,1])
    with a:
        use_example = st.button('Load example gene profile', key='load_genes',type='primary')
        with st.expander('Get the example file'):
            st.download_button('Download gene CSV',file.read_bytes(),file.name,'text/csv')
    with b:
        uploaded = st.file_uploader('Or upload a 50-gene CSV',type=['csv'],key='gene_upload')
    if use_example:
        st.session_state.gene_candidate=(file.name,file.read_bytes())
        st.session_state.genomic=None
    if uploaded is not None:
        digest=hashlib.sha256(uploaded.getvalue()).hexdigest()
        if st.session_state.get('gene_upload_seen')!=digest:
            st.session_state.gene_candidate=(uploaded.name,uploaded.getvalue())
            st.session_state.gene_upload_seen=digest
            st.session_state.genomic=None
    if st.session_state.get('gene_candidate'):
        name,data=st.session_state.gene_candidate
        try:
            frame=genomic_csv(data,single_patient=True)
            st.caption(name+' · checked against the exact training gene list and reordered safely')
            with st.expander('Review all 50 gene values'):
                st.dataframe(frame,hide_index=True)
            confirmed=st.checkbox('I confirm this CSV belongs to the selected case and all 50 gene statuses are known.',key='gene_confirm_'+hashlib.sha256(data).hexdigest())
            if st.button('Run TMB model',disabled=not confirmed,type='primary',key='run_model'):
                prediction=int(load_model().predict(frame.to_numpy())[0])
                st.session_state.genomic={'label':['Low study category','High study category'][prediction],
                    'source':name,'experimental':True,'case_id':case['id']}
                st.session_state.latest_changes=['Experimental TMB study classification added.']
                st.session_state.history.append({'source':name,'changes':st.session_state.latest_changes})
                st.rerun()
        except ValueError as exc: st.error(str(exc))
    if st.session_state.genomic:
        st.success('Experimental result: '+st.session_state.genomic['label'])
        st.caption('Prediction source: '+st.session_state.genomic['source'])
        with st.expander('How this result was produced'):
            st.write('Current GDC mutation calls were mapped to the study gene list and variant categories. The conversion is experimental, and these cases may overlap model development data.')
        st.info('Next: add imaging or pathology to explore the disease context beyond the genomic signal.')


def report_panel(stage):
    imaging=stage=='imaging'
    st.subheader('Add the disease context' if imaging else 'Add the person behind the reports')
    st.write('Bring imaging and pathology findings into the picture.' if imaging else 'Connect blood results and health history with the other findings.')
    st.caption('Upload public or simulated PDF/TXT reports. Review the suggested fields against the source; this step reads report text, not scan images.')
    example_names = [case['id']+'_clinical.txt'] if imaging else []
    if mode == SIMULATED:
        example_names += [case['id']+('_simulated_radiology.txt' if imaging else '_simulated_labs.txt')]
    if example_names:
        example = st.selectbox('Choose a report',example_names,key=stage+'_example',
            format_func=lambda name:'Public clinical record' if name.endswith('_clinical.txt') else ('Simulated radiology report' if 'radiology' in name else 'Simulated blood & history report'))
        example_bytes=(ROOT/'demo_data'/example).read_bytes()
        a,b=st.columns(2)
        with b.expander('Get the example file'):
            st.download_button('Download example report',example_bytes,example,'text/plain',key=stage+'_download')
        if a.button('Load example report',key=stage+'_load',type='primary'):
            st.session_state[stage+'_candidate']=(example,example_bytes)
    elif not imaging:
        st.info('No matched public blood report is available. Choose Full demo above to explore a simulated report.')
    up=st.file_uploader('Upload '+('radiology / pathology report' if imaging else 'blood report / history'),type=['pdf','txt'],key=stage+'_upload')
    if up is not None:
        digest=hashlib.sha256(up.getvalue()).hexdigest()
        if st.session_state.get(stage+'_upload_seen')!=digest:
            st.session_state[stage+'_candidate']=(up.name,up.getvalue())
            st.session_state[stage+'_upload_seen']=digest
    candidate=st.session_state.get(stage+'_candidate')
    if not candidate:
        added=[d for d in st.session_state.documents if d['stage']==stage]
        if added:
            st.success(str(len(added))+' report(s) connected to this patient picture.')
            st.caption('Next: '+('add Labs for more patient context.' if imaging else 'explore Stage & care, then The full picture.'))
        return
    name,data=candidate
    try:
        doc=inspect_report(data,name,case['id'],stage)
        if doc['simulated'] and mode == PUBLIC:
            st.error('This report is labeled simulated. Switch evidence mode before adding it.');return
    except ValueError as exc:st.error(str(exc));return
    if data == (ROOT/'demo_data'/(case['id']+'_clinical.txt')).read_bytes():
        doc['provenance']='Reconstructed public clinical data (not an original report)'
    st.caption('SIMULATED REPORT' if doc['simulated'] else 'PUBLIC / USER-SUPPLIED SOURCE · '+doc['provenance'])
    left,right=st.columns([1,1])
    with left:
        st.markdown('**Source text**')
        for page,text in enumerate(doc['pages'],1):
            st.caption('Page '+str(page));st.text(text)
    with right:
        st.markdown('**Confirm the extracted fields**')
        if not doc['fields']:st.info('No supported labeled fields found. You can add a field from the source below.')
        rows=pd.DataFrame(doc['fields'],columns=['field','value','page','excerpt'])
        edited=st.data_editor(rows,num_rows='dynamic',hide_index=True,width='stretch',
            column_config={'field':st.column_config.SelectboxColumn('Field',options=list(FIELDS),required=True),
                'value':st.column_config.TextColumn('Value',required=True),
                'page':st.column_config.NumberColumn('Page',min_value=1,max_value=len(doc['pages']),step=1,required=True),
                'excerpt':st.column_config.TextColumn('Exact supporting passage',required=True)},
            key=stage+'_editor_'+doc['id'])
        source_ok=st.checkbox('I checked these values and passages against the source and confirm the report belongs to this case.',key=stage+'_confirm_'+doc['id'])
        provenance=st.selectbox('Origin of this report',list(dict.fromkeys([doc['provenance'],'Simulated report'])),key=stage+'_origin_'+doc['id'])
        if st.button('Add confirmed report',key=stage+'_add',type='primary',disabled=not source_ok):
            try:
                if provenance=='Simulated report' and mode==PUBLIC:raise ValueError('Use simulated-extension mode for fictional data.')
                cleaned=[]
                for row in edited.to_dict('records'):
                    if row['field'] not in FIELDS or pd.isna(row['value']) or not str(row['value']).strip():raise ValueError('Every row needs a supported field and a value.')
                    if pd.isna(row['page']) or float(row['page'])!=int(row['page']):raise ValueError('Every field needs an integer source page.')
                    page=int(row['page'])
                    if page<1 or page>len(doc['pages']):raise ValueError('Source page is outside this document.')
                    excerpt=str(row['excerpt'])
                    if not excerpt.strip() or excerpt not in doc['pages'][page-1]:raise ValueError('Each supporting passage must appear exactly on its source page.')
                    cleaned.append({'field':row['field'],'value':str(row['value']).strip(),'page':page,'excerpt':excerpt})
                if not cleaned:raise ValueError('Add at least one supported field with its source passage.')
                if len({r['field'] for r in cleaned})!=len(cleaned):raise ValueError('Use each field once per report; retain ambiguity in its value.')
                if cleaned!=doc['fields']:provenance+='; user-reviewed edits'
                doc.update(fields=cleaned,provenance=provenance)
                append_document(doc)
                del st.session_state[stage+'_candidate']
                st.rerun()
            except ValueError as exc:st.error(str(exc))

with tabs[1]: report_panel('imaging')
with tabs[2]: report_panel('labs')
with tabs[3]: clinical_panel(case, mode == SIMULATED)

with tabs[4]:
    st.subheader('One view. Every finding connected to its source.')
    if st.session_state.genomic:
        st.success('Genomic signal · '+st.session_state.genomic['label']+' · Experimental prediction')
    assessment=st.session_state.get('clinical_result')
    if assessment:
        with st.container(border=True):
            st.caption(assessment['provenance'])
            st.markdown('**Clinical scenario · '+str(assessment['staging']['stage'] or 'Stage unresolved')+'**')
            for card in assessment['treatment']['cards']:st.write('• '+card['title'])
            st.caption('Experimental discussion pathways · See Stage & care for the inputs and reasoning.')
    facts,conflicts=current_facts(st.session_state.documents)
    if st.session_state.latest_changes:
        st.markdown('**What changed most recently**')
        for change in st.session_state.latest_changes:st.write('• '+change)
    if conflicts:st.error('Conflicting sources: '+', '.join(FIELDS[k] for k in conflicts)+'. These values are excluded from research-model inputs until resolved.')
    left,right=st.columns([1.3,1])
    with left:
        st.markdown('**Findings and their sources**')
        if not facts:st.info('Add and confirm a report to populate this view.')
        for key,row in facts.items():
            with st.expander(FIELDS[key]+': '+row['value'],expanded=key in ['diagnosis','stage']):
                st.caption(f"{row['filename']} · page {row['page']} · {row['provenance']}")
                st.text(row['excerpt'])
        st.markdown('**What each report contributes**')
        if 'diagnosis' in facts:
            st.write('A documented diagnosis is available. Histology, biomarkers, disease extent, prior treatment, general health, and patient preferences still need to be considered together.')
        if 'stage' in facts:
            st.write('The historical recorded stage is '+facts['stage']['value']+'. Open Stage & care for a separate calculation from confirmed assessment inputs.')
        if 'imaging_findings' in facts:
            st.write('Imaging information has been added. Uncertain findings remain uncertain and do not automatically change the recorded stage.')
        if any(k in facts for k in ['albumin','nlr','other_conditions','treatment_history']):
            st.write('Clinical context is now available alongside the genomic and disease findings.')
        st.markdown('Explore **4 · Stage & care** to connect confirmed assessment inputs with a calculated pathological stage and matched treatment discussion pathways.')
        st.link_button('NCI: stomach cancer treatment by stage','https://www.cancer.gov/types/stomach/treatment/by-stage')
    with right:
        st.markdown('**What is still unknown**')
        for key in ['diagnosis','stage','staging_edition','imaging_findings','age','albumin','nlr','measured_tmb','prior_systemic']:
            if key not in facts:st.write('• '+FIELDS[key])
        st.markdown('**Exploring LORIS · input readiness**')
        st.caption('Published NCI research explored for a future response-prediction layer. This prototype checks inputs; it does not run LORIS.')
        readiness=loris_readiness(facts,conflicts)
        for item in readiness['missing']:st.caption('Missing: '+item)
        for item in readiness['errors']:st.warning(item)
        if readiness['fields_present']:st.success('The six input fields are populated. Cancer-category mapping and clinical suitability still need confirmation.')
        with st.expander('Why no LORIS response score yet?'):
            st.write('The published repository and web calculator use different coefficients; version selection and calibration need resolution before integration. The high/low TMB study category cannot substitute for measured TMB.')
        st.link_button('View NCI LORIS research tool','https://loris.ccr.cancer.gov/')
    st.divider()
    st.download_button('Download appointment / research summary',export_summary(case,mode,st.session_state.genomic,st.session_state.documents,st.session_state.get('clinical_result')),case['id']+'_summary.txt','text/plain')
    with st.expander('Uploaded reports and change history'):
        for doc in list(st.session_state.documents):
            a,b=st.columns([4,1]);a.write(doc['filename']+' · '+doc['provenance'])
            if b.button('Remove',key='remove_'+doc['id']):
                st.session_state.documents=[d for d in st.session_state.documents if d['id']!=doc['id']]
                st.session_state.latest_changes=['Removed '+doc['filename']+'. The combined view has been recalculated.']
                st.session_state.history.append({'source':doc['filename'],'changes':st.session_state.latest_changes})
                st.rerun()
        for event in st.session_state.history:
            st.write(event['source']);st.caption(' | '.join(event['changes']))

with tabs[5]:
    st.subheader('Built from research. Designed around a bigger question.')
    st.write('What if the separate pieces of a cancer record could tell one connected story? Neil’s prototype starts with his own research and investigates how public evidence could support each next step.')
    for col,(label,title,body) in zip(st.columns(3),[
        ('01 · BUILT','Original TMB research','A 50-gene random-forest classifier predicts the study’s low/high mutation-burden category. The original model runs inside this app.'),
        ('02 · SOURCED','Real public cancer records','TCGA/GDC mutation and clinical data ground the three patient journeys. Public clinical extracts retain their historical stage and source.'),
        ('03 · INVESTIGATED','Published research, including LORIS','The NCI’s LORIS illustrates how multiple clinical variables can inform immunotherapy-response research. Here, input readiness is demonstrated; response scoring remains future work.')]):
        with col,st.container(border=True):
            st.caption(label);st.markdown('### '+title);st.write(body)
    st.markdown('### What powers each step?')
    st.dataframe(pd.DataFrame([
        {'Step':'Genes','Evidence':'Neil’s original model + public GDC mutation data','In this app':'Runs the research classifier'},
        {'Step':'Imaging / pathology','Evidence':'Public clinical extracts + labeled simulated radiology','In this app':'Reviews report text and tracks its sources'},
        {'Step':'Labs / history','Evidence':'Labeled simulated reports; LORIS input research','In this app':'Combines reviewed facts and checks input readiness'},
        {'Step':'Stage & care','Evidence':'Published staging / treatment sources + separate clinical scenarios','In this app':'Calculates experimental stages and matches discussion pathways'}
    ]),hide_index=True,width='stretch')
    st.markdown('### The next chapter')
    st.write('Expand the vision toward integrated diagnosis, staging and personalized treatment support: obtain matched reports, evaluate extraction and model performance independently, and refine the experience with oncologist feedback.')
    with st.expander('Data provenance and model boundaries'):
        st.write('The public cases come from TCGA/GDC. Their historical stages use AJCC 7. The separate clinical scenarios demonstrate AJCC 8 pathological gastric staging; they are not restaging of the historical cases.')
        st.write('The radiology and blood extensions are fictional. LORIS is a published research model/tool—not the source of these patient records. No LORIS response score is generated here. Model development overlap is possible for the TMB examples.')
    a,b=st.columns(2)
    a.link_button('Explore NCI Genomic Data Commons','https://portal.gdc.cancer.gov/')
    b.link_button('Explore the NCI LORIS research tool','https://loris.ccr.cancer.gov/')
