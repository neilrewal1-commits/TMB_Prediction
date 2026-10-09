import copy
import json
import pickle
import unittest

from prototype_core import (ROOT, GENES, genomic_csv, inspect_report,
    current_facts, commit_report, numeric, loris_readiness, export_summary)

CASES = json.loads((ROOT/'demo_data/cases.json').read_text())

def report(case, suffix, stage):
    path = ROOT/'demo_data'/(case['id']+suffix+'.txt')
    return inspect_report(path.read_bytes(), path.name, case['id'], stage)

class InputTests(unittest.TestCase):
    def setUp(self):
        self.data = (ROOT/'demo_data/TCGA-VQ-A8DL_genes.csv').read_bytes()
        self.frame = genomic_csv(self.data)

    def test_reordered_columns_preserve_prediction_inputs(self):
        reordered = self.frame[self.frame.columns[::-1]].to_csv(index=False).encode()
        self.assertTrue(genomic_csv(reordered).equals(self.frame))

    def test_wrong_fifty_gene_schema_rejected(self):
        wrong = self.frame.rename(columns={'MUC6':'DNAH9'})
        with self.assertRaisesRegex(ValueError, 'Missing genes: MUC6; Unexpected columns: DNAH9'):
            genomic_csv(wrong.to_csv(index=False).encode())

    def test_duplicate_blank_nonbinary_and_empty_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            genomic_csv(self.data.replace(b'MUC16', b'TTN'))
        for value in [None, 2, 'unknown']:
            frame = self.frame.astype(object).copy()
            frame.iloc[0,0] = value
            with self.assertRaises(ValueError):
                genomic_csv(frame.to_csv(index=False).encode())
        for data in [b'', b'\n', ','.join(GENES).encode()]:
            with self.assertRaises(ValueError): genomic_csv(data)

    def test_multiple_patients_rejected_for_profile(self):
        import pandas as pd
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            genomic_csv(pd.concat([self.frame,self.frame]).to_csv(index=False).encode(),single_patient=True)

    def test_extra_csv_value_cannot_become_implicit_index(self):
        lines=self.data.decode().splitlines()
        with self.assertRaisesRegex(ValueError,'exactly one value'):
            genomic_csv((lines[0]+'\n0,'+lines[1]).encode())

    def test_three_research_predictions(self):
        with (ROOT/'Best_Model_RF_50Trees_7Depth').open('rb') as f:
            model = pickle.load(f)
        for case, expected in zip(CASES, [0,1,0]):
            frame = genomic_csv((ROOT/'demo_data'/(case['id']+'_genes.csv')).read_bytes())
            self.assertEqual(int(model.predict(frame.to_numpy())[0]),expected)

class ReportTests(unittest.TestCase):
    def test_wrong_case_rejected(self):
        with self.assertRaisesRegex(ValueError,'does not match'):
            inspect_report(b'Case ID: SOMEONE-ELSE\nAge: 70 years','report.txt',CASES[0]['id'],'labs')

    def test_no_free_text_diagnosis_inference(self):
        doc=inspect_report(b'A lung lesion may represent cancer.','report.txt',CASES[0]['id'],'imaging')
        self.assertEqual(doc['fields'],[])

    def test_conflicting_sources_excluded_and_restored_on_removal(self):
        original=report(CASES[0],'_simulated_labs','labs')
        changed=copy.deepcopy(original)
        changed['id']='second';changed['filename']='second.txt'
        next(r for r in changed['fields'] if r['field']=='albumin')['value']='2 g/dL'
        docs, changes=commit_report([original],changed)
        facts,conflicts=current_facts(docs)
        self.assertIn('albumin',conflicts)
        self.assertNotIn('albumin',facts)
        self.assertTrue(any('conflicting' in c for c in changes))
        facts,conflicts=current_facts([original])
        self.assertIn('albumin',facts);self.assertEqual(conflicts,[])
        summary=export_summary(CASES[0],'simulated',None,docs)
        self.assertIn('Conflicting evidence',summary)
        self.assertIn('2 g/dL',summary)

    def test_duplicate_report_rejected(self):
        doc=report(CASES[0],'_clinical','imaging')
        with self.assertRaisesRegex(ValueError,'already'):
            commit_report([doc],doc)

    def test_units_and_qualifiers_not_silently_converted(self):
        self.assertEqual(numeric('4 g/dL','albumin'),4)
        self.assertEqual(numeric('0 mut/Mb','measured_tmb'),0)
        for value in ['40 g/L','<4 g/dL','unknown','4']:
            with self.assertRaises(ValueError): numeric(value,'albumin')

    def test_three_case_readiness_and_provenance(self):
        for case,expected in zip(CASES,[True,True,False]):
            docs=[report(case,'_clinical','imaging'),report(case,'_simulated_labs','labs')]
            self.assertTrue(docs[-1]['simulated'])
            facts,conflicts=current_facts(docs)
            self.assertEqual(loris_readiness(facts,conflicts)['fields_present'],expected)
            summary=export_summary(case,'Public case + explicitly simulated extension',None,docs)
            self.assertIn('Simulated report',summary)
            self.assertIn('no response estimate issued',summary)

class WorkflowTests(unittest.TestCase):
    def test_all_three_patient_workflows_and_reset(self):
        from streamlit.testing.v1 import AppTest
        for i,case in enumerate(CASES):
            app=AppTest.from_file(str(ROOT/'prototype.py'),default_timeout=20).run()
            app.selectbox(key='case_selector').set_value(i).run()
            app.radio(key='mode_selector').set_value('Public case + explicitly simulated extension').run()
            app.button(key='load_genes').click().run()
            next(c for c in app.checkbox if c.key.startswith('gene_confirm_')).check().run()
            app.button(key='run_model').click().run()
            self.assertIsNotNone(app.session_state['genomic'])
            app.button(key='imaging_load').click().run()
            next(c for c in app.checkbox if c.key.startswith('imaging_confirm_')).check().run()
            app.button(key='imaging_add').click().run()
            app.selectbox(key='imaging_example').set_value(case['id']+'_simulated_radiology.txt').run()
            app.button(key='imaging_load').click().run()
            next(c for c in app.checkbox if c.key.startswith('imaging_confirm_')).check().run()
            app.button(key='imaging_add').click().run()
            app.button(key='labs_load').click().run()
            next(c for c in app.checkbox if c.key.startswith('labs_confirm_')).check().run()
            app.button(key='labs_add').click().run()
            self.assertEqual(len(app.session_state['documents']),3)
            self.assertEqual(len(app.exception),0)
            app.radio(key='mode_selector').set_value('Public research case').run()
            self.assertEqual(app.session_state['documents'],[])
            self.assertIsNone(app.session_state['genomic'])
            self.assertEqual(len(app.exception),0)

if __name__=='__main__': unittest.main()
