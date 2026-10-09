"""Experimental, deterministic gastric cancer rules. Not clinically validated.

Stage groups: AJCC 8 pathological stomach tables reproduced by NCI PDQ.
Treatment cards: selected source-linked pathways, not an exhaustive guideline.
"""
import math

VERSION = 'gastric-demo-0.3 / evidence checked 2026-10-08'
NCI = 'https://www.cancer.gov/types/stomach/hp/stomach-treatment-pdq'
FDA_HER2 = 'https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-pembrolizumab-her2-positive-gastric-or-gastroesophageal-junction-adenocarcinoma'
FDA_CLDN = 'https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-zolbetuximab-clzb-chemotherapy-gastric-or-gastroesophageal-junction-adenocarcinoma'
FDA_PERIOP = 'https://www.fda.gov/drugs/resources-information-approved-drugs/fda-approves-durvalumab-resectable-gastric-or-gastroesophageal-junction-adenocarcinoma'

# Each row is N0, N1, N2, N3a, N3b, with M0. T1 includes T1a/T1b.
P_GROUPS = {
    'T1': ['IA','IB','IIA','IIB','IIIB'],
    'T2': ['IB','IIA','IIB','IIIA','IIIB'],
    'T3': ['IIA','IIB','IIIA','IIIB','IIIC'],
    'T4a': ['IIB','IIIA','IIIA','IIIB','IIIC'],
    'T4b': ['IIIA','IIIB','IIIB','IIIC','IIIC'],
}
DEPTHS = {
    'In situ': 'Tis', 'Lamina propria or muscularis mucosae': 'T1a',
    'Submucosa': 'T1b', 'Muscularis propria': 'T2',
    'Subserosa without serosal or adjacent-organ invasion': 'T3',
    'Serosa': 'T4a', 'Adjacent organ invasion': 'T4b',
}

def stage_group(t, n, m, *, site, basis, edition, neoadjuvant):
    """Calculate a stage from confirmed components; never infer missing TNM."""
    result={'stage':None,'tnm':f'{t} {n} {m}','blockers':[], 'source':NCI,'version':VERSION}
    if site != 'Gastric adenocarcinoma': result['blockers'].append('Confirm gastric adenocarcinoma under the stomach staging schema; GEJ/esophageal and other histologies need separate rules.')
    if basis != 'Pathological': result['blockers'].append('This calculator implements pathological grouping only; clinical and post-neoadjuvant staging are separate systems.')
    if edition != 'AJCC 8': result['blockers'].append('Confirm AJCC 8; historical AJCC 7 records are not silently converted.')
    if neoadjuvant != 'No': result['blockers'].append('Confirm no treatment before the staging operation. Post-neoadjuvant ypTNM is not supported.')
    if t not in ['TX','T0','Tis','T1','T1a','T1b','T2','T3','T4a','T4b']:result['blockers'].append('Invalid or missing T category.')
    if n not in ['NX','N0','N1','N2','N3a','N3b']:result['blockers'].append('Invalid or missing N category; N3 needs subdivision for M0.')
    if m not in ['M0','M1']:result['blockers'].append('Metastasis must be confirmed M0 or M1; an indeterminate lesion is not M1.')
    if result['blockers']:return result
    if m=='M1':result['stage']='IV'
    elif t=='Tis' and n=='N0':result['stage']='0'
    elif t in P_GROUPS or t in ['T1a','T1b']:
        if n=='NX':result['blockers'].append('Regional node category is unknown.')
        else:result['stage']=P_GROUPS['T1' if t in ['T1a','T1b'] else t][['N0','N1','N2','N3a','N3b'].index(n)]
    else:result['blockers'].append('This combination has no supported M0 stage group; review the source components.')
    return result

def derive_components(depth, positive_nodes, examined_nodes):
    """Derive pT/pN from human-confirmed pathology; M needs its own assessment."""
    if depth not in DEPTHS: raise ValueError('Select a supported confirmed invasion depth.')
    for count in [positive_nodes,examined_nodes]:
        if isinstance(count,bool) or not isinstance(count,int) or count<0:raise ValueError('Node counts must be nonnegative integers.')
    if positive_nodes>examined_nodes:raise ValueError('Positive nodes cannot exceed examined nodes.')
    if examined_nodes==0:raise ValueError('No examined nodes: do not assume N0.')
    n='N0' if positive_nodes==0 else 'N1' if positive_nodes<=2 else 'N2' if positive_nodes<=6 else 'N3a' if positive_nodes<=15 else 'N3b'
    return DEPTHS[depth],n

def treatment_pathways(p, stage):
    """Match discussion options, never prescribe, dose, rank or estimate benefit."""
    out={'cards':[],'blockers':[],'missing':[],'notes':[], 'version':VERSION}
    def card(title,why,source,checks):out['cards'].append({'title':title,'why':why,'source':source,'checks':checks})
    if p.get('site')!='Gastric adenocarcinoma':out['blockers'].append('The implemented treatment module covers gastric adenocarcinoma only.')
    age=p.get('age')
    if not isinstance(age,(int,float)) or isinstance(age,bool) or not math.isfinite(age) or age<18:out['blockers'].append('A confirmed adult age is required for this module.')
    setting=p.get('setting','Unknown')
    if setting not in ['After surgery','Before surgery — resectable','Advanced — first line','Advanced — later line']:out['blockers'].append('Confirm the current treatment setting, separately from historical stage.')
    if p.get('same_episode') is not True:out['blockers'].append('Confirm these inputs describe one assessment episode; do not combine historical staging with a new recurrence.')
    # Enforce consistency here, not only in the screen calling the rules.
    m=stage.get('tnm','').split()[-1:]
    if (m==['M0'] and p.get('metastatic')=='Yes') or (m==['M1'] and p.get('metastatic')=='No'):
        out['blockers'].append('Staging and treatment assessments disagree about distant metastasis in the same episode.')
    if setting=='Before surgery — resectable' and p.get('unresectable')!='No':
        out['blockers'].append('Confirm the disease is resectable; an unknown or unresectable assessment cannot match the perioperative pathway.')
    if out['blockers']:return out
    if p.get('fitness')!='Reviewed for combination therapy':
        out['blockers'].append('Combination-treatment fitness is unconfirmed or needs specialist review. Age, weight or albumin alone cannot establish eligibility.')
        return out
    immune_ok=p.get('immune_review')=='Reviewed — no flagged concern'
    if not immune_ok:out['notes'].append('Immunotherapy combinations are withheld pending review of autoimmune disease, transplant history, immunosuppression and other immune-toxicity risks. This is not an automatic contraindication.')
    checks='Oncology review of organ function, blood counts, comorbidities, medications, preferences and full current prescribing information is still required.'
    if setting=='After surgery':
        if not stage.get('stage') or stage.get('blockers'):out['blockers'].append('A supported pathological stage from this same operative episode is required.')
        elif stage['stage']=='IV':out['blockers'].append('Metastatic disease does not fit this localized postoperative pathway; review the current setting.')
        elif stage['stage'] in ['IIA','IIB','IIIA','IIIB','IIIC']:
            card('Postoperative chemotherapy discussion',f"Calculated pathological stage {stage['stage']} after surgery, with no neoadjuvant therapy, matches the broad postoperative treatment setting.",NCI,checks+' Confirm margins and extent of lymph-node dissection; regimen selection is not implemented.')
            card('Postoperative chemoradiation discussion','Radiation with chemotherapy is a possible postoperative pathway; stage alone cannot decide between it and chemotherapy.',NCI,'Review margins, lymph-node dissection, prior radiation and multidisciplinary recommendations. The app does not select radiation fields or doses.')
        else:out['notes'].append('Early-stage postoperative management needs more detailed endoscopic, margin and surgical risk criteria than this module implements; no regimen is selected.')
    elif setting=='Before surgery — resectable':
        if p.get('metastatic')!='No':out['blockers'].append('Confirm no distant metastasis and clinical resectability before considering a perioperative pathway.')
        elif p.get('prior_episode')!='No':out['blockers'].append('Confirm no previous treatment in this episode for this illustrative perioperative pathway; no prior advanced therapy is insufficient.')
        elif immune_ok:card('Perioperative durvalumab + FLOT discussion','The entered profile describes an adult with resectable gastric adenocarcinoma. FDA approval covers treatment before and after surgery followed by durvalumab alone.',FDA_PERIOP,checks+' A team must confirm clinical stage, resectability and FLOT suitability; this is not an adjuvant-only substitute.')
        out['notes'].append('Clinical cTNM grouping is not calculated by the pathological calculator. A pathological stage must not be reused as a pretreatment clinical stage.')
    else:
        if p.get('metastatic')!='Yes' and p.get('unresectable')!='Yes':out['blockers'].append('Confirm distant metastasis or locally advanced unresectability for an advanced-disease pathway.')
        if setting=='Advanced — later line':out['blockers'].append('Later-line sequencing requires the actual previous regimens and progression history; not implemented in this version.')
        elif p.get('prior_advanced')!='No':out['blockers'].append('Confirm no previous systemic therapy for advanced disease before matching first-line options.')
        if out['blockers']:return out
        for field,label in [('her2','HER2'),('msi','MSI/MMR'),('cldn','CLDN18.2')]:
            if p.get(field,'Unknown')=='Unknown':out['missing'].append(label)
        cps=p.get('cps')
        if cps is None:out['missing'].append('PD-L1 CPS')
        elif isinstance(cps,bool) or not isinstance(cps,(float,int)) or not math.isfinite(cps) or not 0<=cps<=100:
            out['blockers'].append('PD-L1 CPS must be a number from 0 to 100 or unknown.');return out
        card('Systemic-treatment discussion','The profile indicates advanced disease. Biomarker results and patient fitness determine the appropriate combination.',NCI,checks+' This general card does not select a regimen.')
        if p.get('her2')=='Positive' and cps is not None and cps>=1 and immune_ok:
            card('Pembrolizumab + trastuzumab + chemotherapy','HER2-positive disease and PD-L1 CPS ≥1 match the biomarker criteria for this FDA-approved first-line combination.',FDA_HER2,checks+' Confirm validated HER2/PD-L1 assays and cardiac assessment for trastuzumab.')
        if p.get('her2')=='Negative' and p.get('cldn')=='Positive':
            card('Zolbetuximab + chemotherapy','HER2-negative, CLDN18.2-positive advanced disease matches the biomarker criteria for this first-line option.',FDA_CLDN,checks+' CLDN18.2 positivity must be established by the approved companion assay; a generic gene mutation is insufficient.')
        if p.get('msi')=='MSI-high / dMMR':out['notes'].append('MSI-high/dMMR needs a dedicated immunotherapy discussion. This partial rule set does not select an MSI-based regimen or sequence.')
        if p.get('her2')=='Negative':out['notes'].append('Other chemotherapy–immunotherapy options may apply. This version does not implement all HER2-negative PD-L1 pathways and must not be read as ruling them out.')
        if p.get('symptoms')=='Yes':card('Radiation / local symptom-control review','Symptoms such as bleeding, pain or obstruction may justify a local treatment discussion alongside systemic care.',NCI,'A treating team must assess symptoms; radiation is not automatically selected, and urgent symptoms need direct clinical assessment.')
    out['notes'].append('The high/low research TMB result, age and weight do not independently choose a treatment. No doses, rankings or survival predictions are generated.')
    return out
