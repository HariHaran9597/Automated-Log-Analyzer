import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import seaborn as sns
from config import Config
from utils import setup_rotating_logger, get_timestamp_str

class LogVisualizer:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else Config.VISUALIZATIONS_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.logger = setup_rotating_logger(
            'visualizer',
            Config.LOGS_DIR / 'visualizer.log'
        )
        self.setup_style()

    def setup_style(self):
        """Set up the visual style for plots"""
        try:
            plt.style.use(Config.VISUALIZATION_CONFIG['style'])
            sns.set_palette(Config.VISUALIZATION_CONFIG['color_palette'])
        except Exception as e:
            self.logger.error(f"Error setting up visualization style: {str(e)}")

    def save_plot(self, filename, fig=None):
        """Save plot with proper error handling"""
        try:
            if fig is None:
                fig = plt.gcf()
            filepath = self.output_dir / filename
            fig.savefig(filepath, dpi=Config.VISUALIZATION_CONFIG['dpi'])
            plt.close(fig)
            self.logger.info(f"Successfully saved visualization: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving visualization {filename}: {str(e)}")
            return False

    def plot_severity_distribution(self, df, filename=None):
        """Create a pie chart of log severity distribution"""
        try:
            if filename is None:
                filename = f"severity_distribution_{get_timestamp_str()}.png"
            
            fig, ax = plt.subplots(figsize=Config.VISUALIZATION_CONFIG['figure_size'])
            severity_counts = df['severity'].value_counts()
            plt.pie(severity_counts, labels=severity_counts.index, autopct='%1.1f%%')
            plt.title('Distribution of Log Severity Levels')
            
            return self.save_plot(filename, fig)
        except Exception as e:
            self.logger.error(f"Error creating severity distribution plot: {str(e)}")
            return False

    def plot_time_series(self, df, filename=None):
        """Create a time series plot of errors and response times"""
        try:
            if filename is None:
                filename = f"time_series_{get_timestamp_str()}.png"
            
            fig, ax1 = plt.subplots(figsize=Config.VISUALIZATION_CONFIG['figure_size'])
            
            # Create severity counts by time
            severity_by_time = df.set_index('timestamp')['severity'].value_counts().unstack().fillna(0)
            
            # Plot severity counts
            severity_by_time.plot(kind='line', ax=ax1)
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Number of Logs')
            
            # Plot response times on secondary y-axis if available
            if 'response_time' in df.columns and df['response_time'].notna().any():
                ax2 = ax1.twinx()
                df.set_index('timestamp')['response_time'].rolling(window=10).mean().plot(
                    color='red', linestyle='--', ax=ax2, label='Avg Response Time'
                )
                ax2.set_ylabel('Response Time (ms)')
            
            plt.title('Log Events and Response Times Over Time')
            return self.save_plot(filename, fig)
        except Exception as e:
            self.logger.error(f"Error creating time series plot: {str(e)}")
            return False

    def plot_hourly_distribution(self, df, filename=None):
        """Create a heatmap of log events by hour and severity"""
        try:
            if filename is None:
                filename = f"hourly_distribution_{get_timestamp_str()}.png"
            
            fig, ax = plt.subplots(figsize=Config.VISUALIZATION_CONFIG['figure_size'])
            
            df['hour'] = df['timestamp'].dt.hour
            hourly_severity = pd.crosstab(df['hour'], df['severity'])
            
            sns.heatmap(hourly_severity, cmap='YlOrRd', annot=True, fmt='d', ax=ax)
            plt.title('Hourly Distribution of Log Events by Severity')
            plt.xlabel('Severity Level')
            plt.ylabel('Hour of Day')
            
            return self.save_plot(filename, fig)
        except Exception as e:
            self.logger.error(f"Error creating hourly distribution plot: {str(e)}")
            return False

    def generate_all_visualizations(self, df):
        """Generate all available visualizations"""
        self.logger.info("Starting visualization generation...")
        
        results = {
            'severity_distribution': self.plot_severity_distribution(df),
            'time_series': self.plot_time_series(df),
            'hourly_distribution': self.plot_hourly_distribution(df)
        }
        
        success_count = sum(results.values())
        total_count = len(results)
        
        self.logger.info(f"Visualization generation completed. {success_count}/{total_count} visualizations created successfully.")
        return results