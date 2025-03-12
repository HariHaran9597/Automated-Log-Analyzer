import random
from datetime import datetime, timedelta
import argparse
from pathlib import Path
import logging

class LogGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.severities = {
            'INFO': 0.7,      # 70% chance
            'WARNING': 0.2,   # 20% chance
            'ERROR': 0.1      # 10% chance
        }
        
        self.messages = {
            'INFO': [
                'User login successful',
                'Database query completed',
                'Cache refreshed',
                'Request processed successfully',
                'Data backup completed'
            ],
            'WARNING': [
                'High CPU usage detected',
                'Memory usage above 80%',
                'Disk usage above 90%',
                'Slow database response',
                'Cache miss rate increasing'
            ],
            'ERROR': [
                'Database connection failed',
                'API endpoint timeout',
                'Authentication failed',
                'Out of memory error',
                'File system error'
            ]
        }

    def generate_timestamp(self, start_time, end_time):
        time_diff = end_time - start_time
        random_seconds = random.randint(0, int(time_diff.total_seconds()))
        return start_time + timedelta(seconds=random_seconds)

    def generate_response_time(self, severity):
        if severity == 'ERROR':
            return random.uniform(5000, 15000)  # 5-15 seconds
        elif severity == 'WARNING':
            return random.uniform(1000, 5000)   # 1-5 seconds
        else:
            return random.uniform(50, 1000)     # 50ms-1 second

    def generate_log_entry(self, timestamp):
        severity = random.choices(list(self.severities.keys()), 
                                weights=list(self.severities.values()))[0]
        message = random.choice(self.messages[severity])
        response_time = self.generate_response_time(severity)
        
        return f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {severity} {message} response_time={response_time:.1f}"

    def generate_logs(self, num_entries, start_time=None, end_time=None):
        if start_time is None:
            start_time = datetime.now() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.now()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"generated_logs_{timestamp}.log"
        
        try:
            with open(output_file, 'w') as f:
                for _ in range(num_entries):
                    timestamp = self.generate_timestamp(start_time, end_time)
                    log_entry = self.generate_log_entry(timestamp)
                    f.write(log_entry + '\n')
                    
            print(f"Generated {num_entries} log entries in {output_file}")
            return str(output_file)
            
        except Exception as e:
            logging.error(f"Error generating logs: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Generate sample log files for testing')
    parser.add_argument('--output-dir', type=str, default='logs',
                        help='Directory to store generated logs')
    parser.add_argument('--entries', type=int, default=1000,
                        help='Number of log entries to generate')
    parser.add_argument('--days', type=int, default=1,
                        help='Number of days to spread the logs over')
    
    args = parser.parse_args()
    
    generator = LogGenerator(args.output_dir)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=args.days)
    
    generator.generate_logs(args.entries, start_time, end_time)

if __name__ == "__main__":
    main()