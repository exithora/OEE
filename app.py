
import streamlit as st
from utils.auth import init_auth, login, logout, get_current_user, is_admin
from utils.data_processor import create_template_csv
from datetime import datetime
import pandas as pd

# Set page config first
st.set_page_config(page_title="OEE Calculator", page_icon="📊")

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
        from pages.Help import render_help
        render_help()
    else:
        # Admin sees full app
        st.title("OEE Calculator and Analyzer")
        st.write("Upload your production data to calculate and analyze OEE metrics")
        
        # File upload section
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            from utils.data_processor import process_csv_file
            df = process_csv_file(uploaded_file)
            if df is not None:
                st.session_state['data'] = df
                st.success("Data uploaded successfully!")
                st.write("Go to the Dashboard page to view analytics.")

if __name__ == "__main__":
    main()
