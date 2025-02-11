import pandas as pd
import numpy as np

def calculate_oee(df):
    """
    Calculate OEE metrics from the provided dataframe
    """
    # Calculate Availability
    availability = (df['runtime'].sum() / df['planned_time'].sum()) * 100
    
    # Calculate Performance
    ideal_output = df['runtime'].sum() / df['ideal_cycle_time'].mean()
    performance = (df['total_pieces'].sum() / ideal_output) * 100
    
    # Calculate Quality
    quality = (df['good_pieces'].sum() / df['total_pieces'].sum()) * 100
    
    # Calculate OEE
    oee = (availability * performance * quality) / 10000
    
    return {
        'availability': availability,
        'performance': performance,
        'quality': quality,
        'oee': oee
    }

def calculate_hourly_oee(df):
    """
    Calculate OEE metrics on an hourly basis
    """
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    
    hourly_metrics = []
    for hour in df['hour'].unique():
        hour_data = df[df['hour'] == hour]
        metrics = calculate_oee(hour_data)
        metrics['hour'] = hour
        hourly_metrics.append(metrics)
    
    return pd.DataFrame(hourly_metrics)
