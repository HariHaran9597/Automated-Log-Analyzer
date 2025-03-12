import re
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from utils import setup_rotating_logger, save_json, get_timestamp_str
from config import Config

class LogAnalyzer:
    def __init__(self, log_dir=None):
        self.log_dir = Path(log_dir) if log_dir else Config.LOGS_DIR
        self.log_patterns = Config.LOG_PATTERNS
        self.logger = setup_rotating_logger(
            'log_analyzer',
            Config.LOGS_DIR / 'analyzer.log'
        )

    def parse_log_line(self, line):
        """Parse a single log line and extract relevant information."""
        try:
            timestamp_match = re.search(self.log_patterns['timestamp'], line)
            timestamp = datetime.strptime(timestamp_match.group(), '%Y-%m-%d %H:%M:%S') if timestamp_match else None
            
            severity = 'INFO'
            if re.search(self.log_patterns['error'], line):
                severity = 'ERROR'
            elif re.search(self.log_patterns['warning'], line):
                severity = 'WARNING'
            
            response_time_match = re.search(self.log_patterns['response_time'], line)
            response_time = float(response_time_match.group(1)) if response_time_match else None
            
            return {
                'timestamp': timestamp,
                'severity': severity,
                'message': line.strip(),
                'response_time': response_time
            }
        except Exception as e:
            self.logger.error(f"Error parsing log line: {e}")
            return None

    def analyze_logs(self):
        """Analyze all log files in the log directory."""
        all_logs = []
        for log_file in self.log_dir.glob('*.log'):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        parsed = self.parse_log_line(line)
                        if parsed:
                            all_logs.append(parsed)
            except Exception as e:
                self.logger.error(f"Error processing file {log_file}: {e}")
        
        return pd.DataFrame(all_logs)

    def generate_summary(self, df):
        """Generate a summary of the analyzed logs."""
        summary = {
            'total_logs': len(df),
            'error_count': len(df[df['severity'] == 'ERROR']),
            'warning_count': len(df[df['severity'] == 'WARNING']),
            'info_count': len(df[df['severity'] == 'INFO']),
            'avg_response_time': df['response_time'].mean(),
            'max_response_time': df['response_time'].max(),
            'start_time': df['timestamp'].min(),
            'end_time': df['timestamp'].max()
        }
        return summary

    def save_report(self, summary, output_file=None):
        """Save the analysis report to a file."""
        if output_file is None:
            timestamp = get_timestamp_str()
            output_file = Config.REPORTS_DIR / f"log_summary_{timestamp}.json"
        
        output_file.parent.mkdir(exist_ok=True)
        save_json(summary, output_file)