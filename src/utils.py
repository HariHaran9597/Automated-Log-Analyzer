import os
import shutil
import psutil
from pathlib import Path
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from config import Config

def setup_rotating_logger(name, log_file, level=logging.INFO):
    """Setup a rotating file logger"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

def save_json(data, filepath):
    """Save data to JSON file"""
    import json
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, default=str)

def get_timestamp_str():
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_disk_usage(path):
    """Get disk usage information for a given path"""
    try:
        usage = shutil.disk_usage(path)
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': (usage.used / usage.total) * 100
        }
    except Exception as e:
        logging.error(f"Error getting disk usage: {e}")
        return None

def get_system_metrics():
    """Get current system metrics"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': get_disk_usage(Config.BASE_DIR)
        }
    except Exception as e:
        logging.error(f"Error getting system metrics: {e}")
        return None

def format_timestamp(dt):
    """Format datetime object to string"""
    return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

def validate_log_directory():
    """Validate and create log directory if not exists"""
    try:
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error validating log directory: {e}")
        return False

def cleanup_files(directory, max_age_days):
    """Clean up files older than max_age_days in the specified directory"""
    try:
        directory = Path(directory)
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_days * 86400
        
        removed_files = 0
        for file in directory.glob('*'):
            if file.is_file():
                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    file.unlink()
                    removed_files += 1
        
        return removed_files
    except Exception as e:
        logging.error(f"Error cleaning up files: {e}")
        return -1

def validate_config():
    """Validate configuration settings"""
    required_dirs = [Config.LOGS_DIR, Config.REPORTS_DIR, Config.VISUALIZATIONS_DIR]
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                missing_dirs.append(str(dir_path))
                logging.error(f"Error creating directory {dir_path}: {e}")
    
    return len(missing_dirs) == 0