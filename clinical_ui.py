"""Human-reviewed assessment workspace; simulation is explicitly segregated."""
import hashlib
import json

import streamlit as st

from clinical_rules import DEPTHS, VERSION, NCI, derive_components, stage_group, treatment_pathways
from care_app.ui import badge

def clinical_panel(case, simulated_mode):
    st.subheader('Pathological stage and treatment pathways')
    with st.expander('Staging schema'):
        st.write('Gastric adenocarcinoma · AJCC 8 · pathological staging · no neoadjuvant therapy')
    if simulated_mode:
        badge('Fictional clinical scenario')
        if st.button('Load sample assessment',key='clinical_demo',type='primary'):
            i=['TCGA-VQ-A8DL','TCGA-VQ-A8DU','TCGA-VQ-A8DZ'].index(case['id'])
            values={'site':'Gastric adenocarcinoma','basis':'Pathological','edition':'AJCC 8','neoadjuvant':'No',
                'depth':['Subserosa without serosal or adjacent-organ invasion','Serosa','Subserosa without serosal or adjacent-organ invasion'][i],
                'positive':[0,3,1][i],'examined':[18,20,18][i],'m':['M0','M0','M1'][i],
                'age':[69,63,70][i],'setting':['After surgery','After surgery','Advanced — first line'][i],
                'fitness':'Reviewed for combination therapy','immune_review':'Reviewed — no flagged concern',
                'metastatic':['No','No','Yes'][i],'unresectable':['No','No','Yes'][i],
                'prior_advanced':'No','prior_episode':'Yes','her2':['Unknown','Unknown','Positive'][i],
                'cps':None if i<2 else 5.0,'cldn':'Unknown','msi':'Unknown','symptoms':'No',
                'same_episode':True,'source':'Fictional scenario '+['A','B','C'][i]+'. Staging, biomarkers, and fitness inputs are simulated.'}
            for key,value in values.items():st.session_state['clinical_'+key]=value
    with st.expander('Assessment inputs', expanded=not simulated_mode):
        def select(label,key,options):return st.selectbox(label,options,key='clinical_'+key)
        st.markdown('**Pathology and staging**')
        left,right=st.columns(2)
        with left:
            site=select('Histology / staging schema','site',['Unknown','Gastric adenocarcinoma','Other / GEJ schema unresolved'])
            basis=select('Assessment basis','basis',['Unknown','Pathological','Clinical','Post-neoadjuvant'])
            edition=select('AJCC edition','edition',['Unknown','AJCC 8','AJCC 7','Other'])
            neo=select('Neoadjuvant therapy','neoadjuvant',['Unknown','No','Yes'])
        with right:
            depth=select('Pathological invasion depth','depth',['Unknown']+list(DEPTHS))
            positive=st.number_input('Positive regional nodes',key='clinical_positive',value=None,min_value=0,max_value=500,step=1)
            examined=st.number_input('Examined regional nodes',key='clinical_examined',value=None,min_value=0,max_value=500,step=1)
            m=select('Distant metastasis category','m',['Unknown / indeterminate','M0','M1'])
        st.markdown('**Treatment context**')
        left,right=st.columns(2)
        with left:
            age=st.number_input('Age at assessment',key='clinical_age',value=None,min_value=0,max_value=120,step=1)
            setting=select('Current treatment setting','setting',['Unknown','After surgery','Before surgery — resectable','Advanced — first line','Advanced — later line'])
            metastatic=select('Current distant metastasis','metastatic',['Unknown','No','Yes'])
            unresectable=select('Locally advanced and unresectable','unresectable',['Unknown','No','Yes'])
            prior=select('Prior systemic therapy · current advanced episode','prior_advanced',['Unknown','No','Yes'])
            prior_episode=select('Prior therapy or surgery · current episode','prior_episode',['Unknown','No','Yes'])
            fitness=select('Clinical fitness / organ-function review','fitness',['Unknown','Reviewed for combination therapy','Needs specialist assessment'])
            immune=select('Immunotherapy risk review','immune_review',['Unknown','Reviewed — no flagged concern','Concern present — specialist review needed'])
        with right:
            her2=select('Confirmed HER2 result','her2',['Unknown','Positive','Negative'])
            cps=st.number_input('PD-L1 CPS',key='clinical_cps',value=None,min_value=0.0,max_value=100.0,step=1.0)
            cldn=select('CLDN18.2 companion assay','cldn',['Unknown','Positive','Negative'])
            msi=select('MSI / mismatch repair result','msi',['Unknown','MSI-high / dMMR','MSS / pMMR'])
            symptoms=select('Symptoms needing local control: bleeding, pain or obstruction','symptoms',['Unknown','No','Yes'])
        source=st.text_area('Source reports and assessment date',key='clinical_source')
        same=st.checkbox('I reconciled these findings to one disease episode.',key='clinical_same_episode')
        profile={'site':site,'age':age,'setting':setting,'fitness':fitness,'immune_review':immune,'metastatic':metastatic,'unresectable':unresectable,'prior_advanced':prior,'prior_episode':prior_episode,'her2':her2,'cps':cps,'cldn':cldn,'msi':msi,'symptoms':symptoms,'same_episode':same}
        staging_inputs={'depth':depth,'positive':positive,'examined':examined,'m':m,'basis':basis,'edition':edition,'neoadjuvant':neo}
        fingerprint=hashlib.sha256(json.dumps([profile,staging_inputs,source,simulated_mode],sort_keys=True).encode()).hexdigest()
    confirmed=st.checkbox('I verified the assessment sources.',key='clinical_confirm_'+fingerprint)
    st.session_state.clinical_result=None
    if not confirmed:
        return
    if not source.strip():st.error('Identify the source and assessment context before calculating.');return
    if not simulated_mode and any(x in source.lower() for x in ['fictional','simulated','synthetic']):
        st.error('Use simulated-extension mode for fictional assessments.');return
    try:
        t,n=derive_components(depth,positive,examined)
        stage=stage_group(t,n,m,site=site,basis=basis,edition=edition,neoadjuvant=neo)
    except ValueError as exc:
        stage={'stage':None,'tnm':'Unresolved','blockers':[str(exc)],'source':NCI,'version':VERSION}
    if not same:
        stage['stage']=None
        stage['blockers'].append('Reconcile the assessment episode before combining staging findings.')
    # Cross-check only when both inputs explicitly describe the same episode.
    inconsistency=(m=='M0' and metastatic=='Yes') or (m=='M1' and metastatic=='No')
    if inconsistency:
        stage['blockers'].append('The staging M category conflicts with the treatment metastasis assessment.')
        stage['stage']=None
    treatment=treatment_pathways(profile,stage)
    if inconsistency:
        treatment['cards']=[];treatment['blockers'].append('Resolve the contradictory metastasis inputs before matching treatment pathways.')
    if stage['stage']:
        st.success('Calculated stage group: '+stage['stage']+' · '+stage['tnm']+' · AJCC 8 pathological')
    for blocker in stage['blockers']:st.warning('Staging: '+blocker)
    st.link_button('Review staging evidence',NCI)
    st.markdown('**Matched treatment pathways**')
    for blocker in treatment['blockers']:st.warning(blocker)
    for item in treatment['cards']:
        with st.container(border=True):
            st.markdown('**'+item['title']+'**');st.write(item['why'])
            with st.expander('Eligibility checks'):
                st.write(item['checks'])
            st.link_button('Clinical source',item['source'],key='source_'+hashlib.sha256(item['title'].encode()).hexdigest())
    if treatment['missing']:st.info('Missing biomarker information: '+', '.join(treatment['missing']))
    if treatment['notes']:
        with st.expander('Assessment details'):
            for note in treatment['notes']:st.write(note)
            st.caption('Evidence version: '+VERSION)
    st.session_state.clinical_result={'case_id':case['id'],'provenance':'Independent fictional scenario' if simulated_mode else 'Manually reviewed public research assessment',
        'source':source,'profile':profile,'staging_inputs':staging_inputs,'staging':stage,'treatment':treatment}
    st.download_button('Download assessment',json.dumps(st.session_state.clinical_result,indent=2),case['id']+'_experimental_clinical_assessment.json','application/json',icon=':material/download:')
