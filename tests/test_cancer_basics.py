import re
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from streamlit.testing.v1 import AppTest

from care_app.cancer_basics_content import CHAPTERS, SOURCES, reading_guide
from care_app.cancer_basics_diagrams import illustration

ROOT = Path(__file__).resolve().parents[1]


class CancerBasicsTests(unittest.TestCase):
    def test_substantial_sourced_chapters_and_download(self):
        self.assertEqual(len(CHAPTERS), 6)
        self.assertIn('Stomach cancer', CHAPTERS[-1]['title'])
        guide = reading_guide()
        for chapter in CHAPTERS:
            words = sum(len(re.findall(r'\b\w+\b', block['body'])) for block in chapter['sections'])
            self.assertGreater(words, 400)
            self.assertIn(chapter['title'], guide)
            for block in chapter['sections']:
                self.assertTrue(block['sources'])
                for key in block['sources']:
                    self.assertIn(SOURCES[key][1], guide)

    def test_illustrations_are_accessible_self_contained_svg(self):
        ns = {'s': 'http://www.w3.org/2000/svg'}
        for chapter in CHAPTERS:
            root = ET.fromstring(illustration(chapter['diagram']))
            svg = root
            self.assertEqual(svg.attrib['role'], 'img')
            self.assertTrue(svg.find('s:title', ns).text)
            self.assertTrue(svg.find('s:desc', ns).text)
            self.assertIsNone(svg.find('.//s:script', ns))
            self.assertFalse(any('href' in key for node in svg.iter() for key in node.attrib))

    def test_all_chapters_and_previous_next_render(self):
        app = AppTest.from_file(str(ROOT / 'prototype.py')).run(timeout=30)
        app.switch_page('app_pages/cancer_basics.py').run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, 'Cancer Basics')
        self.assertTrue(app.button(key='basics_previous').disabled)
        for index, chapter in enumerate(CHAPTERS):
            app.selectbox(key='care_basics_picker').set_value(index).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.header[0].value, chapter['title'])
        self.assertTrue(app.button(key='basics_next').disabled)
        app.button(key='basics_previous').click().run()
        self.assertEqual(app.header[0].value, CHAPTERS[-2]['title'])
        app.button(key='basics_next').click().run()
        self.assertEqual(app.header[0].value, CHAPTERS[-1]['title'])

    def test_navigation_after_support_in_both_views(self):
        for audience in ('Patient', 'Clinician'):
            app = AppTest.from_file(str(ROOT / 'prototype.py'))
            app.session_state['care_audience'] = audience
            app.run(timeout=30)
            self.assertFalse(app.exception)
            labels = [link.label for link in app.sidebar.get('page_link')]
            support = 'Find support' if 'Find support' in labels else 'Support'
            self.assertEqual(labels[labels.index(support) + 1], 'Cancer Basics')


if __name__ == '__main__':
    unittest.main()
