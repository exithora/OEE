import pandas as pd
import streamlit as st

def create_template_csv():
    """
    Create a sample CSV template with example data
    """
    template_data = {
        'timestamp': ['2025-02-07 08:00:00', '2025-02-07 09:00:00'],
        'part_number': ['P001', 'P002'],
        'line_number': ['L1', 'L1'],
        'planned_time': [60, 60],  # minutes
        'runtime': [55, 58],  # minutes
        'ideal_cycle_time': [0.5, 0.5],  # minutes per piece
        'total_pieces': [100, 110],
        'good_pieces': [95, 105]
    }
    return pd.DataFrame(template_data)

def filter_data_by_date(df, start_date, end_date, frequency='D'):
    """
    Filter dataframe by date range and resample by specified frequency
    frequency options: 'D' for daily, 'W' for weekly, 'M' for monthly, 'Y' for yearly
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
    return df.loc[mask]

def process_csv_file(uploaded_file):
    """
    Process the uploaded CSV file and perform initial data validation
    """
    try:
        # Read CSV with explicit data types
        df = pd.read_csv(uploaded_file)

        # Convert timestamp column if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # Check for required columns
        required_columns = ['planned_time', 'runtime', 'ideal_cycle_time', 
                          'total_pieces', 'good_pieces', 'part_number', 'line_number']

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            st.info("Please download and use the template from the Help page.")
            return None

        # Convert numeric columns
        numeric_columns = ['planned_time', 'runtime', 'ideal_cycle_time', 
                         'total_pieces', 'good_pieces']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Data validation with more informative messages
        if df[numeric_columns].isna().any().any():
            st.error("Some numeric values are invalid. Please check your data.")
            return None

        if (df[numeric_columns] < 0).any().any():
            st.error("Negative values found in the dataset. All values must be positive.")
            return None

        if (df['good_pieces'] > df['total_pieces']).any():
            st.error("Good pieces cannot exceed total pieces. Please check your data.")
            return None

        if df['runtime'].max() > df['planned_time'].max():
            st.warning("Runtime exceeds planned time in some records. Please verify your data.")

        return df

    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty. Please check your CSV file.")
        return None
    except pd.errors.ParserError as e:
        st.error("Error parsing CSV file. Please ensure it's a valid CSV format.")
        st.info("Download the template from the Help page for the correct format.")
        return None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("If the problem persists, please check the file format in the Help section.")
        return None