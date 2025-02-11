
import streamlit as st
import yaml
from typing import Optional

# Initialize users if not in session state
def init_auth():
    if 'users' not in st.session_state:
        st.session_state.users = {
            'admin': {'password': 'admin123', 'role': 'admin'},
            'guest': {'password': 'guest123', 'role': 'guest'}
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

def login(username: str, password: str) -> bool:
    if username in st.session_state.users:
        if st.session_state.users[username]['password'] == password:
            st.session_state.authenticated = True
            st.session_state.current_user = {
                'username': username,
                'role': st.session_state.users[username]['role']
            }
            return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None

def get_current_user() -> Optional[dict]:
    return st.session_state.current_user

def is_admin() -> bool:
    return (st.session_state.current_user is not None and 
            st.session_state.current_user['role'] == 'admin')
