import time
import schedule
from datetime import datetime
from pathlib import Path
import logging
from log_analyzer import LogAnalyzer
from visualizer import LogVisualizer
from alert_system import AlertSystem
from config import Config
from utils import setup_rotating_logger

class LogAnalyzerService:
    def __init__(self):
        # Initialize logger first
        self.logger = setup_rotating_logger(
            'log_analyzer_service',
            Config.LOGS_DIR / 'service.log'
        )
        
        self.logger.info("Initializing Log Analyzer Service...")
        try:
            self.analyzer = LogAnalyzer()
            self.visualizer = LogVisualizer()
            self.alert_system = AlertSystem()
            self.create_directories()
            self.logger.info("Service initialization completed successfully")
        except Exception as e:
            self.logger.error(f"Service initialization failed: {str(e)}")
            raise

    def create_directories(self):
        """Ensure all required directories exist"""
        try:
            for directory in [Config.LOGS_DIR, Config.REPORTS_DIR, Config.VISUALIZATIONS_DIR]:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Directory ensured: {directory}")
        except Exception as e:
            self.logger.error(f"Failed to create directories: {str(e)}")
            raise

    def process_logs(self):
        """Main function to process logs and generate reports"""
        try:
            self.logger.info("Starting log analysis cycle...")
            
            # Analyze logs
            df = self.analyzer.analyze_logs()
            if df.empty:
                self.logger.warning("No logs found to analyze")
                return

            # Generate summary
            summary = self.analyzer.generate_summary(df)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = Config.REPORTS_DIR / f"log_summary_{timestamp}.json"
            self.analyzer.save_report(summary, report_file)
            
            # Generate visualizations
            viz_results = self.visualizer.generate_all_visualizations(df)
            
            # Check for critical errors and send alerts
            critical_logs = df[df['severity'] == 'ERROR']
            alerts_sent = 0
            for _, log in critical_logs.iterrows():
                if self.alert_system.should_send_alert(log):
                    if self.alert_system.send_alert(log):
                        alerts_sent += 1

            self.logger.info(
                f"Analysis cycle completed: "
                f"Processed {len(df)} logs, "
                f"Found {len(critical_logs)} critical issues, "
                f"Sent {alerts_sent} alerts, "
                f"Generated {sum(viz_results.values())}/{len(viz_results)} visualizations"
            )
            
        except Exception as e:
            self.logger.error(f"Error in log analysis cycle: {str(e)}")

    def cleanup_old_files(self, days_to_keep=None):
        """Clean up old reports and visualizations"""
        days_to_keep = days_to_keep or Config.RETENTION_DAYS
        try:
            self.logger.info(f"Starting cleanup of files older than {days_to_keep} days")
            current_time = time.time()
            deleted_count = 0
            
            for folder in [Config.REPORTS_DIR, Config.VISUALIZATIONS_DIR]:
                folder.mkdir(exist_ok=True)
                for file in folder.glob("*"):
                    if file.is_file():
                        file_time = file.stat().st_mtime
                        if current_time - file_time > days_to_keep * 86400:
                            try:
                                file.unlink()
                                deleted_count += 1
                                self.logger.debug(f"Deleted old file: {file}")
                            except Exception as e:
                                self.logger.error(f"Failed to delete file {file}: {str(e)}")
            
            self.logger.info(f"Cleanup completed. Deleted {deleted_count} old files")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

def setup_schedules(service):
    """Set up scheduled tasks"""
    try:
        # Schedule log analysis
        schedule.every(Config.SCHEDULE_CONFIG['analysis_interval']).minutes.do(
            service.process_logs
        )
        
        # Schedule daily cleanup
        schedule.every().day.at(Config.SCHEDULE_CONFIG['cleanup_time']).do(
            service.cleanup_old_files
        )
        
        return True
    except Exception as e:
        logging.error(f"Failed to setup schedules: {str(e)}")
        return False

def main():
    try:
        service = LogAnalyzerService()
        if setup_schedules(service):
            service.logger.info("Scheduled tasks configured successfully")
        else:
            service.logger.error("Failed to configure scheduled tasks")
            return
        
        # Run initial analysis
        service.process_logs()
        
        # Keep running
        service.logger.info("Starting main service loop")
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except KeyboardInterrupt:
        logging.info("Service shutdown requested")
    except Exception as e:
        logging.error(f"Fatal error in main service: {str(e)}")
    finally:
        logging.info("Service shutdown complete")

if __name__ == "__main__":
    main()