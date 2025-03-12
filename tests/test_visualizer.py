import sys
from pathlib import Path
import pytest
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from visualizer import LogVisualizer

@pytest.fixture
def test_visualizer(tmp_path):
    output_dir = tmp_path / "test_visualizations"
    output_dir.mkdir()
    return LogVisualizer(output_dir)

@pytest.fixture
def sample_df():
    # Create sample data for testing visualizations
    base_time = datetime.now()
    data = []
    
    # Generate 24 hours of sample data
    for hour in range(24):
        current_time = base_time + timedelta(hours=hour)
        
        # Add some INFO logs
        data.append({
            'timestamp': current_time,
            'severity': 'INFO',
            'response_time': 100.0
        })
        
        # Add WARNING logs every 4 hours
        if hour % 4 == 0:
            data.append({
                'timestamp': current_time,
                'severity': 'WARNING',
                'response_time': 2000.0
            })
        
        # Add ERROR logs every 8 hours
        if hour % 8 == 0:
            data.append({
                'timestamp': current_time,
                'severity': 'ERROR',
                'response_time': 5000.0
            })
    
    return pd.DataFrame(data)

def test_plot_severity_distribution(test_visualizer, sample_df):
    test_visualizer.plot_severity_distribution(sample_df, "test_severity.png")
    assert (test_visualizer.output_dir / "test_severity.png").exists()

def test_plot_time_series(test_visualizer, sample_df):
    test_visualizer.plot_time_series(sample_df, "test_timeseries.png")
    assert (test_visualizer.output_dir / "test_timeseries.png").exists()

def test_plot_hourly_distribution(test_visualizer, sample_df):
    test_visualizer.plot_hourly_distribution(sample_df, "test_hourly.png")
    assert (test_visualizer.output_dir / "test_hourly.png").exists()

def test_generate_all_visualizations(test_visualizer, sample_df):
    test_visualizer.generate_all_visualizations(sample_df)
    
    expected_files = [
        "severity_distribution.png",
        "time_series.png",
        "hourly_distribution.png"
    ]
    
    for filename in expected_files:
        assert (test_visualizer.output_dir / filename).exists()

def test_visualization_style(test_visualizer):
    # Test if style settings are applied
    assert plt.style.available
    test_visualizer.setup_style()
    # Current style should match config
    assert plt.style.available