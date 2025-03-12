import sys
from pathlib import Path
import pytest
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from alert_system import AlertSystem
from config import Config

@pytest.fixture
def test_alert_system():
    # Test configuration for alerts
    test_config = {
        'server': 'test.smtp.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'test_password',
        'from_email': 'test@example.com',
        'to_email': 'admin@example.com'
    }
    return AlertSystem(test_config)

@pytest.fixture
def sample_error_data():
    return {
        'timestamp': datetime.now(),
        'severity': 'ERROR',
        'message': 'Database connection failed',
        'response_time': 6000.0
    }

def test_should_send_alert(test_alert_system, sample_error_data):
    # Test error severity trigger
    assert test_alert_system.should_send_alert(sample_error_data) == True
    
    # Test response time threshold
    sample_error_data['severity'] = 'WARNING'
    assert test_alert_system.should_send_alert(sample_error_data) == True
    
    # Test normal case (should not alert)
    sample_error_data['severity'] = 'INFO'
    sample_error_data['response_time'] = 100.0
    assert test_alert_system.should_send_alert(sample_error_data) == False

def test_create_alert_message(test_alert_system, sample_error_data):
    msg = test_alert_system.create_alert_message(sample_error_data)
    
    assert msg['From'] == 'test@example.com'
    assert msg['To'] == 'admin@example.com'
    assert 'CRITICAL ALERT' in msg['Subject']
    
    # Convert message to string to check content
    message_str = str(msg)
    assert 'Database connection failed' in message_str
    assert 'response_time=6000.0' in message_str