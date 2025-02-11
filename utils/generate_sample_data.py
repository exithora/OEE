
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_rows=2000):
    # Start date
    start_date = datetime(2024, 1, 1)
    
    # Generate timestamps
    timestamps = [start_date + timedelta(hours=i) for i in range(num_rows)]
    
    # Part numbers (P001 to P010)
    part_numbers = [f'P{str(i).zfill(3)}' for i in range(1, 11)]
    
    # Line numbers (L1 to L5)
    line_numbers = [f'L{i}' for i in range(1, 6)]
    
    data = {
        'timestamp': timestamps,
        'part_number': np.random.choice(part_numbers, num_rows),
        'line_number': np.random.choice(line_numbers, num_rows),
        'planned_time': np.random.uniform(50, 60, num_rows),  # minutes
        'runtime': None,  # will be calculated
        'ideal_cycle_time': np.random.uniform(0.4, 0.6, num_rows),  # minutes per piece
        'total_pieces': np.random.randint(90, 120, num_rows),
        'good_pieces': None  # will be calculated
    }
    
    df = pd.DataFrame(data)
    
    # Calculate runtime (slightly less than planned_time)
    df['runtime'] = df['planned_time'] * np.random.uniform(0.9, 1.0, num_rows)
    
    # Calculate good_pieces (slightly less than total_pieces)
    df['good_pieces'] = (df['total_pieces'] * np.random.uniform(0.92, 0.98, num_rows)).astype(int)
    
    # Save to CSV
    df.to_csv('sample_data.csv', index=False)
    return df

if __name__ == "__main__":
    generate_sample_data(2000)
