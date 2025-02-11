import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd #Import pandas here, as it's used in the edited code but missing in the original
from utils.oee_calculator import calculate_oee

st.set_page_config(page_title="OEE Analysis", page_icon="🔍")

def render_analysis():
    if 'data' not in st.session_state:
        st.warning("Please upload data file in the home page first.")
        return

    st.title("OEE Analysis")

    # Real-time mode toggle
    if 'enable_realtime' not in st.session_state:
        st.session_state.enable_realtime = False
    
    st.session_state.enable_realtime = st.sidebar.checkbox("Enable Real-time Updates", value=st.session_state.enable_realtime)
    if st.session_state.enable_realtime:
        st.sidebar.info("Real-time updates enabled. Data will refresh automatically.")
        st.sidebar.markdown("Last update: " + st.session_state.last_update.strftime("%Y-%m-%d %H:%M:%S"))
        st.rerun()

    df = st.session_state['data']
    
    # Time frequency selector
    frequency = st.sidebar.selectbox(
        "Select Time Frequency",
        options=['Daily', 'Weekly', 'Monthly', 'Yearly'],
        index=0
    )

    # Convert frequency selection to pandas frequency string
    freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Yearly': 'Y'}
    selected_freq = freq_map[frequency]

    # Resample data based on selected frequency
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    resampled_df = df.set_index('timestamp').resample(selected_freq).agg({
        'runtime': 'sum',
        'planned_time': 'sum',
        'total_pieces': 'sum',
        'good_pieces': 'sum',
        'ideal_cycle_time': 'mean',
        'part_number': 'first',
        'line_number': 'first'
    }).reset_index()

    # Part and Line Analysis
    st.subheader("Part and Line Performance")

    # Calculate OEE by part number and line
    part_metrics = []
    for part in df['part_number'].unique():
        for line in df[df['part_number'] == part]['line_number'].unique():
            part_data = df[(df['part_number'] == part) & (df['line_number'] == line)]
            metrics = calculate_oee(part_data)
            metrics.update({
                'part_number': part,
                'line_number': line
            })
            part_metrics.append(metrics)

    # Convert to DataFrame for visualization
    part_df = pd.DataFrame(part_metrics)

    # Heatmap of OEE by part and line
    fig_heatmap = px.imshow(
        part_df.pivot(index='part_number', columns='line_number', values='oee'),
        title="OEE Heatmap by Part and Line",
        labels=dict(x="Line Number", y="Part Number", color="OEE %")
    )
    st.plotly_chart(fig_heatmap)

    # Bar chart comparing OEE components
    selected_metric = st.selectbox(
        "Select Metric to Compare",
        options=['oee', 'availability', 'performance', 'quality']
    )

    fig_bar = px.bar(
        part_df,
        x='part_number',
        y=selected_metric,
        color='line_number',
        title=f"{selected_metric.upper()} Comparison by Part and Line",
        barmode='group'
    )
    st.plotly_chart(fig_bar)

    # Detailed metrics table
    st.subheader("Detailed Metrics by Part and Line")
    st.dataframe(
        part_df.round(2).sort_values(['part_number', 'line_number']),
        use_container_width=True
    )

    # Overall Performance Analysis
    st.subheader(f"Overall Performance Analysis ")
    
    # Calculate metrics for each time period
    period_metrics = []
    for _, period_data in resampled_df.iterrows():
        period_metric = calculate_oee(pd.DataFrame([period_data]))
        period_metric['timestamp'] = period_data['timestamp']
        period_metrics.append(period_metric)
    
    period_df = pd.DataFrame(period_metrics)
    
    # Calculate average metrics for the selected frequency
    avg_metrics = {
        'availability': period_df['availability'].mean(),
        'performance': period_df['performance'].mean(),
        'quality': period_df['quality'].mean(),
        'oee': period_df['oee'].mean()
    }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Parts Produced", f"{resampled_df['total_pieces'].sum():,.0f}")
        st.metric("Good Parts", f"{resampled_df['good_pieces'].sum():,.0f}")
    with col2:
        st.metric("Total Runtime", f"{resampled_df['runtime'].sum():,.0f} mins")
        st.metric("Planned Time", f"{resampled_df['planned_time'].sum():,.0f} mins")
    with col3:
        st.metric("Scrap Rate", f"{(1 - avg_metrics['quality']/100):.1%}")
        st.metric("Average Cycle Time", f"{resampled_df['ideal_cycle_time'].mean():.2f} mins")
    
    # Display OEE metrics
    st.subheader(f"Average OEE Metrics ({frequency})")
    oee_col1, oee_col2, oee_col3, oee_col4 = st.columns(4)
    with oee_col1:
        st.metric("Availability", f"{avg_metrics['availability']:.1f}%")
    with oee_col2:
        st.metric("Performance", f"{avg_metrics['performance']:.1f}%")
    with oee_col3:
        st.metric("Quality", f"{avg_metrics['quality']:.1f}%")
    with oee_col4:
        st.metric("OEE", f"{avg_metrics['oee']:.1f}%")

if __name__ == "__main__":
    render_analysis()