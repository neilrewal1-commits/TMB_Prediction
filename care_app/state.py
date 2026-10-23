"""Patient-scoped session state, separate from the historical demo cases."""
import hashlib
import json

import streamlit as st


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def initialize():
    st.session_state.setdefault('portal_epoch', 0)
    st.session_state.setdefault('portal_patient', {
        'alias': '', 'age': None, 'diagnosis': '', 'city': '', 'country': ''})


def clear_patient():
    epoch = st.session_state.get('portal_epoch', 0) + 1
    for key in list(st.session_state):
        if key.startswith('portal_') and not key.startswith('portal_community_'):
            del st.session_state[key]
    st.session_state.portal_epoch = epoch
    initialize()


def bind_image(kind, data):
    """A changed or removed upload invalidates extraction and model results."""
    digest = hashlib.sha256(data).hexdigest() if data is not None else None
    key = 'portal_' + kind
    old = st.session_state.get(key)
    if old is None or old['digest'] != digest:
        st.session_state[key] = {'digest': digest, 'extraction': None, 'prediction': None,
                                 'attempted': False, 'error': None}
    return st.session_state[key]
