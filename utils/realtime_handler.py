import pandas as pd
from datetime import datetime
import streamlit as st
from typing import Dict, List, Optional

def initialize_realtime_queue():
    """
    Initialize the real-time data queue in session state and load saved data
    """
    if 'realtime_queue' not in st.session_state:
        st.session_state.realtime_queue = []
        # Load saved data if exists
        if pd.io.common.file_exists('realtime_data.csv'):
            saved_data = pd.read_csv('realtime_data.csv')
            saved_data['timestamp'] = pd.to_datetime(saved_data['timestamp'])
            st.session_state.realtime_queue = saved_data.to_dict('records')
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

def add_realtime_data(data: Dict):
    """
    Add new data point to the real-time queue and save to file
    """
    if 'realtime_queue' not in st.session_state:
        initialize_realtime_queue()
    
    # Convert timestamp to datetime if it's a string
    if isinstance(data.get('timestamp'), str):
        data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    st.session_state.realtime_queue.append(data)
    st.session_state.last_update = datetime.now()
    
    # Save to CSV file
    df = pd.DataFrame([data])
    df.to_csv('realtime_data.csv', mode='a', header=not pd.io.common.file_exists('realtime_data.csv'), index=False)

def get_realtime_data() -> Optional[pd.DataFrame]:
    """
    Get current real-time data as DataFrame
    """
    if 'realtime_queue' not in st.session_state or not st.session_state.realtime_queue:
        return None
    
    return pd.DataFrame(st.session_state.realtime_queue)

def clear_old_data(max_points: int = 1000):
    """
    Clear old data points to prevent memory issues
    """
    if len(st.session_state.realtime_queue) > max_points:
        st.session_state.realtime_queue = st.session_state.realtime_queue[-max_points:]

def merge_with_historical(historical_df: pd.DataFrame, realtime_df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge historical and real-time data
    """
    if realtime_df is None or realtime_df.empty:
        return historical_df
    
    # Ensure timestamp columns are datetime
    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])
    realtime_df['timestamp'] = pd.to_datetime(realtime_df['timestamp'])
    
    # Combine and sort by timestamp
    combined_df = pd.concat([historical_df, realtime_df], ignore_index=True)
    combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
    
    return combined_df
