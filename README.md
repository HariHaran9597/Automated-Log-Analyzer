# Automated Log Analyzer

A Python-based log monitoring system that automatically scans server logs, detects anomalies, and generates reports/alerts for system performance issues.

## Features

- 📊 Automated log file parsing and analysis
- 📈 Data visualization of log patterns
- ⚠️ Real-time email alerts for critical failures
- 📅 Scheduled automation for continuous monitoring
- 🧹 Automatic cleanup of old reports and visualizations
- 📊 Progress tracking for long operations
- 🔄 Sample log generation for testing

## Project Structure

```
LogAnalyzer/
├── logs/           # Log files directory
├── reports/        # Generated analysis reports
├── src/           # Source code
│   ├── config.py          # Configuration settings
│   ├── log_analyzer.py    # Core log analysis logic
│   ├── visualizer.py      # Data visualization
│   ├── alert_system.py    # Email notification system
│   ├── utils.py          # Utility functions
│   ├── cli.py           # Command line interface
│   ├── log_generator.py  # Sample log generator
│   └── main.py          # Main service runner
├── tests/         # Test files
│   ├── test_alert_system.py
│   ├── test_config.py
│   ├── test_log_analyzer.py
│   ├── test_utils.py
│   └── test_visualizer.py
└── visualizations/ # Generated charts and graphs
```

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables for email alerts:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_FROM_EMAIL=your-email@gmail.com
ALERT_TO_EMAIL=recipient@example.com
```

## Usage

### Command Line Interface

The analyzer can be used through its CLI interface:

```bash
# Basic usage
python src/cli.py --log-dir logs

# Analyze logs since a specific date
python src/cli.py --since 2024-03-01

# Enable email alerts
python src/cli.py --alert

# Show system metrics
python src/cli.py --metrics

# Clean up old files
python src/cli.py --cleanup
```

### Automated Service

Run the analyzer as a service:
```bash
python src/main.py
```

The service will:
- Automatically analyze logs every hour
- Generate reports in JSON format
- Create visualizations of log patterns
- Send email alerts for critical issues
- Clean up old files daily at midnight

### Generate Sample Logs

Generate test log data:
```bash
python src/log_generator.py --entries 1000 --days 7
```

Options:
- `--entries`: Number of log entries to generate
- `--days`: Number of days to spread the logs over
- `--output-dir`: Directory to store generated logs

## Testing

Run the test suite:
```bash
pytest tests/
```

For test coverage report:
```bash
pytest --cov=src tests/
```

## Output Files

### Reports
JSON files containing:
- Total log count
- Error/Warning/Info counts
- Average response times
- Time range analysis

### Visualizations
- `severity_distribution.png`: Pie chart of log severities
- `time_series.png`: Time series of events and response times
- `hourly_distribution.png`: Heatmap of events by hour

## Configuration

All settings in `src/config.py`:
- Log patterns and parsing rules
- Alert thresholds
- Visualization settings
- Scheduling intervals
- Retention periods

## Monitoring

The analyzer logs its own activities to `logs/analyzer.log`, including:
- Analysis starts/completions
- Error notifications
- File cleanup operations
- Configuration changes

## Performance

- Progress bars for long operations
- Efficient log parsing
- Configurable cleanup policies
- System resource monitoring