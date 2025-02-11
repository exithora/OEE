import streamlit as st
import pandas as pd
from utils.data_processor import process_csv_file
from utils.oee_calculator import calculate_oee
from utils.sharepoint_auth import init_sharepoint_auth, check_sharepoint_auth
from utils.realtime_handler import (
    initialize_realtime_queue, 
    get_realtime_data, 
    merge_with_historical
)

st.set_page_config(
    page_title="OEE Upload",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'OEE Calculator'
    }
)

# Initialize realtime state before any page loads
if 'realtime_queue' not in st.session_state:
    initialize_realtime_queue()

def main():
    # Initialize SharePoint authentication
    init_sharepoint_auth()
    
    # Initialize authentication
    from utils.auth import init_auth, login, logout, get_current_user
    init_auth()
    
    # Show login form if not authenticated
    if not st.session_state.authenticated:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        return
    
    # Show logout button
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
        
    # Show user info
    user = get_current_user()
    st.sidebar.write(f"Logged in as: {user['username']} ({user['role']})")

    st.title("OEE Calculator and Analyzer")
    st.write("Upload your production data to calculate and analyze OEE metrics")

    # Initialize realtime state if not exists
    if 'enable_realtime' not in st.session_state:
        st.session_state.enable_realtime = False

    # Real-time mode toggle
    st.session_state.enable_realtime = st.sidebar.checkbox("Enable Real-time Updates", value=st.session_state.enable_realtime)
    if st.session_state.enable_realtime:
        st.sidebar.info("Real-time updates enabled. Data will refresh automatically.")
        st.sidebar.markdown("Last update: " + st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S"))
        st.rerun()  # Using st.rerun() instead of st.experimental_rerun()

    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload a CSV file containing production data"
    )

    try:
        if uploaded_file is not None:
            # Process the uploaded file
            historical_df = process_csv_file(uploaded_file)

            if historical_df is not None:
                # Get real-time data if enabled
                realtime_df = get_realtime_data() if st.session_state.enable_realtime else None

                # Merge historical and real-time data
                df = merge_with_historical(historical_df, realtime_df)
                st.session_state['data'] = df

                # Calculate OEE
                oee_metrics = calculate_oee(df)

                # Display overall OEE
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Overall OEE", f"{oee_metrics['oee']:.1f}%")
                with col2:
                    st.metric("Availability", f"{oee_metrics['availability']:.1f}%")
                with col3:
                    st.metric("Performance", f"{oee_metrics['performance']:.1f}%")
                with col4:
                    st.metric("Quality", f"{oee_metrics['quality']:.1f}%")

                st.success("Data processed successfully! Navigate to Dashboard and Analysis pages for detailed insights.")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please ensure your CSV file contains the required columns: planned_time, runtime, ideal_cycle_time, total_pieces, good_pieces")

if __name__ == "__main__":
    main()