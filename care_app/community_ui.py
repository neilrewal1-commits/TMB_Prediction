"""Opt-in peer connection UI, kept separate from support-resource cards."""
import sqlite3

import streamlit as st

from care_app.ai import setting
from care_app.community import CommunityStore
from care_app.ui import badge
from prototype_core import ROOT


def perform(function, *args):
    try:
        function(*args)
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))


def render_community():
    if not setting('COMMUNITY_ENABLED', True):
        st.info('Peer connections are disabled by this deployment.')
        return
    st.subheader('Connect with peers')
    badge('Community demo')
    try:
        store = CommunityStore(setting('COMMUNITY_DB_PATH', str(ROOT / '.local/community.sqlite3')))
        _render(store)
    except (OSError, sqlite3.Error):
        st.error('Community is unavailable. Try again shortly.')


def _render(store):
    credential = st.session_state.get('portal_community_auth')
    if not credential:
        join, login = st.tabs(['Join', 'Sign in'])
        with join, st.form('portal_community_join'):
            alias = st.text_input('Community alias', max_chars=30)
            cancer = st.selectbox('Cancer group to share', ['Prefer not to say', 'Stomach / gastric',
                'Breast', 'Lung', 'Colorectal', 'Prostate', 'Blood cancer', 'Other'])
            phase = st.selectbox('Experience to share', ['Prefer not to say', 'Newly diagnosed',
                'In treatment', 'After treatment', 'Caregiver', 'Supporter'])
            region = st.text_input('Region', max_chars=80)
            interests = st.text_area('What would you like to connect about?', max_chars=300)
            consent = st.checkbox('I am 18 or older. Share these details with signed-in members.')
            if st.form_submit_button('Create profile', type='primary'):
                try:
                    st.session_state.portal_community_auth = store.create_profile(
                        alias, cancer, phase, region, interests, consent=consent)
                    st.session_state.portal_community_new = True
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        with login, st.form('portal_community_login'):
            alias = st.text_input('Your community alias')
            code = st.text_input('Private access code', type='password')
            if st.form_submit_button('Sign in'):
                try:
                    st.session_state.portal_community_auth = store.login(alias, code)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        return
    try:
        me = store.profile(credential)
    except ValueError:
        st.session_state.pop('portal_community_auth', None)
        st.rerun()
    st.write('Signed in as **' + me['alias'] + '**')
    if st.session_state.get('portal_community_new'):
        st.success('Save your access code to sign in again.')
        st.code(credential['token'], language=None)
        if st.button('I saved my access code'):
            st.session_state.portal_community_new = False
            st.rerun()
    a, b = st.columns(2)
    if a.button('Sign out of community'):
        st.session_state.pop('portal_community_auth', None)
        st.session_state.pop('portal_community_new', None)
        st.rerun()
    b.button('Refresh community')
    directory, inbox, account = st.tabs(['Discover people', 'Connections & messages', 'My profile'])
    connections = store.connections(credential)
    with directory:
        same_cancer = st.checkbox('Show my cancer group only')
        same_region = st.checkbox('Show my region only')
        peers = store.peers(credential, same_cancer, same_region)
        if not peers:
            st.info('No matching profiles yet.')
        connected = {r['receiver'] if r['sender'] == me['id'] else r['sender']: r['status'] for r in connections}
        for peer in peers:
            with st.container(border=True, key='care_card_peer_' + peer['id']):
                st.subheader(peer['alias'])
                st.text(' · '.join(filter(None, [peer['cancer'], peer['phase'], peer['region']])))
                st.text(peer['interests'])
                st.caption('Shared: ' + (', '.join(peer['shared']) or 'Open to connection'))
                if peer['id'] in connected:
                    st.caption('Connection: ' + connected[peer['id']])
                elif st.button('Request connection', key='portal_community_request_' + peer['id']):
                    perform(store.request, credential, peer['id'])
    with inbox:
        if not connections:
            st.info('Your requests and accepted connections will appear here.')
        for connection in connections:
            ident = str(connection['id'])
            with st.expander(connection['alias'] + ' · ' + connection['status'], expanded=True):
                if connection['status'] == 'pending':
                    if connection['receiver'] == me['id']:
                        a, b = st.columns(2)
                        if a.button('Accept', key='portal_community_accept_' + ident):
                            perform(store.respond, credential, connection['id'], 'accepted')
                        if b.button('Decline', key='portal_community_decline_' + ident):
                            perform(store.respond, credential, connection['id'], 'declined')
                    else:
                        st.caption('Waiting for the other person to accept.')
                if connection['status'] == 'accepted':
                    for message in store.messages(credential, connection['id']):
                        st.caption(message['alias'] + ' · ' + message['created_at'])
                        st.text(message['body'])
                    with st.form('portal_community_message_' + ident, clear_on_submit=True):
                        body = st.text_area('Message', max_chars=1000)
                        if st.form_submit_button('Send message'):
                            perform(store.send, credential, connection['id'], body)
                if connection['status'] in {'pending', 'accepted'}:
                    if st.button('Block connection', key='portal_community_block_' + ident):
                        perform(store.respond, credential, connection['id'], 'blocked')
    with account:
        st.text(' · '.join(filter(None, [me['alias'], me['cancer'], me['phase'], me['region']])))
        st.text(me['interests'])
        confirmed = st.checkbox('Delete my profile, connections and associated messages.')
        if st.button('Delete community profile', disabled=not confirmed):
            perform(store.delete_profile, credential)
