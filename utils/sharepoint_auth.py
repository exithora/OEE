import os
import msal
import streamlit as st
from typing import Optional

def init_sharepoint_auth():
    """
    Initialize SharePoint authentication settings
    """
    # SharePoint authentication settings
    st.session_state.sharepoint_config = {
        'authority': "https://login.microsoftonline.com/common",
        'scope': ["https://graph.microsoft.com/.default"],
        'validate_authority': True,
    }

def get_auth_token() -> Optional[str]:
    """
    Get authentication token for SharePoint access
    """
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
        
    return st.session_state.access_token

def check_sharepoint_auth():
    """
    Check if user is authenticated with SharePoint
    """
    token = get_auth_token()
    return token is not None
