import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest
from config import Config

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return {
        'LOGS_DIR': Path('test_data/logs'),
        'REPORTS_DIR': Path('test_data/reports'),
        'VISUALIZATIONS_DIR': Path('test_data/visualizations'),
        'LOG_PATTERNS': Config.LOG_PATTERNS,
        'ALERT_THRESHOLDS': {
            'response_time': 1000,  # Lower threshold for testing
            'error_count': 2,
            'disk_usage': 90
        }
    }