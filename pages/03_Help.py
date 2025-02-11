import streamlit as st
from utils.data_processor import create_template_csv
import io

st.set_page_config(page_title="OEE Help", page_icon="❓")

def render_help():
    st.title("OEE Calculator Help")

    # Real-time mode toggle
    if 'enable_realtime' not in st.session_state:
        st.session_state.enable_realtime = False
    
    st.session_state.enable_realtime = st.sidebar.checkbox("Enable Real-time Updates", value=st.session_state.enable_realtime)
    if st.session_state.enable_realtime:
        st.sidebar.info("Real-time updates enabled. Data will refresh automatically.")
        st.sidebar.markdown("Last update: " + st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S"))
        st.rerun()

    # Download template section
    st.header("Download Template")
    template_df = create_template_csv()

    # Convert DataFrame to CSV
    csv = template_df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV Template",
        data=csv,
        file_name="oee_template.csv",
        mime="text/csv",
        help="Click to download a sample CSV template with example data"
    )

    st.header("About OEE")
    st.write("""
    Overall Equipment Effectiveness (OEE) is a measure of manufacturing productivity that combines three factors:

    1. **Availability**: The percentage of scheduled time that the operation is available to operate
    2. **Performance**: The speed at which the work center runs as a percentage of its designed speed
    3. **Quality**: The good units produced as a percentage of the total units started
    """)

    st.header("Required Data Format")
    st.write("""
    Your CSV file should contain the following columns:

    - **timestamp**: Time of the record (format: YYYY-MM-DD HH:MM:SS)
    - **part_number**: Unique identifier for the part being produced
    - **line_number**: Production line identifier
    - **planned_time**: Total time scheduled for production (minutes)
    - **runtime**: Actual time the machine was running (minutes)
    - **ideal_cycle_time**: Standard time to produce one piece (minutes)
    - **total_pieces**: Total number of pieces produced
    - **good_pieces**: Number of good pieces produced (meeting quality standards)
    """)

    # Real-time API Documentation
    st.header("Real-time Data Integration")
    st.write("""
    The application supports real-time data integration through a REST API endpoint. To enable real-time updates:

    1. Toggle 'Enable Real-time Updates' in the sidebar
    2. Send production data to the API endpoint
    """)

    st.subheader("API Endpoint")
    st.code("""
    POST /api/v1/production-data
    Host: your-app-url
    Content-Type: application/json
    Authorization: Bearer <your-access-token>
    """)

    st.subheader("Request Body Format")
    st.code("""
    {
        "timestamp": "2025-02-07 10:30:00",
        "part_number": "P001",
        "line_number": "L1",
        "planned_time": 60,
        "runtime": 55,
        "ideal_cycle_time": 0.5,
        "total_pieces": 100,
        "good_pieces": 95
    }
    """, language="json")

    st.subheader("Real-time Data Rules")
    st.write("""
    - Data is temporarily stored in memory
    - Maximum of 1000 recent data points are retained
    - Updates occur automatically every 5 seconds
    - Historical data is preserved when real-time mode is disabled
    """)

    # Show example data
    st.subheader("Example Data")
    st.dataframe(template_df, use_container_width=True)

    st.header("Calculations")
    st.write("""
    - **Availability** = Runtime / Planned Time
    - **Performance** = (Total Pieces × Ideal Cycle Time) / Runtime
    - **Quality** = Good Pieces / Total Pieces
    - **OEE** = Availability × Performance × Quality
    """)

    st.header("Tips")
    st.write("""
    - Ensure all time values are in the same unit (minutes)
    - Verify that good pieces don't exceed total pieces
    - Check for any negative values in your data
    - Make sure timestamps are in a standard format
    - Use consistent part numbers and line numbers across records
    - For real-time updates, ensure your data sending frequency matches the refresh rate
    """)

if __name__ == "__main__":
    render_help()