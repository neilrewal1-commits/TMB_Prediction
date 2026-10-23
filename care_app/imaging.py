"""Shared combined imaging workflow for patient and clinician views."""
import json

import streamlit as st

from care_app import ai
from care_app.imaging_files import batch_digest, normalize_files, prepare_documents
from care_app.ui import auto_analyze, clinician, header, patient_explanation
from prototype_core import ROOT


def imaging_input(auto_send=True):
    st.caption(('PDFs and images are sent to OpenAI automatically for one combined review. ' if auto_send else 'Click EXPLAIN MY REPORT to send these files to OpenAI for review. ') +
               'Remove names and identifying details before uploading.')
    st.caption('Up to 10 files · 10 MB each · 30 MB total · 30 pages per PDF · 60 pages/images total')
    revision = st.session_state.get('portal_imaging_revision', 0)
    widget = f'portal_imaging_upload_{st.session_state.portal_epoch}_{revision}'

    def changed():
        uploads = st.session_state.get(widget) or []
        st.session_state.portal_radiology_sources = [
            {'name': upload.name, 'data': upload.getvalue()} for upload in uploads]
        st.session_state.pop('portal_radiology_source', None)

    st.file_uploader('Choose imaging files (PDF or images)',
        type=['pdf', 'png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True,
        max_upload_size=10, key=widget, on_change=changed)
    legacy = st.session_state.get('portal_radiology_source')
    if 'portal_radiology_sources' not in st.session_state or (legacy and not st.session_state.portal_radiology_sources):
        st.session_state.portal_radiology_sources = [legacy] if legacy else []
    files = st.session_state.portal_radiology_sources
    if not files:
        st.session_state.portal_radiology = {'digest': None, 'extraction': None,
            'prediction': None, 'attempted': False, 'error': None}
        return [], st.session_state.portal_radiology
    try:
        files = normalize_files(files)
        digest = batch_digest(files)
    except ValueError as exc:
        st.session_state.portal_radiology = {'digest': None, 'extraction': None,
            'prediction': None, 'attempted': False, 'error': None}
        st.error(str(exc))
        return [], st.session_state.portal_radiology
    old = st.session_state.get('portal_radiology')
    if old and len(files) == 1 and old.get('digest') == files[0]['digest']:
        old['digest'] = digest  # Preserve a pre-upgrade, single-image session.
    if old is None or old.get('digest') != digest:
        st.session_state.portal_radiology = {'digest': digest, 'extraction': None,
            'prediction': None, 'attempted': False, 'error': None}
    state = st.session_state.portal_radiology
    with st.expander(f'Files in this review ({len(files)})', expanded=True):
        for file in files:
            st.text(file['name'])
            if file['name'].lower().endswith('.pdf'):
                st.pdf(file['data'], height=600,
                       key='imaging_pdf_' + file['name'] + '_' + file['digest'],
                       alt='Uploaded imaging document: ' + file['name'])
            else:
                try:
                    ai.image_data_url(file['data'])
                    st.image(file['data'], width='stretch')
                except ValueError:
                    pass
    if st.button('Remove all imaging files', key='portal_imaging_remove'):
        st.session_state.portal_radiology_sources = []
        st.session_state.pop('portal_radiology_source', None)
        st.session_state.portal_imaging_revision = revision + 1
        st.session_state.pop('portal_radiology', None)
        st.rerun()
    return files, state


def analyze_files(files):
    # Validate every document before any request; never silently omit a bad file.
    _, metadata = prepare_documents(files, ai.image_data_url)
    if len(files) == 1 and not files[0]['name'].lower().endswith('.pdf'):
        result = ai.review_radiology(files[0]['data'])
        result['input_files'] = metadata
        for finding in result.get('findings', []):
            finding['sources'] = [{'filename': files[0]['name'], 'page': 1}]
        return result
    return ai.review_radiology_batch(files)


def render_imaging(show_title=True):
    if show_title:
        if not clinician():
            home = ROOT / 'app_pages/home.py'
            if not home.exists():
                home = ROOT / 'app_pages/welcome.py'
            st.page_link(str(home), label='Back to home', icon=':material/arrow_back:')
        header('Your imaging', 'Radiology review')
    st.write('Add your imaging reports and images together. You will receive one combined explanation.')
    files, state = imaging_input()
    if not files:
        return
    auto_analyze('radiology', {'name': 'Combined imaging upload', 'data': files}, state, analyze_files)
    result = state.get('extraction')
    if not result:
        return
    st.subheader('Your results' if not clinician() else 'Combined imaging findings')
    st.caption(f'Combined review of {len(files)} file' + ('s' if len(files) != 1 else ''))
    explanation = result.get('patient_explanation')
    if clinician():
        st.write(result.get('clinical_summary') or result['summary'])
    elif explanation:
        patient_explanation(explanation)
    else:
        st.write(result['summary'])
    for conflict in result.get('conflicts', []):
        st.warning(conflict)
    if not result['readable']:
        st.warning('The uploaded material could not be read reliably. Try clearer reports.')
    for item in result.get('findings', []):
        title = item['finding'] if clinician() else (item.get('plain_language') or item['finding'])
        with st.expander(title):
            if clinician() and item.get('plain_language'):
                st.write(item['plain_language'])
            st.caption('Exact supporting text / visible evidence')
            st.write(item['evidence'])
            for source in item.get('sources', []):
                st.caption(source['filename'] + (f" · page {source['page']}" if source.get('page') else ''))
    with st.expander('Files reviewed and limitations'):
        for entry in result.get('file_reviews', []):
            st.write('**' + entry['filename'] + '**')
            st.write(entry['notes'])
            if not entry['readable']:
                st.warning('This file could not be read reliably.')
        for item in result.get('limitations', []):
            st.write(item)
    if result.get('questions_for_clinician'):
        with st.expander('Questions for your care team'):
            for question in result['questions_for_clinician']:
                st.write('• ' + question)
    st.download_button('Save combined results', json.dumps(result, indent=2),
        'combined_imaging_review.json', 'application/json', icon=':material/download:')
