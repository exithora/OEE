
import streamlit as st
from utils.auth import init_auth, login, logout, get_current_user, is_admin
from utils.data_processor import create_template_csv
from datetime import datetime
import pandas as pd

def main():
    # Initialize authentication
    init_auth()
    
    if not st.session_state.authenticated:
        st.title("Login")
        col1, col2 = st.columns([2,1])
        with col1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        with col2:
            st.info("""
            Default credentials:
            - Admin: admin/admin123
            - Guest: guest/guest123
            """)
        return

    # Show logout button in sidebar
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
    
    # Show user info
    user = get_current_user()
    st.sidebar.write(f"Logged in as: {user['username']} ({user['role']})")

    # Main app content
    if user['role'] == 'guest':
        # For guest users, only show help page
        from pages import Help
        Help.render_help()
    else:
        # Admin sees full app
        st.title("OEE Calculator and Analyzer")
        st.write("Upload your production data to calculate and analyze OEE metrics")
        # Rest of your main app content here

if __name__ == "__main__":
    main()
