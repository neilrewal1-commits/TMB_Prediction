import io
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from PIL import Image
from pypdf import PdfWriter
from streamlit.testing.v1 import AppTest

from care_app import ai
from care_app.imaging_files import batch_digest, normalize_files, prepare_documents
from prototype_core import ROOT


def image_bytes(color='white'):
    output = io.BytesIO()
    Image.new('RGB', (30, 30), color).save(output, 'PNG')
    return output.getvalue()


def pdf_bytes(pages=2, encrypted=False):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(612, 792)
    if encrypted:
        writer.encrypt('test-password')
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def files():
    return [{'name': 'first.png', 'data': image_bytes()}, {'name': 'second.pdf', 'data': pdf_bytes()}]


def result():
    return {'image_kind': 'Mixed imaging documents', 'readable': True,
        'summary': 'Combined explanation from both reports.', 'clinical_summary': 'Combined clinical findings.',
        'findings': [{'finding': 'Finding spanning both documents', 'evidence': 'Exact report text.',
            'plain_language': 'A finding explained simply.',
            'sources': [{'filename': 'first.png', 'page': 1}, {'filename': 'second.pdf', 'page': 2}]}],
        'patient_explanation': {'overview': 'Both reports were read together.', 'key_points': [],
                                'terms': [], 'next_steps': []},
        'limitations': [], 'questions_for_clinician': [], 'conflicts': ['Reports use different examination dates.'],
        'file_reviews': [{'filename': 'first.png', 'readable': True, 'notes': 'First report.'},
                         {'filename': 'second.pdf', 'readable': True, 'notes': 'Second report.'}]}


class ImagingValidationTests(unittest.TestCase):
    def test_mixed_native_pdf_and_image_inputs(self):
        content, metadata = prepare_documents(files(), ai.image_data_url)
        self.assertEqual([c['type'] for c in content], ['input_text', 'input_image', 'input_text', 'input_file'])
        self.assertTrue(content[-1]['file_data'].startswith('data:application/pdf;base64,'))
        self.assertEqual(metadata[-1]['pages'], 2)

    def test_invalid_encrypted_and_oversized_pdf_rejected(self):
        cases = [b'bad', b'%PDF-invalid', pdf_bytes(encrypted=True), pdf_bytes(pages=31)]
        for data in cases:
            with self.assertRaises(ValueError):
                prepare_documents([{'name': 'bad.pdf', 'data': data}], ai.image_data_url)
        with self.assertRaises(ValueError):
            normalize_files([{'name': 'data.exe', 'data': b'not supported'}])
        with self.assertRaises(ValueError):
            normalize_files(files() * 6)

    def test_batch_changes_and_duplicate_names(self):
        batch = files()
        self.assertEqual(batch_digest(batch), batch_digest(batch[::-1]))
        self.assertNotEqual(batch_digest(batch), batch_digest(batch[:1]))
        renamed = [batch[0] | {'name': 'renamed.png'}]
        self.assertNotEqual(batch_digest(batch[:1]), batch_digest(renamed))
        self.assertEqual(len(normalize_files([batch[0], batch[0]])), 1)
        duplicates = normalize_files([batch[0], batch[0] | {'data': image_bytes('black')}])
        self.assertEqual([x['name'] for x in duplicates], ['first.png', 'first (2).png'])

    def test_total_pages_and_size_limits(self):
        with self.assertRaises(ValueError):
            prepare_documents([{'name': f'{i}.pdf', 'data': pdf_bytes(30)} for i in range(3)], ai.image_data_url)
        with patch('care_app.imaging_files.MAX_BATCH_BYTES', 10):
            with self.assertRaises(ValueError):
                normalize_files(files())


class CombinedRequestTests(unittest.TestCase):
    def test_one_model_request_contains_all_files_and_source_metadata(self):
        fake = Mock()
        fake.responses.parse.return_value = SimpleNamespace(status='completed',
            output_parsed=ai.CombinedRadiologyReview(**result()))
        with patch.object(ai, 'client', return_value=fake), patch.object(ai, 'setting', return_value='test-model'):
            review = ai.review_radiology_batch(files())
        self.assertEqual(fake.responses.parse.call_count, 1)
        request = fake.responses.parse.call_args.kwargs
        content = request['input'][0]['content']
        self.assertEqual(sum(x['type'] == 'input_file' for x in content), 1)
        self.assertEqual(sum(x['type'] == 'input_image' for x in content), 1)
        self.assertIn('one combined review', request['instructions'])
        self.assertFalse(request['store'])
        self.assertEqual(len(review['input_files']), 2)

    def test_bad_sources_and_missing_file_coverage_are_rejected(self):
        invalid = result()
        invalid['findings'][0]['sources'][0]['filename'] = 'not-uploaded.pdf'
        missing = result()
        missing['file_reviews'] = missing['file_reviews'][:1]
        bad_page = result()
        bad_page['findings'][0]['sources'][1]['page'] = 3
        for review in [invalid, missing, bad_page]:
            with patch.object(ai, 'review_radiology', return_value=review):
                with self.assertRaises(ValueError):
                    ai.review_radiology_batch(files())


class CombinedImagingUITests(unittest.TestCase):
    def test_batch_auto_review_once_change_removal_and_view_switch(self):
        with patch('care_app.ui.setting', return_value='fake-test-key'), \
             patch.object(ai, 'review_radiology_batch', return_value=result()) as analyze:
            app = AppTest.from_file(str(ROOT / 'prototype.py'), default_timeout=30).run()
            app.switch_page('app_pages/radiology.py').run()
            app.session_state['portal_radiology_sources'] = files()
            app.run()
            app.run()
            self.assertEqual(analyze.call_count, 1)
            self.assertEqual([e.message for e in app.exception], [])
            self.assertIn('Both reports were read together.', [m.value for m in app.markdown])
            app.get('segmented_control')[0].set_value('Clinician').run()
            self.assertEqual(analyze.call_count, 1)
            self.assertIn('Combined clinical findings.', [m.value for m in app.markdown])
            self.assertTrue(any('second.pdf' in c.value and 'page 2' in c.value for c in app.caption))
            app.session_state['portal_radiology_sources'] = files() + [{'name': 'third.png', 'data': image_bytes('black')}]
            app.run()
            self.assertEqual(analyze.call_count, 2)
            app.button(key='portal_imaging_remove').click().run()
            self.assertEqual(app.session_state['portal_radiology_sources'], [])
            self.assertIsNone(app.session_state['portal_radiology']['extraction'])
            self.assertEqual(analyze.call_count, 2)

    def test_invalid_file_blocks_request_and_clears_old_output(self):
        with patch('care_app.ui.setting', return_value='fake-test-key'), \
             patch.object(ai, 'review_radiology_batch', return_value=result()) as analyze:
            app = AppTest.from_file(str(ROOT / 'prototype.py'), default_timeout=30).run()
            app.switch_page('app_pages/radiology.py').run()
            app.session_state['portal_radiology_sources'] = files()
            app.run()
            app.session_state['portal_radiology_sources'] = [{'name': 'bad.pdf', 'data': b'not pdf'}]
            app.run()
            app.run()
            self.assertIsNone(app.session_state['portal_radiology']['extraction'])
            self.assertEqual(analyze.call_count, 1)
            self.assertTrue(app.error)
