import sys
from pathlib import Path
import pytest
from datetime import datetime
import shutil
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils import format_timestamp, cleanup_files, validate_config, get_disk_usage
from config import Config

@pytest.fixture
def test_directory(tmp_path):
    """Create a temporary directory with test files"""
    # Create test files with different timestamps
    test_files = {
        'old.txt': 10,  # 10 days old
        'new.txt': 1,   # 1 day old
        'current.txt': 0 # current
    }
    
    for filename, days_old in test_files.items():
        file_path = tmp_path / filename
        file_path.write_text(f"Test content for {filename}")
        # Set file modification time
        mtime = datetime.now().timestamp() - (days_old * 86400)
        file_path.touch()
        os.utime(file_path, (mtime, mtime))
    
    return tmp_path

def test_format_timestamp():
    dt = datetime(2024, 3, 12, 15, 30, 0)
    formatted = format_timestamp(dt)
    assert formatted == "2024-03-12 15:30:00"
    assert format_timestamp(None) is None

def test_cleanup_files(test_directory):
    # Test cleanup of files older than 5 days
    removed = cleanup_files(test_directory, 5)
    assert removed == 1  # Should remove only old.txt
    
    # Verify files
    remaining_files = list(test_directory.glob('*'))
    assert len(remaining_files) == 2
    assert not (test_directory / 'old.txt').exists()
    assert (test_directory / 'new.txt').exists()
    assert (test_directory / 'current.txt').exists()

def test_validate_config(tmp_path):
    # Test with temporary directories
    Config.LOGS_DIR = tmp_path / "logs"
    Config.REPORTS_DIR = tmp_path / "reports"
    Config.VISUALIZATIONS_DIR = tmp_path / "visualizations"
    
    assert validate_config() == True
    assert Config.LOGS_DIR.exists()
    assert Config.REPORTS_DIR.exists()
    assert Config.VISUALIZATIONS_DIR.exists()

def test_get_disk_usage(tmp_path):
    usage = get_disk_usage(tmp_path)
    assert usage is not None
    assert 'total' in usage
    assert 'used' in usage
    assert 'free' in usage
    assert 'percent' in usage
    assert 0 <= usage['percent'] <= 100