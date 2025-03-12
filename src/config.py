import os
from pathlib import Path

class Config:
    # Base directory configuration
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = BASE_DIR / "reports"
    VISUALIZATIONS_DIR = BASE_DIR / "visualizations"

    # Log analysis configuration
    LOG_PATTERNS = {
        'timestamp': r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}',
        'error': r'ERROR|CRITICAL|FATAL',
        'warning': r'WARNING|WARN',
        'info': r'INFO',
        'response_time': r'response_time=(\d+\.?\d*)',
    }

    # Alert configuration
    ALERT_THRESHOLDS = {
        'response_time': 5000,  # ms
        'error_count': 5,  # errors per hour
        'disk_usage': 90,  # percentage
    }

    # Email configuration
    SMTP_CONFIG = {
        'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'from_email': os.getenv('ALERT_FROM_EMAIL', ''),
        'to_email': os.getenv('ALERT_TO_EMAIL', '')
    }

    # Visualization settings
    VISUALIZATION_CONFIG = {
        'figure_size': (12, 8),
        'style': 'seaborn',
        'color_palette': 'husl',
        'dpi': 100
    }

    # Retention configuration
    RETENTION_DAYS = 7  # How long to keep old reports and visualizations

    # Scheduling configuration
    SCHEDULE_CONFIG = {
        'analysis_interval': 60,  # minutes
        'cleanup_time': "00:00"   # Daily cleanup time
    }