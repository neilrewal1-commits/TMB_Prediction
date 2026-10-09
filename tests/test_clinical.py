import unittest
from pathlib import Path
from clinical_rules import stage_group, derive_components, treatment_pathways

CONTEXT=dict(site='Gastric adenocarcinoma',basis='Pathological',edition='AJCC 8',neoadjuvant='No')

class StageTests(unittest.TestCase):
    def test_reference_groups_and_subdivisions(self):
        # Specific AJCC 8 boundary examples checked against NCI PDQ tables 1–5.
        for t,n,m,expected in [('Tis','N0','M0','0'),('T1a','N0','M0','IA'),('T1b','N1','M0','IB'),('T3','N0','M0','IIA'),('T4a','N0','M0','IIB'),('T4a','N2','M0','IIIA'),('T1','N3b','M0','IIIB'),('T4b','N3a','M0','IIIC'),('TX','NX','M1','IV')]:
            with self.subTest(t=t,n=n,m=m):self.assertEqual(stage_group(t,n,m,**CONTEXT)['stage'],expected)

    def test_unknown_metastasis_and_wrong_schema_block(self):
        for key,value in [('site','Other'),('basis','Clinical'),('basis','Post-neoadjuvant'),('edition','AJCC 7'),('neoadjuvant','Yes'),('neoadjuvant','Unknown')]:
            context=CONTEXT|{key:value}
            self.assertIsNone(stage_group('T3','N0','M0',**context)['stage'])
        self.assertIsNone(stage_group('T3','N0','Unknown',**CONTEXT)['stage'])
        self.assertIsNone(stage_group('T3','N3','M0',**CONTEXT)['stage'])
        self.assertIsNone(stage_group('T3','NX','M0',**CONTEXT)['stage'])

    def test_node_boundaries_and_invalid_counts(self):
        for count,n in [(0,'N0'),(1,'N1'),(2,'N1'),(3,'N2'),(6,'N2'),(7,'N3a'),(15,'N3a'),(16,'N3b')]:
            self.assertEqual(derive_components('Serosa',count,20),('T4a',n))
        for positive,total in [(0,0),(3,2),(-1,20),(1.5,20),(None,20)]:
            with self.assertRaises(ValueError):derive_components('Serosa',positive,total)

class TreatmentTests(unittest.TestCase):
    def setUp(self):
        self.profile=dict(site='Gastric adenocarcinoma',age=70,setting='Advanced — first line',same_episode=True,
            fitness='Reviewed for combination therapy',immune_review='Reviewed — no flagged concern',
            metastatic='Yes',unresectable='Yes',prior_advanced='No',her2='Positive',cps=5,cldn='Unknown',msi='Unknown',symptoms='No')
        self.stage=stage_group('T3','N1','M1',**CONTEXT)

    def titles(self,p):return [c['title'] for c in treatment_pathways(p,self.stage)['cards']]

    def test_her2_cps_and_immune_gates(self):
        self.assertTrue(any('Pembrolizumab' in c for c in self.titles(self.profile)))
        for change in [{'cps':0},{'cps':None},{'her2':'Negative'},{'immune_review':'Unknown'}]:
            self.assertFalse(any('Pembrolizumab' in c for c in self.titles(self.profile|change)))

    def test_cldn_requires_both_biomarkers(self):
        self.assertTrue(any('Zolbetuximab' in c for c in self.titles(self.profile|{'her2':'Negative','cldn':'Positive'})))
        self.assertFalse(any('Zolbetuximab' in c for c in self.titles(self.profile|{'cldn':'Positive'})))

    def test_missing_fitness_prior_line_and_episode_block(self):
        for change in [{'fitness':'Unknown'},{'same_episode':False},{'age':17},{'prior_advanced':'Yes'},{'setting':'Advanced — later line'},{'metastatic':'Unknown','unresectable':'Unknown'}]:
            self.assertEqual(self.titles(self.profile|change),[])

    def test_postoperative_and_pretreatment_not_mixed(self):
        p=self.profile|{'setting':'After surgery','metastatic':'No'}
        stage=stage_group('T3','N0','M0',**CONTEXT)
        result=treatment_pathways(p,stage)
        self.assertEqual(len(result['cards']),2)
        self.assertFalse(any('durvalumab' in c['title'].lower() for c in result['cards']))
        self.assertEqual(treatment_pathways(p,self.stage)['cards'],[])

    def test_core_rejects_conflicting_metastasis_without_ui(self):
        self.assertEqual(treatment_pathways(self.profile|{'metastatic':'No'},self.stage)['cards'],[])
        m0=stage_group('T3','N0','M0',**CONTEXT)
        self.assertEqual(treatment_pathways(self.profile,m0)['cards'],[])

    def test_perioperative_requires_resectability_and_no_prior_episode_treatment(self):
        p=self.profile|{'setting':'Before surgery — resectable','metastatic':'No','unresectable':'No','prior_episode':'No'}
        unresolved={'stage':None,'tnm':'Unresolved','blockers':['Clinical stage outside pathological module']}
        self.assertTrue(any('durvalumab' in c['title'] for c in treatment_pathways(p,unresolved)['cards']))
        for change in [{'unresectable':'Yes'},{'unresectable':'Unknown'},{'prior_episode':'Yes'},{'prior_episode':'Unknown'}]:
            self.assertEqual(treatment_pathways(p|change,unresolved)['cards'],[])

class ClinicalUITests(unittest.TestCase):
    def test_three_scenarios_and_no_stale_output(self):
        from streamlit.testing.v1 import AppTest
        appfile=Path(__file__).resolve().parents[1]/'cloud/app.py'
        for i,expected in enumerate(['IIA','IIIA','IV']):
            app=AppTest.from_file(str(appfile),default_timeout=20).run()
            app.button(key='journey_'+str(i)).click().run()
            app.radio(key='mode_selector').set_value('Public case + explicitly simulated extension').run()
            app.button(key='clinical_demo').click().run()
            next(c for c in app.checkbox if c.key.startswith('clinical_confirm_')).check().run()
            self.assertEqual(len(app.exception),0)
            result=app.session_state['clinical_result']
            self.assertEqual(result['staging']['stage'],expected)
            self.assertTrue(result['treatment']['cards'])
            self.assertIn('fictional',result['provenance'])
            app.selectbox(key='clinical_m').set_value('Unknown / indeterminate').run()
            self.assertIsNone(app.session_state['clinical_result'])
            app.button(key='journey_'+str((i+1)%3)).click().run()
            self.assertIsNone(app.session_state['clinical_result'])

if __name__=='__main__':unittest.main()
