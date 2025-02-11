
import streamlit as st
from utils.data_processor import create_template_csv
import io

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

if __name__ == "__main__":
    render_help()
