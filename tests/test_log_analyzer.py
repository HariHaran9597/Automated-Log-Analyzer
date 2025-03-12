import sys
from pathlib import Path
import pytest
import pandas as pd
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from log_analyzer import LogAnalyzer
from test_config import test_config

@pytest.fixture
def sample_log_content():
    return [
        "2024-03-12 01:15:23 INFO Server started successfully",
        "2024-03-12 01:15:24 INFO Database connection established response_time=50.2",
        "2024-03-12 01:16:30 WARNING High CPU usage detected response_time=1200.5",
        "2024-03-12 01:17:45 ERROR Database connection failed response_time=8000.0"
    ]

@pytest.fixture
def log_analyzer(test_config, tmp_path):
    # Create temporary log directory
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    # Create sample log file
    log_file = log_dir / "test.log"
    log_file.write_text("\n".join(sample_log_content()))
    
    return LogAnalyzer(log_dir)

def test_parse_log_line(log_analyzer):
    line = "2024-03-12 01:15:24 INFO Database connection established response_time=50.2"
    result = log_analyzer.parse_log_line(line)
    
    assert result is not None
    assert result['severity'] == 'INFO'
    assert result['response_time'] == 50.2
    assert isinstance(result['timestamp'], datetime)

def test_analyze_logs(log_analyzer):
    df = log_analyzer.analyze_logs()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4
    assert 'severity' in df.columns
    assert 'response_time' in df.columns
    assert 'timestamp' in df.columns
    
    # Verify severity counts
    severity_counts = df['severity'].value_counts()
    assert severity_counts['INFO'] == 2
    assert severity_counts['WARNING'] == 1
    assert severity_counts['ERROR'] == 1

def test_generate_summary(log_analyzer):
    df = log_analyzer.analyze_logs()
    summary = log_analyzer.generate_summary(df)
    
    assert isinstance(summary, dict)
    assert summary['total_logs'] == 4
    assert summary['error_count'] == 1
    assert summary['warning_count'] == 1
    assert summary['info_count'] == 2
    assert isinstance(summary['avg_response_time'], float)