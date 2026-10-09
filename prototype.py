"""Run separately: streamlit run prototype.py. Research/simulated records only."""
import hashlib
import json
import pickle

import pandas as pd
import streamlit as st

from prototype_core import (ROOT, GENES, FIELDS, genomic_csv, inspect_report,
                            current_facts, commit_report, loris_readiness, export_summary)
from clinical_ui import clinical_panel

st.set_page_config(page_title='Cancer Care | Research Prototype', page_icon='◈', layout='wide')
st.markdown('''<style>
.stApp {background: #f7f9fc;} h1,h2,h3 {color:#14344a;}
div[data-testid="stMetric"] {background:white;padding:16px;border-radius:10px;border:1px solid #dce5ea;}
.block-container {max-width:1200px;padding-top:2rem;}
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
    st.title('Cancer Care')
    st.caption('RESEARCH PROTOTYPE · VERSION 0.2')
    selection = st.selectbox('Explore a patient', range(len(CASES)),
                            format_func=lambda i:CASES[i]['label'], key='case_selector', on_change=reset_case)
    mode = st.radio('Evidence mode', [PUBLIC,SIMULATED], key='mode_selector', on_change=reset_case)
    st.caption('Switching patient or mode clears the current workspace.')
    st.button('Reset this workspace', on_click=reset_case, width='stretch')
    st.divider()
    st.markdown('**About this version**')
    st.caption('Upload public research or simulated records only. Files are processed in this app session, with no external AI service. This build is not prepared to accept private clinical records.')
    st.link_button('Original TMB research app', 'https://tmbprediction-vmbvabws9cd5mbng4gftvp.streamlit.app/predictionapp')

case = CASES[selection]
for key, default in [('documents',[]),('history',[]),('latest_changes',[]),('genomic',None)]:
    if key not in st.session_state: st.session_state[key] = default

st.title('See how the reports connect')
st.write('Add genomic information, imaging and pathology, then labs and history. Review each source before it enters the combined view.')
st.caption(f"{case['id']} · {case['description']}")
if mode == SIMULATED:
    st.warning('SIMULATED EXTENSION: any added fictional imaging or lab values are demonstration inputs, not facts about this TCGA patient. This label remains in exports.')
else:
    st.info('Public research data. Original radiology reports and matched blood values have not been located. Unknown fields remain unknown.')

facts, conflicts = current_facts(st.session_state.documents)
cols = st.columns(3)
cols[0].metric('1 · Genomics', 'Added' if st.session_state.genomic else 'Awaiting input')
cols[1].metric('2 · Imaging / pathology', str(sum(d['stage']=='imaging' for d in st.session_state.documents))+' reports')
cols[2].metric('3 · Labs / history', str(sum(d['stage']=='labs' for d in st.session_state.documents))+' reports')
tabs = st.tabs(['1  Genomics','2  Imaging & pathology','3  Labs & history','Combined view','4  Staging & treatment'])

with tabs[0]:
    st.subheader('Your TMB research model')
    st.write('The original 50-gene random forest runs here. Its output is the study’s high/low mutation-burden category, not a clinical mutations-per-megabase measurement.')
    file = ROOT/'demo_data'/(case['id']+'_genes.csv')
    a,b = st.columns([1,1])
    with a:
        st.download_button('Download this case’s gene CSV',file.read_bytes(),file.name,'text/csv')
        use_example = st.button('Load this case’s gene CSV', key='load_genes')
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
        st.caption('Current GDC mutation calls were mapped using the study variant categories. This conversion is experimental; these TCGA cases may overlap model development data.')


def report_panel(stage):
    imaging=stage=='imaging'
    st.subheader('Review what the report says')
    st.caption('PDF text and TXT are supported. Automatic suggestions recognize labeled fields; they do not diagnose cancer or interpret scan pixels. Review the source and add missing fields explicitly.')
    example_names = [case['id']+'_clinical.txt'] if imaging else []
    if mode == SIMULATED:
        example_names += [case['id']+('_simulated_radiology.txt' if imaging else '_simulated_labs.txt')]
    if example_names:
        example = st.selectbox('Example report',example_names,key=stage+'_example')
        example_bytes=(ROOT/'demo_data'/example).read_bytes()
        a,b=st.columns(2)
        a.download_button('Download example report',example_bytes,example,'text/plain',key=stage+'_download')
        if b.button('Load example for review',key=stage+'_load'):
            st.session_state[stage+'_candidate']=(example,example_bytes)
    elif not imaging:
        st.info('No matched blood report has been established for this real case. Switch to simulated-extension mode to demonstrate a fictional lab upload.')
    up=st.file_uploader('Upload '+('radiology / pathology report' if imaging else 'blood report / history'),type=['pdf','txt'],key=stage+'_upload')
    if up is not None:
        digest=hashlib.sha256(up.getvalue()).hexdigest()
        if st.session_state.get(stage+'_upload_seen')!=digest:
            st.session_state[stage+'_candidate']=(up.name,up.getvalue())
            st.session_state[stage+'_upload_seen']=digest
    candidate=st.session_state.get(stage+'_candidate')
    if not candidate:return
    name,data=candidate
    try:
        doc=inspect_report(data,name,case['id'],stage)
        if doc['simulated'] and mode == PUBLIC:
            st.error('This report is labeled simulated. Switch evidence mode before adding it.');return
    except ValueError as exc:st.error(str(exc));return
    if data == (ROOT/'demo_data'/(case['id']+'_clinical.txt')).read_bytes():
        doc['provenance']='Reconstructed public clinical data (not an original report)'
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
with tabs[4]: clinical_panel(case, mode == SIMULATED)

with tabs[3]:
    st.subheader('The combined picture')
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
        st.markdown('**Treatment discussion**')
        if 'diagnosis' in facts:
            st.write('A documented diagnosis is available. Histology, biomarkers, disease extent, prior treatment, general health, and patient preferences still need to be considered together.')
        if 'stage' in facts:
            st.write('The recorded stage is '+facts['stage']['value']+'. Its source and staging edition matter; this app has not independently assigned or updated the stage.')
        if 'imaging_findings' in facts:
            st.write('Imaging information has been added. Uncertain findings remain uncertain and do not automatically change the recorded stage.')
        if any(k in facts for k in ['albumin','nlr','other_conditions','treatment_history']):
            st.write('Clinical context is now available for review. This version does not infer treatment suitability or drug doses from these values.')
        st.markdown('Open **4 · Staging & treatment** to calculate a pathological stage from confirmed findings and match experimental treatment discussion options. That workspace requires explicit assessment inputs and keeps fictional scenarios separate from this report profile.')
        st.link_button('NCI: stomach cancer treatment by stage','https://www.cancer.gov/types/stomach/treatment/by-stage')
    with right:
        st.markdown('**What is still unknown**')
        for key in ['diagnosis','stage','staging_edition','imaging_findings','age','albumin','nlr','measured_tmb','prior_systemic']:
            if key not in facts:st.write('• '+FIELDS[key])
        st.markdown('**LORIS research inputs**')
        readiness=loris_readiness(facts,conflicts)
        for item in readiness['missing']:st.caption('Missing: '+item)
        for item in readiness['errors']:st.warning(item)
        if readiness['fields_present']:st.success('The six input fields are populated. Cancer-category mapping and clinical suitability still need confirmation.')
        st.info('No response percentage is issued. The published repository and web calculator use different coefficients; version selection and calibration are still under review.')
        st.caption('Your experimental high/low TMB result cannot fill the measured-TMB field.')
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

st.caption('Full vision: integrated diagnosis, staging and personalized treatment support. This build includes the original research model, reviewed reports and experimental gastric staging / treatment rules. It has not been clinically validated.')
