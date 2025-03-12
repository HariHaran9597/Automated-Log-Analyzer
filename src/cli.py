import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
from log_analyzer import LogAnalyzer
from visualizer import LogVisualizer
from alert_system import AlertSystem
from config import Config
from utils import validate_config, get_system_metrics
from tqdm import tqdm

def setup_argparse():
    parser = argparse.ArgumentParser(description='Log Analyzer CLI')
    parser.add_argument('--log-dir', type=str, help='Directory containing log files')
    parser.add_argument('--report-dir', type=str, help='Directory for saving reports')
    parser.add_argument('--vis-dir', type=str, help='Directory for saving visualizations')
    parser.add_argument('--since', type=str, help='Analyze logs since (YYYY-MM-DD)')
    parser.add_argument('--alert', action='store_true', help='Enable email alerts')
    parser.add_argument('--metrics', action='store_true', help='Show system metrics')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old files')
    return parser

def process_logs_with_progress(analyzer, log_dir):
    """Process logs with progress bar"""
    log_files = list(Path(log_dir).glob('*.log'))
    all_logs = []
    
    for log_file in tqdm(log_files, desc="Processing log files"):
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in tqdm(lines, desc=f"Processing {log_file.name}", leave=False):
                    parsed = analyzer.parse_log_line(line)
                    if parsed:
                        all_logs.append(parsed)
        except Exception as e:
            logging.error(f"Error processing {log_file}: {e}")
    
    return analyzer.analyze_logs()

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Validate configuration
    if not validate_config():
        logging.error("Configuration validation failed")
        sys.exit(1)
    
    # Setup components
    analyzer = LogAnalyzer(args.log_dir if args.log_dir else Config.LOGS_DIR)
    visualizer = LogVisualizer(args.vis_dir if args.vis_dir else Config.VISUALIZATIONS_DIR)
    alert_system = AlertSystem() if args.alert else None
    
    # Show system metrics if requested
    if args.metrics:
        metrics = get_system_metrics()
        if metrics:
            print("\nSystem Metrics:")
            print(f"CPU Usage: {metrics['cpu_percent']}%")
            print(f"Memory Usage: {metrics['memory_percent']}%")
            if metrics['disk_usage']:
                print(f"Disk Usage: {metrics['disk_usage']['percent']:.1f}%")
    
    try:
        # Process logs with progress bar
        print("\nAnalyzing logs...")
        df = process_logs_with_progress(analyzer, args.log_dir or Config.LOGS_DIR)
        
        if df.empty:
            print("No logs found to analyze")
            return
        
        # Filter by date if specified
        if args.since:
            since_date = datetime.strptime(args.since, '%Y-%m-%d')
            df = df[df['timestamp'] >= since_date]
        
        # Generate and save report
        summary = analyzer.generate_summary(df)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path(args.report_dir) if args.report_dir else Config.REPORTS_DIR
        report_file = report_dir / f"log_summary_{timestamp}.json"
        analyzer.save_report(summary, report_file)
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        visualizer.generate_all_visualizations(df)
        
        # Show summary
        print("\nAnalysis Summary:")
        print(f"Total Logs: {summary['total_logs']}")
        print(f"Error Count: {summary['error_count']}")
        print(f"Warning Count: {summary['warning_count']}")
        print(f"Info Count: {summary['info_count']}")
        print(f"Average Response Time: {summary['avg_response_time']:.2f}ms")
        
        # Handle alerts if enabled
        if args.alert and alert_system:
            critical_logs = df[df['severity'] == 'ERROR']
            if not critical_logs.empty:
                print("\nSending alerts for critical errors...")
                for _, log in critical_logs.iterrows():
                    if alert_system.should_send_alert(log):
                        alert_system.send_alert(log)
        
        # Cleanup if requested
        if args.cleanup:
            from utils import cleanup_files
            cleaned = cleanup_files(Config.REPORTS_DIR, Config.RETENTION_DAYS)
            if cleaned > 0:
                print(f"\nCleaned up {cleaned} old files")
        
        print(f"\nReport saved to: {report_file}")
        print(f"Visualizations saved to: {visualizer.output_dir}")
        
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()