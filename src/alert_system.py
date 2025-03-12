import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config
from utils import setup_rotating_logger

class AlertSystem:
    def __init__(self, smtp_config=None):
        self.smtp_config = smtp_config or Config.SMTP_CONFIG
        self.thresholds = Config.ALERT_THRESHOLDS
        self.logger = setup_rotating_logger(
            'alert_system',
            Config.LOGS_DIR / 'alerts.log'
        )

    def create_alert_message(self, error_data):
        """Create an email message for the alert"""
        subject = f"CRITICAL ALERT: Log Analysis Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
        Critical Alert from Log Analyzer

        Time: {error_data.get('timestamp', 'N/A')}
        Severity: {error_data.get('severity', 'N/A')}
        Message: {error_data.get('message', 'N/A')}

        Additional Information:
        - Response Time: {error_data.get('response_time', 'N/A')} ms
        """

        msg = MIMEMultipart()
        msg['From'] = self.smtp_config['from_email']
        msg['To'] = self.smtp_config['to_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        return msg

    def send_alert(self, error_data):
        """Send an email alert for critical errors"""
        try:
            if not all([self.smtp_config['username'], self.smtp_config['password']]):
                self.logger.warning("SMTP credentials not configured. Skipping alert.")
                return False

            msg = self.create_alert_message(error_data)
            
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            self.logger.info(f"Alert sent successfully for error at {error_data.get('timestamp')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {str(e)}")
            return False

    def should_send_alert(self, error_data):
        """Determine if an alert should be sent based on error severity and thresholds"""
        if error_data['severity'] == 'ERROR':
            return True
        if error_data.get('response_time') and error_data['response_time'] > self.thresholds['response_time']:
            return True
        return False