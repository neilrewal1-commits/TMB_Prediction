"""Shared presentation and audience-aware language for the care workspace."""
from html import escape
from pathlib import Path

import streamlit as st
from openai import OpenAIError

from care_app.ai import image_data_url, setting
from care_app.state import bind_image


def apply_theme():
    st.html('<style>' + Path(__file__).with_name('theme.css').read_text(encoding='utf-8') + '</style>')


def clinician():
    return st.session_state.get('care_audience', 'Patient') == 'Clinician'


def words(patient, professional):
    return professional if clinician() else patient


def field_label(key):
    from prototype_core import FIELDS
    patient_labels = {
        'diagnosis': 'Diagnosis', 'stage': 'Recorded stage', 'staging_edition': 'Staging system',
        'imaging_findings': 'Scan findings', 'albumin': 'Blood protein (albumin)',
        'nlr': 'White blood cell ratio (NLR)', 'measured_tmb': 'TMB from the report',
        'prior_systemic': 'Past drug treatment', 'other_conditions': 'Other health conditions',
    }
    return words(patient_labels.get(key, FIELDS[key]), FIELDS[key])


def header(title, professional=None, description=None):
    """Render audience-aware titles and support legacy step/title/description pages."""
    if description is not None:
        st.title(professional or title)
        st.write(description)
    else:
        st.title(words(title, professional or title))


def status_card(label, value, detail='', icon='description'):
    symbol = {'task_alt': '✓', 'person': '○', 'location_on': '⌖', 'genetics': '◇'}.get(icon, '▤')
    st.html(f'''<div class="care-status"><span class="care-icon" aria-hidden="true">{symbol}</span>
        <div class="care-label">{escape(label)}</div><div class="care-value">{escape(value)}</div>
        {('<div class="care-detail">' + escape(detail) + '</div>') if detail else ''}</div>''')


def badge(text):
    st.html('<span class="care-badge">' + escape(text) + '</span>')


def image_input(kind, label):
    st.caption('New images are sent to OpenAI automatically for explanation. '
               'Remove names and identifying details before uploading.')
    source_key = 'portal_' + kind + '_source'
    revision_key = 'portal_' + kind + '_revision'
    revision = st.session_state.get(revision_key, 0)
    widget_key = f'portal_{kind}_upload_{st.session_state.portal_epoch}_{revision}'
    def changed():
        upload = st.session_state.get(widget_key)
        st.session_state[source_key] = (
            {'name': upload.name, 'data': upload.getvalue()} if upload is not None else None)

    st.file_uploader(label, type=['png', 'jpg', 'jpeg', 'webp'],
                     accept_multiple_files=False, key=widget_key, on_change=changed, max_upload_size=10)
    source = st.session_state.get(source_key)
    result = bind_image(kind, source['data'] if source else None)
    if source:
        try:
            image_data_url(source['data'])
        except ValueError as exc:
            st.error(str(exc))
            return None, result
        st.image(source['data'], caption=source['name'], width='stretch')
        if st.button('Remove report', key='portal_' + kind + '_remove', icon=':material/close:'):
            st.session_state[source_key] = None
            st.session_state[revision_key] = revision + 1
            bind_image(kind, None)
            st.rerun()
    return source, result


def auto_analyze(kind, source, state, analyzer):
    """Send a new image once per session; never retry paid calls on ordinary reruns."""
    if not source or state.get('extraction') is not None:
        return False
    key = setting('OPENAI_API_KEY')
    if not key or key == 'replace-with-your-api-key':
        st.info('Image analysis is not connected. Configure the OpenAI API key to continue.',
                icon=':material/link_off:')
        return False
    if state.get('error'):
        st.error(state['error'])
        if st.button('Retry image analysis', key='portal_auto_retry_' + kind):
            state.update(attempted=False, error=None)
    if state.get('attempted'):
        return False
    state.update(attempted=True, error=None, prediction=None)
    try:
        with st.spinner('Reading your image and preparing an explanation…'):
            state['extraction'] = analyzer(source['data'])
        return True
    except (OpenAIError, ValueError) as exc:
        state['error'] = api_error_message(exc)
        st.rerun()
    return False


def api_error_message(exc):
    from openai import AuthenticationError, RateLimitError, PermissionDeniedError, APITimeoutError
    if isinstance(exc, AuthenticationError):
        return 'OpenAI rejected the API key. Check OPENAI_API_KEY in Streamlit secrets, then retry.'
    elif isinstance(exc, RateLimitError):
        if getattr(exc, 'code', None) == 'insufficient_quota':
            return 'The OpenAI project has no available API quota. Check its billing and credits, then retry.'
        else:
            return 'OpenAI is receiving too many requests. Wait a moment and try again.'
    elif isinstance(exc, PermissionDeniedError):
        return 'This OpenAI project cannot access the selected model. Check the model setting and project permissions.'
    elif isinstance(exc, APITimeoutError):
        return 'The image review took too long. Try a clear, smaller image or retry shortly.'
    elif isinstance(exc, OpenAIError):
        return 'The request could not finish. Check the connection and try again.'
    else:
        return str(exc)


def api_error(exc):
    st.error(api_error_message(exc))


def patient_explanation(explanation):
    if not explanation:
        return
    st.subheader('In everyday words')
    st.write(explanation['overview'])
    for point in explanation['key_points']:
        st.write('• ' + point)
    if explanation['terms']:
        with st.expander('What the medical words mean'):
            for item in explanation['terms']:
                st.write('**' + item['term'] + '**')
                st.write(item['meaning'])
    if explanation['next_steps']:
        st.subheader('What you can do next')
        for step in explanation['next_steps']:
            st.write('• ' + step)
