import io
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PIL import Image

from care_app import ai
from care_app.community import CommunityStore
from care_app.model import predict, reviewed_features
from prototype_core import GENES, ROOT, genomic_csv


def image_bytes(color='white'):
    out = io.BytesIO()
    Image.new('RGB', (50, 50), color).save(out, 'PNG')
    return out.getvalue()


def gene_report():
    frame = genomic_csv((ROOT / 'demo_data/TCGA-VQ-A8DL_genes.csv').read_bytes())
    return {'readable': True, 'report_kind': 'Fictional test report', 'measured_tmb': '12 mut/Mb',
            'measured_tmb_evidence': 'TMB: 12 mut/Mb', 'limitations': [],
            'genes': [{'gene': g, 'status': 'Mutated' if frame.iloc[0][g] else 'Not mutated',
                       'evidence': g + ': explicitly tested status'} for g in GENES]}


class ModelBridgeTests(unittest.TestCase):
    def test_original_prediction_and_safe_order(self):
        rows = gene_report()['genes'][::-1]
        self.assertEqual(predict(rows)['label'], 'Low study category')
        self.assertEqual(list(reviewed_features(rows).columns), GENES)

    def test_unknown_missing_duplicate_and_unsupported_evidence_block(self):
        rows = gene_report()['genes']
        variants = [rows[:-1], rows[:-1] + [rows[0]],
                    [rows[0] | {'status': 'Unknown'}] + rows[1:],
                    [rows[0] | {'evidence': ''}] + rows[1:]]
        for variant in variants:
            with self.assertRaises(ValueError):
                reviewed_features(variant)


class OpenAIBridgeTests(unittest.TestCase):
    def test_scan_review_cannot_return_diagnostic_findings(self):
        response = ai.RadiologyReview(image_kind='Scan image', readable=True,
            findings=[ai.Finding(finding='Unsupported diagnosis', evidence='Model inference')],
            summary='Unsupported diagnosis', clinical_summary='Unsupported diagnosis',
            limitations=[], questions_for_clinician=[])
        with patch.object(ai, 'parse_image', return_value=response):
            result = ai.review_radiology(image_bytes())
        self.assertEqual(result['findings'], [])
        self.assertNotIn('Unsupported diagnosis', str(result))
        self.assertIn('written radiology report', result['patient_explanation']['overview'])

    def test_report_keeps_source_and_patient_explanation(self):
        response = ai.RadiologyReview(image_kind='Written radiology report', readable=True,
            findings=[ai.Finding(finding='Pulmonary nodule', evidence='Indeterminate pulmonary nodule.',
                                plain_language='A small spot in the lung; its cause is not clear.')],
            summary='The report describes an uncertain lung spot.',
            clinical_summary='Indeterminate pulmonary nodule.', limitations=['Cause is not established.'],
            questions_for_clinician=['What follow-up does the report recommend?'],
            patient_explanation=ai.PatientExplanation(
                overview='The cause of this small spot is not yet known.',
                key_points=['The report does not confirm cancer.'],
                terms=[ai.ExplainedTerm(term='Nodule', meaning='A small spot or lump.')],
                next_steps=['Discuss the report with your care team.']))
        with patch.object(ai, 'parse_image', return_value=response):
            result = ai.review_radiology(image_bytes())
        self.assertEqual(result['findings'][0]['evidence'], 'Indeterminate pulmonary nodule.')
        self.assertIn('not confirm cancer', result['patient_explanation']['key_points'][0])
    def test_image_validation_and_data_url(self):
        self.assertTrue(ai.image_data_url(image_bytes()).startswith('data:image/png;base64,'))
        for data in [b'', b'not an image', b'x' * (10 * 1024 * 1024 + 1)]:
            with self.assertRaises(ValueError):
                ai.image_data_url(data)

    def test_structured_image_request_and_null_results(self):
        fake = Mock()
        fake.responses.parse.return_value = SimpleNamespace(
            status='completed', output_parsed=ai.GeneReport(**gene_report()))
        with patch.object(ai, 'client', return_value=fake), patch.object(ai, 'setting', return_value='gpt-4.1-mini'):
            result = ai.extract_genes(image_bytes())
            request = fake.responses.parse.call_args.kwargs
            self.assertFalse(request['store'])
            self.assertIs(request['text_format'], ai.GeneReport)
            self.assertEqual(request['input'][0]['content'][1]['type'], 'input_image')
            self.assertEqual(len(result['genes']), 50)
            fake.responses.parse.return_value.output_parsed = None
            with self.assertRaisesRegex(ValueError, 'refused or incomplete'):
                ai.extract_genes(image_bytes())

    def test_extraction_never_fills_missing_genes_or_unsupported_negatives(self):
        report = gene_report()
        report['genes'][0]['evidence'] = ''
        report['measured_tmb_evidence'] = None
        with patch.object(ai, 'parse_image', return_value=ai.GeneReport(**report)):
            result = ai.extract_genes(image_bytes())
            self.assertEqual(result['genes'][0]['status'], 'Unknown')
            self.assertIsNone(result['measured_tmb'])
        report['genes'] = report['genes'][:-1]
        with patch.object(ai, 'parse_image', return_value=ai.GeneReport(**report)):
            with self.assertRaisesRegex(ValueError, 'invalid gene list'):
                ai.extract_genes(image_bytes())

    def test_center_search_requires_live_tool_and_links(self):
        text = 'A verified hospital CITATION'
        ann = SimpleNamespace(type='url_citation', url='https://hospital.example/oncology',
                              title='Hospital', start_index=20, end_index=len(text))
        part = SimpleNamespace(type='output_text', text=text, annotations=[ann])
        response = SimpleNamespace(status='completed', output_text=text,
                                   output=[SimpleNamespace(content=[part])])
        fake = Mock()
        fake.responses.create.return_value = response
        with patch.object(ai, 'client', return_value=fake), patch.object(ai, 'setting', return_value='gpt-4.1-mini'):
            result = ai.find_centers('Test city', 'Test country')
            request = fake.responses.create.call_args.kwargs
            self.assertEqual(request['tool_choice'], 'required')
            self.assertFalse(request['store'])
            self.assertIn('[Source 1](<https://hospital.example/oncology>)', result['text'])
            part.annotations = []
            with self.assertRaisesRegex(ValueError, 'No source-linked'):
                ai.find_centers('Test city', 'Test country')
        with self.assertRaises(ValueError):
            ai.find_centers('', 'Test country')


class CommunityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'community.sqlite3'
        self.store = CommunityStore(self.path)
        self.a = self.join('Demo-A', 'Stomach / gastric')
        self.b = self.join('Demo-B', 'Stomach / gastric')
        self.c = self.join('Demo-C', 'Breast')

    def tearDown(self):
        self.tmp.cleanup()

    def join(self, alias, cancer):
        return self.store.create_profile(alias, cancer, 'In treatment', 'Test region', 'Support', consent=True)

    def test_opt_in_private_credentials_and_persistence(self):
        with self.assertRaises(ValueError):
            self.store.create_profile('No-consent', 'Other', '', '', '', consent=False)
        with self.assertRaises(ValueError):
            self.join('demo-a', 'Other')
        with self.assertRaises(ValueError):
            self.store.login('Demo-A', 'incorrect')
        reopened = CommunityStore(self.path)
        self.assertEqual(reopened.login('Demo-A', self.a['token']), self.a)
        self.assertNotIn('token_hash', reopened.profile(self.a))
        self.assertNotIn('token_hash', reopened.peers(self.a)[0])
        self.assertEqual(len(reopened.peers(self.a, same_cancer=True)), 1)

    def test_consent_connection_message_authorization_and_block(self):
        self.store.request(self.a, self.b['id'])
        connection = self.store.connections(self.a)[0]['id']
        with self.assertRaises(ValueError):
            self.store.send(self.a, connection, 'Before acceptance')
        with self.assertRaises(ValueError):
            self.store.respond(self.a, connection, 'accepted')
        self.store.respond(self.b, connection, 'accepted')
        self.store.send(self.a, connection, 'Hello from a fictional profile')
        self.assertEqual(len(self.store.messages(self.b, connection)), 1)
        with self.assertRaises(ValueError):
            self.store.messages(self.c, connection)
        with self.assertRaises(ValueError):
            self.store.send(self.c, connection, 'Unauthorized')
        self.store.respond(self.b, connection, 'blocked')
        with self.assertRaises(ValueError):
            self.store.send(self.a, connection, 'After blocking')
        self.assertEqual(len(self.store.peers(self.a)), 1)

    def test_delete_cascades_and_invalid_credentials_rejected(self):
        self.store.request(self.a, self.b['id'])
        connection = self.store.connections(self.a)[0]['id']
        self.store.respond(self.b, connection, 'accepted')
        self.store.send(self.a, connection, 'Temporary test message')
        with self.assertRaises(ValueError):
            self.store.delete_profile(self.a | {'token': 'wrong'})
        self.store.delete_profile(self.a)
        self.assertEqual(self.store.connections(self.b), [])
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM messages').fetchone()[0], 0)
        with self.assertRaises(ValueError):
            self.store.profile(self.a)


class MultipageUITests(unittest.TestCase):
    def setUp(self):
        # Unit/UI tests must never use a real key or submit an image to OpenAI.
        configured = patch('care_app.ui.setting', return_value=None)
        configured.start()
        self.addCleanup(configured.stop)

    def app(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT / 'prototype.py'), default_timeout=30).run()
        return app.switch_page('app_pages/genes.py').run()

    def test_image_explanation_is_simple_in_patient_view(self):
        app = self.app()
        app.switch_page('app_pages/radiology.py').run()
        app.session_state['portal_radiology_source'] = {'name': 'fictional.png', 'data': image_bytes()}
        app.run()
        review = {'image_kind': 'Written radiology report', 'readable': True,
            'summary': 'A small spot is mentioned.', 'clinical_summary': 'Indeterminate pulmonary nodule.',
            'findings': [{'finding': 'Pulmonary nodule', 'plain_language': 'A small spot in the lung.',
                          'evidence': 'Indeterminate pulmonary nodule.'}],
            'limitations': [], 'questions_for_clinician': ['What does this mean for me?'],
            'patient_explanation': {'overview': 'The cause is not yet known.',
                'key_points': ['This does not confirm cancer.'],
                'terms': [{'term': 'Nodule', 'meaning': 'A small spot or lump.'}],
                'next_steps': ['Discuss this report with your care team.']}}
        with patch('care_app.ui.setting', return_value='test-not-a-real-key'), \
             patch.object(ai, 'review_radiology', return_value=review) as analyze:
            app.run()
            app.run()
            self.assertEqual(analyze.call_count, 1)
        self.assertNotIn('Read image', [b.label for b in app.button])
        self.assertEqual([e.message for e in app.exception], [])
        self.assertIn('In everyday words', [h.value for h in app.subheader])
        self.assertIn('A small spot in the lung.', [e.label for e in app.expander])
        app.get('segmented_control')[0].set_value('Clinician').run()
        self.assertNotIn('In everyday words', [h.value for h in app.subheader])
        self.assertIn('Pulmonary nodule', [e.label for e in app.expander])

    def test_audience_switch_persists_across_pages_and_case_reset(self):
        app = self.app()
        self.assertEqual(app.title[0].value, 'Your gene report')
        app.get('segmented_control')[0].set_value('Clinician').run()
        self.assertEqual(app.title[0].value, 'Genomic analysis')
        app.switch_page('app_pages/radiology.py').run()
        self.assertEqual(app.title[0].value, 'Radiology review')
        app.switch_page('integrated_report.py').run()
        app.button(key='journey_2').click().run()
        self.assertEqual(app.session_state['care_audience'], 'Clinician')
        self.assertEqual(app.title[0].value, 'Research workspace')
        app.get('segmented_control')[0].set_value('Patient').run()
        self.assertEqual(app.title[0].value, 'Explore a sample case')
        self.assertNotIn('clinical_demo', [b.key for b in app.button])
        self.assertEqual([e.message for e in app.exception], [])

    def test_cloud_entry_point_opens_every_page(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT / 'cloud/app.py'), default_timeout=30).run()
        self.assertEqual([e.message for e in app.exception], [])
        for page in ['app_pages/welcome.py', 'app_pages/genes.py', 'app_pages/radiology.py', 'app_pages/patient.py',
                     'app_pages/community.py', 'integrated_report.py']:
            app.switch_page('../' + page).run()
            self.assertEqual([e.message for e in app.exception], [])

    def test_radiology_summary_matches_the_selected_audience(self):
        app = self.app()
        app.switch_page('app_pages/radiology.py').run()
        app.session_state['portal_radiology_source'] = {'name': 'sample.png', 'data': image_bytes()}
        app.run()
        app.session_state['portal_radiology']['extraction'] = {
            'readable': True, 'summary': 'The report describes a small area in the lung.',
            'clinical_summary': 'The report documents a pulmonary nodule.',
            'findings': [], 'limitations': [], 'questions_for_clinician': [],
        }
        app.run()
        text = '\n'.join(m.value for m in app.markdown)
        self.assertIn('small area in the lung', text)
        self.assertNotIn('pulmonary nodule', text)
        app.get('segmented_control')[0].set_value('Clinician').run()
        text = '\n'.join(m.value for m in app.markdown)
        self.assertIn('pulmonary nodule', text)
        self.assertNotIn('small area in the lung', text)
        self.assertEqual([e.message for e in app.exception], [])

    def test_header_supports_both_page_signatures(self):
        from streamlit.testing.v1 import AppTest

        def render():
            from care_app.ui import header
            header('02 / 05', 'Radiology review', 'Description')
            header('Patient title', 'Clinician title')

        app = AppTest.from_function(render, default_timeout=30).run()
        self.assertEqual([e.message for e in app.exception], [])
        self.assertEqual([t.value for t in app.title], ['Radiology review', 'Patient title'])

    def test_community_profile_request_and_message_workflow(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'community.sqlite3'
            store = CommunityStore(path)
            peer = store.create_profile('Test-peer', 'Stomach / gastric', 'In treatment',
                                         'Demo region', '', consent=True)
            def config(name, default=None):
                return str(path) if name == 'COMMUNITY_DB_PATH' else default
            with patch('care_app.community_ui.setting', side_effect=config):
                app = self.app()
                app.switch_page('app_pages/community.py').run()
                app.toggle(key='portal_community_show').set_value(True).run()
                next(t for t in app.text_input if t.label == 'Community alias').set_value('Test-viewer')
                next(c for c in app.checkbox if c.label.startswith('I am 18')).check()
                next(b for b in app.button if b.label == 'Create profile').click().run()
                self.assertEqual([e.message for e in app.exception], [])
                credential = app.session_state['portal_community_auth']
                next(b for b in app.button if b.label == 'Request connection').click().run()
                connection = store.connections(peer)[0]['id']
                store.respond(peer, connection, 'accepted')
                next(b for b in app.button if b.label == 'Refresh community').click().run()
                next(t for t in app.text_area if t.label == 'Message').set_value('A fictional hello')
                next(b for b in app.button if b.label == 'Send message').click().run()
                self.assertEqual(store.messages(peer, connection)[0]['body'], 'A fictional hello')
                next(c for c in app.checkbox if c.label.startswith('Delete my profile')).check().run()
                next(b for b in app.button if b.label == 'Delete community profile').click().run()
                self.assertEqual([e.message for e in app.exception], [])
                self.assertNotIn('portal_community_auth', app.session_state)
                with self.assertRaises(ValueError):
                    store.profile(credential)

    def test_all_pages_and_demo_reset_preserves_patient_workspace(self):
        app = self.app()
        self.assertEqual(len(app.exception), 0)
        app.session_state['portal_patient'] = {'alias': 'Test', 'age': 40,
                                              'diagnosis': '', 'city': '', 'country': ''}
        for page in ['app_pages/welcome.py', 'app_pages/genes.py', 'app_pages/radiology.py', 'app_pages/patient.py',
                     'app_pages/community.py', 'integrated_report.py']:
            app.switch_page(page).run()
            self.assertEqual([e.message for e in app.exception], [])
        app.button(key='journey_1').click().run()
        self.assertEqual(app.session_state['portal_patient']['alias'], 'Test')
        app.switch_page('app_pages/patient.py').run()
        app.session_state['portal_genes'] = {'digest': 'old', 'extraction': None, 'prediction': {'label': 'old'}}
        next(t for t in app.text_input if t.label in ['Preferred name', 'Patient alias']).set_value('New patient')
        next(b for b in app.button if b.label == 'Save details').click().run()
        self.assertEqual(app.session_state['portal_patient']['alias'], 'New patient')
        self.assertNotIn('portal_genes', app.session_state)

    def test_gene_image_review_model_and_changed_image_clears_result(self):
        app = self.app()
        app.session_state['portal_genes_source'] = {'name': 'test.png', 'data': image_bytes()}
        app.run()
        with patch('care_app.ui.setting', return_value='test-not-a-real-key'), \
             patch.object(ai, 'extract_genes', return_value=gene_report()) as analyze:
            app.run()
            app.run()
            self.assertEqual(analyze.call_count, 1)
        self.assertNotIn('Read report', [b.label for b in app.button])
        self.assertEqual([e.message for e in app.exception], [])
        next(c for c in app.checkbox if c.label.startswith('I checked')).check().run()
        next(b for b in app.button if b.label == 'Get model result').click().run()
        self.assertEqual(app.session_state['portal_genes']['prediction']['label'], 'Low study category')
        app.switch_page('app_pages/radiology.py').run()
        app.switch_page('app_pages/genes.py').run()
        self.assertIsNotNone(app.session_state['portal_genes']['prediction'])
        app.session_state['portal_genes_source'] = {'name': 'new.png', 'data': image_bytes('black')}
        app.run()
        self.assertIsNone(app.session_state['portal_genes']['prediction'])
        self.assertIsNone(app.session_state['portal_genes']['extraction'])

    def test_unknown_gene_disables_prediction(self):
        app = self.app()
        app.session_state['portal_genes_source'] = {'name': 'test.png', 'data': image_bytes()}
        app.run()
        report = gene_report()
        report['genes'][0]['status'] = 'Unknown'
        with patch('care_app.ui.setting', return_value='test-not-a-real-key'), \
             patch.object(ai, 'extract_genes', return_value=report):
            app.run()
        next(c for c in app.checkbox if c.label.startswith('I checked')).check().run()
        self.assertTrue(next(b for b in app.button if b.label == 'Get model result').disabled)


if __name__ == '__main__':
    unittest.main()
