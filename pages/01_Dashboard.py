import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.oee_calculator import calculate_hourly_oee
from utils.data_processor import filter_data_by_date
import pandas as pd
from datetime import datetime, timedelta
from utils.realtime_handler import get_realtime_data, merge_with_historical

st.set_page_config(page_title="OEE Dashboard", page_icon="📈")

def render_dashboard():
    if 'data' not in st.session_state:
        st.warning("Please upload data file in the home page first.")
        return

    st.title("OEE Dashboard")

    # Real-time mode toggle
    if 'enable_realtime' not in st.session_state:
        st.session_state.enable_realtime = False

    st.session_state.enable_realtime = st.sidebar.checkbox("Enable Real-time Updates", value=st.session_state.enable_realtime)
    if st.session_state.enable_realtime:
        st.sidebar.info("Real-time updates enabled. Data will refresh automatically.")
        st.sidebar.markdown("Last update: " + st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S"))
        st.rerun()

    df = st.session_state['data']

    # Check for real-time updates
    if st.session_state.enable_realtime:
        realtime_df = get_realtime_data()
        if realtime_df is not None:
            df = merge_with_historical(df, realtime_df)
            st.sidebar.success("Real-time data active")
            last_update = st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S")
            st.sidebar.info(f"Last update: {last_update}")

    # Date filtering
    st.sidebar.header("Date Filters")

    # Get min and max dates from the data
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()

    # Date range selector
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)

    # Time frequency selector
    frequency = st.sidebar.selectbox(
        "Select Time Frequency",
        options=['Daily', 'Weekly', 'Monthly', 'Yearly'],
        index=0
    )

    # Convert frequency selection to pandas frequency string
    freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Yearly': 'Y'}
    selected_freq = freq_map[frequency]

    # Filter data by date
    filtered_df = filter_data_by_date(
        df, 
        pd.Timestamp(start_date), 
        pd.Timestamp(end_date) + pd.Timedelta(days=1),
        selected_freq
    )

    # Part and Line filters
    col1, col2 = st.columns(2)
    with col1:
        selected_line = st.selectbox(
            "Select Production Line",
            options=['All Lines'] + sorted(filtered_df['line_number'].unique().tolist())
        )

    with col2:
        selected_part = st.selectbox(
            "Select Part Number",
            options=['All Parts'] + sorted(filtered_df['part_number'].unique().tolist())
        )

    # Apply part and line filters
    if selected_line != 'All Lines':
        filtered_df = filtered_df[filtered_df['line_number'] == selected_line]
    if selected_part != 'All Parts':
        filtered_df = filtered_df[filtered_df['part_number'] == selected_part]

    # Calculate metrics based on filtered data
    hourly_metrics = calculate_hourly_oee(filtered_df)

    # OEE Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = hourly_metrics['oee'].mean(),
        title = {'text': "Average OEE"},
        gauge = {
            'axis': {'range': [None, 100]},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 85], 'color': "gray"},
                {'range': [85, 100], 'color': "darkblue"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))

    st.plotly_chart(fig_gauge)

    # Time-based trends
    col1, col2 = st.columns(2)

    # Group data by selected frequency
    freq_df = filtered_df.set_index('timestamp').resample(selected_freq).agg({
        'runtime': 'sum',
        'planned_time': 'sum',
        'total_pieces': 'sum',
        'good_pieces': 'sum',
        'ideal_cycle_time': 'mean'
    }).reset_index()

    # Calculate OEE metrics for each period
    metrics_over_time = []
    for _, period_data in freq_df.iterrows():
        metrics = calculate_oee(pd.DataFrame([period_data]))
        metrics['timestamp'] = period_data['timestamp']
        metrics_over_time.append(metrics)
    
    metrics_df = pd.DataFrame(metrics_over_time)

    with col1:
        fig_trend = px.line(metrics_df, x='timestamp', y=['availability', 'performance', 'quality'],
                           title=f"{frequency} OEE Components Trend")
        if st.session_state.enable_realtime:
            fig_trend.add_annotation(
                text="Live Updates",
                xref="paper", yref="paper",
                x=1, y=1,
                showarrow=False,
                font=dict(color="green")
            )
        st.plotly_chart(fig_trend)

    with col2:
        fig_oee = px.line(metrics_df, x='timestamp', y='oee',
                         title=f"{frequency} OEE Trend")
        if st.session_state.enable_realtime:
            fig_oee.add_annotation(
                text="Live Updates",
                xref="paper", yref="paper",
                x=1, y=1,
                showarrow=False,
                font=dict(color="green")
            )
        st.plotly_chart(fig_oee)

    # Production Summary
    st.subheader("Production Summary")
    summary = filtered_df.groupby(['part_number', 'line_number']).agg({
        'total_pieces': 'sum',
        'good_pieces': 'sum',
        'runtime': 'sum',
        'planned_time': 'sum'
    }).reset_index()

    summary['scrap_rate'] = (1 - summary['good_pieces'] / summary['total_pieces']) * 100
    summary['utilization'] = (summary['runtime'] / summary['planned_time']) * 100

    st.dataframe(summary.round(2), use_container_width=True)

    if st.session_state.enable_realtime:
        st.empty()  # Placeholder for real-time updates
        st.rerun()  # Trigger rerun for real-time updates

if __name__ == "__main__":
    render_dashboard()