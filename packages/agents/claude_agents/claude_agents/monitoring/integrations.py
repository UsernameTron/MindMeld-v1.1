import os
import logging
import json
import time
import datetime
from typing import Dict, Any, Optional, List, Union
import threading
import socket
import platform

logger = logging.getLogger(__name__)

class MetricsExporter:
    """Base class for metrics exporters."""
    
    def __init__(self, agent_monitor):
        """
        Initialize the metrics exporter.
        
        Args:
            agent_monitor: AgentMonitor instance to export metrics from
        """
        self.agent_monitor = agent_monitor
    
    def export_metrics(self):
        """Export metrics to external system."""
        raise NotImplementedError("Subclasses must implement export_metrics")
    
    def start_periodic_export(self, interval: int = 60):
        """
        Start periodic export of metrics.
        
        Args:
            interval: Export interval in seconds
        """
        def export_periodically():
            while True:
                try:
                    self.export_metrics()
                except Exception as e:
                    logger.error(f"Error exporting metrics: {str(e)}")
                
                time.sleep(interval)
        
        export_thread = threading.Thread(target=export_periodically, daemon=True)
        export_thread.start()
        
        logger.info(f"Started periodic metrics export with interval {interval} seconds")


class PrometheusExporter(MetricsExporter):
    """Export metrics to Prometheus."""
    
    def __init__(
        self,
        agent_monitor,
        port: int = 8000,
        endpoint: str = "/metrics"
    ):
        """
        Initialize the Prometheus exporter.
        
        Args:
            agent_monitor: AgentMonitor instance to export metrics from
            port: HTTP port to serve metrics on
            endpoint: HTTP endpoint to serve metrics on
        """
        super().__init__(agent_monitor)
        self.port = port
        self.endpoint = endpoint
        
        # Initialize Prometheus client if available
        try:
            from prometheus_client import start_http_server, Counter, Gauge, Summary
            self.prometheus_available = True
            
            # API metrics
            self.api_requests = Counter(
                "claude_agents_api_requests_total",
                "Total number of Claude API requests",
                ["status"]
            )
            self.api_tokens = Counter(
                "claude_agents_api_tokens_total",
                "Total number of tokens used",
                ["type"]
            )
            self.api_cost = Counter(
                "claude_agents_api_cost_total",
                "Total API cost in USD"
            )
            self.api_response_time = Summary(
                "claude_agents_api_response_time_seconds",
                "Response time of Claude API calls"
            )
            
            # Agent metrics
            self.agent_invocations = Counter(
                "claude_agents_agent_invocations_total",
                "Total number of agent invocations",
                ["agent", "status"]
            )
            self.agent_response_time = Gauge(
                "claude_agents_agent_response_time_seconds",
                "Average response time of agent invocations",
                ["agent"]
            )
            self.agent_cost = Counter(
                "claude_agents_agent_cost_total",
                "Total cost of agent invocations",
                ["agent"]
            )
            
            # Pipeline metrics
            self.pipeline_tasks = Counter(
                "claude_agents_pipeline_tasks_total",
                "Total number of pipeline tasks",
                ["status"]
            )
            self.pipeline_iterations = Gauge(
                "claude_agents_pipeline_iterations_avg",
                "Average number of iterations per pipeline task"
            )
            self.pipeline_completion_time = Gauge(
                "claude_agents_pipeline_completion_time_seconds_avg",
                "Average completion time of pipeline tasks"
            )
            self.pipeline_token_efficiency = Gauge(
                "claude_agents_pipeline_token_efficiency",
                "Tokens used per successful task"
            )
            
            # System metrics
            self.system_uptime = Gauge(
                "claude_agents_system_uptime_seconds",
                "System uptime in seconds"
            )
            self.system_memory_usage = Gauge(
                "claude_agents_system_memory_usage_mb",
                "Memory usage in MB"
            )
            
            # Start HTTP server
            start_http_server(port)
            logger.info(f"Prometheus metrics server running on port {port} at endpoint {endpoint}")
            
        except ImportError:
            logger.warning("prometheus_client not available. Install prometheus_client to export metrics to Prometheus.")
            self.prometheus_available = False
    
    def export_metrics(self):
        """Export metrics to Prometheus."""
        if not self.prometheus_available:
            return
            
        # Get current metrics
        metrics = self.agent_monitor.get_current_metrics()
        
        # Update API metrics
        self.api_requests.labels(status="success").inc(metrics["api"]["successful_requests"])
        self.api_requests.labels(status="failure").inc(metrics["api"]["failed_requests"])
        self.api_tokens.labels(type="prompt").inc(metrics["api"]["prompt_tokens"])
        self.api_tokens.labels(type="completion").inc(metrics["api"]["completion_tokens"])
        self.api_cost.inc(metrics["api"]["total_cost"])
        
        # Update agent metrics
        for agent_type, agent_data in metrics["agents"].items():
            self.agent_invocations.labels(agent=agent_type, status="success").inc(agent_data["successful"])
            self.agent_invocations.labels(agent=agent_type, status="failure").inc(agent_data["failed"])
            self.agent_response_time.labels(agent=agent_type).set(agent_data["avg_response_time"])
            self.agent_cost.labels(agent=agent_type).inc(agent_data["total_cost"])
        
        # Update pipeline metrics
        self.pipeline_tasks.labels(status="completed").inc(metrics["pipeline"]["tasks_completed"])
        self.pipeline_tasks.labels(status="failed").inc(metrics["pipeline"]["tasks_failed"])
        self.pipeline_iterations.set(metrics["pipeline"]["avg_iterations"])
        self.pipeline_completion_time.set(metrics["pipeline"]["avg_completion_time"])
        self.pipeline_token_efficiency.set(metrics["pipeline"]["token_efficiency"])
        
        # Update system metrics
        self.system_uptime.set(metrics["system"]["uptime"])
        self.system_memory_usage.set(metrics["system"]["memory_usage_mb"])


class DatadogExporter(MetricsExporter):
    """Export metrics to Datadog."""
    
    def __init__(
        self,
        agent_monitor,
        api_key: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize the Datadog exporter.
        
        Args:
            agent_monitor: AgentMonitor instance to export metrics from
            api_key: Datadog API key (defaults to DATADOG_API_KEY environment variable)
            tags: Additional tags to add to metrics
        """
        super().__init__(agent_monitor)
        self.api_key = api_key or os.environ.get("DATADOG_API_KEY")
        self.tags = tags or []
        
        # Add standard tags
        self.tags.extend([
            f"host:{socket.gethostname()}",
            f"os:{platform.system()}",
            "service:claude-agents"
        ])
        
        # Initialize Datadog client if available
        try:
            from datadog import initialize, statsd
            self.datadog_available = True
            
            if not self.api_key:
                logger.warning("Datadog API key not provided. Some features may not work.")
                
            # Initialize Datadog
            initialize(api_key=self.api_key)
            self.statsd = statsd
            
            logger.info("Datadog metrics exporter initialized")
            
        except ImportError:
            logger.warning("datadog not available. Install datadog to export metrics to Datadog.")
            self.datadog_available = False
    
    def export_metrics(self):
        """Export metrics to Datadog."""
        if not self.datadog_available:
            return
            
        # Get current metrics
        metrics = self.agent_monitor.get_current_metrics()
        
        # Send API metrics
        self.statsd.gauge("claude_agents.api.requests.total", metrics["api"]["total_requests"], tags=self.tags)
        self.statsd.gauge("claude_agents.api.requests.successful", metrics["api"]["successful_requests"], tags=self.tags)
        self.statsd.gauge("claude_agents.api.requests.failed", metrics["api"]["failed_requests"], tags=self.tags)
        self.statsd.gauge("claude_agents.api.tokens.prompt", metrics["api"]["prompt_tokens"], tags=self.tags)
        self.statsd.gauge("claude_agents.api.tokens.completion", metrics["api"]["completion_tokens"], tags=self.tags)
        self.statsd.gauge("claude_agents.api.cost", metrics["api"]["total_cost"], tags=self.tags)
        
        # Send agent metrics
        for agent_type, agent_data in metrics["agents"].items():
            agent_tags = self.tags + [f"agent:{agent_type}"]
            self.statsd.gauge("claude_agents.agent.invocations", agent_data["invocations"], tags=agent_tags)
            self.statsd.gauge("claude_agents.agent.successful", agent_data["successful"], tags=agent_tags)
            self.statsd.gauge("claude_agents.agent.failed", agent_data["failed"], tags=agent_tags)
            self.statsd.gauge("claude_agents.agent.response_time", agent_data["avg_response_time"], tags=agent_tags)
            self.statsd.gauge("claude_agents.agent.tokens", agent_data["total_tokens"], tags=agent_tags)
            self.statsd.gauge("claude_agents.agent.cost", agent_data["total_cost"], tags=agent_tags)
        
        # Send pipeline metrics
        self.statsd.gauge("claude_agents.pipeline.tasks.completed", metrics["pipeline"]["tasks_completed"], tags=self.tags)
        self.statsd.gauge("claude_agents.pipeline.tasks.failed", metrics["pipeline"]["tasks_failed"], tags=self.tags)
        self.statsd.gauge("claude_agents.pipeline.iterations", metrics["pipeline"]["avg_iterations"], tags=self.tags)
        self.statsd.gauge("claude_agents.pipeline.completion_time", metrics["pipeline"]["avg_completion_time"], tags=self.tags)
        self.statsd.gauge("claude_agents.pipeline.token_efficiency", metrics["pipeline"]["token_efficiency"], tags=self.tags)
        
        # Send system metrics
        self.statsd.gauge("claude_agents.system.uptime", metrics["system"]["uptime"], tags=self.tags)
        self.statsd.gauge("claude_agents.system.memory", metrics["system"]["memory_usage_mb"], tags=self.tags)
        
        # Send performance metrics
        perf_metrics = self.agent_monitor.get_performance_metrics()
        self.statsd.gauge("claude_agents.performance.api_success_rate", perf_metrics["api_success_rate"] * 100, tags=self.tags)
        self.statsd.gauge("claude_agents.performance.pipeline_success_rate", perf_metrics["pipeline_success_rate"] * 100, tags=self.tags)
        
        # Send cost projection
        cost_projection = self.agent_monitor.get_daily_cost_projection()
        self.statsd.gauge("claude_agents.cost.hourly", cost_projection["hourly_cost"], tags=self.tags)
        self.statsd.gauge("claude_agents.cost.daily", cost_projection["daily_cost"], tags=self.tags)
        self.statsd.gauge("claude_agents.cost.monthly", cost_projection["monthly_cost"], tags=self.tags)


class SlackAlerter(MetricsExporter):
    """Send alerts to Slack based on metrics thresholds."""
    
    def __init__(
        self,
        agent_monitor,
        webhook_url: Optional[str] = None,
        channel: str = "#claude-agents-alerts",
        username: str = "Claude Agents Monitor",
        thresholds: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Slack alerter.
        
        Args:
            agent_monitor: AgentMonitor instance to monitor
            webhook_url: Slack webhook URL (defaults to SLACK_WEBHOOK_URL environment variable)
            channel: Slack channel to send alerts to
            username: Username to use for alerts
            thresholds: Alert thresholds (defaults to standard thresholds)
        """
        super().__init__(agent_monitor)
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
        self.channel = channel
        self.username = username
        
        # Set up default thresholds if not provided
        self.thresholds = thresholds or {
            "cost": {
                "monthly_projection": 450.0,  # Alert when monthly cost projection exceeds $450 (90% of budget)
                "daily": 15.0  # Alert when daily cost exceeds $15
            },
            "performance": {
                "api_success_rate": 0.95,  # Alert when API success rate falls below 95%
                "pipeline_success_rate": 0.90  # Alert when pipeline success rate falls below 90%
            },
            "system": {
                "memory_mb": 1000  # Alert when memory usage exceeds 1000 MB
            }
        }
        
        # Track when alerts were last sent to avoid spamming
        self.last_alert_times = {}
        self.alert_cooldown = 3600  # 1 hour cooldown between similar alerts
        
        # Check if webhook URL is provided
        if not self.webhook_url:
            logger.warning("Slack webhook URL not provided. Alerts will not be sent.")
    
    def export_metrics(self):
        """Check metrics against thresholds and send alerts if needed."""
        if not self.webhook_url:
            return
            
        # Get current metrics
        metrics = self.agent_monitor.get_current_metrics()
        perf_metrics = self.agent_monitor.get_performance_metrics()
        cost_projection = self.agent_monitor.get_daily_cost_projection()
        
        # Check cost thresholds
        if cost_projection["monthly_cost"] > self.thresholds["cost"]["monthly_projection"]:
            self._send_alert(
                "cost_monthly",
                f"🚨 Monthly cost projection of ${cost_projection['monthly_cost']:.2f} exceeds threshold of ${self.thresholds['cost']['monthly_projection']:.2f}",
                {
                    "Monthly Cost Projection": f"${cost_projection['monthly_cost']:.2f}",
                    "Budget Threshold": f"${self.thresholds['cost']['monthly_projection']:.2f}",
                    "Current Total Cost": f"${metrics['api']['total_cost']:.2f}",
                    "Hourly Cost Rate": f"${cost_projection['hourly_cost']:.2f}/hour"
                }
            )
        
        if cost_projection["daily_cost"] > self.thresholds["cost"]["daily"]:
            self._send_alert(
                "cost_daily",
                f"⚠️ Daily cost of ${cost_projection['daily_cost']:.2f} exceeds threshold of ${self.thresholds['cost']['daily']:.2f}",
                {
                    "Daily Cost": f"${cost_projection['daily_cost']:.2f}",
                    "Daily Threshold": f"${self.thresholds['cost']['daily']:.2f}",
                    "API Requests Today": metrics["api"]["total_requests"],
                    "Token Usage Today": metrics["api"]["total_tokens"]
                }
            )
        
        # Check performance thresholds
        if perf_metrics["api_success_rate"] < self.thresholds["performance"]["api_success_rate"]:
            self._send_alert(
                "api_success_rate",
                f"🔴 API success rate of {perf_metrics['api_success_rate']*100:.1f}% below threshold of {self.thresholds['performance']['api_success_rate']*100:.1f}%",
                {
                    "API Success Rate": f"{perf_metrics['api_success_rate']*100:.1f}%",
                    "Threshold": f"{self.thresholds['performance']['api_success_rate']*100:.1f}%",
                    "Successful Requests": metrics["api"]["successful_requests"],
                    "Failed Requests": metrics["api"]["failed_requests"],
                    "Common Errors": self._format_errors(metrics["api"]["error_counts"])
                }
            )
        
        if perf_metrics["pipeline_success_rate"] < self.thresholds["performance"]["pipeline_success_rate"]:
            self._send_alert(
                "pipeline_success_rate",
                f"🔴 Pipeline success rate of {perf_metrics['pipeline_success_rate']*100:.1f}% below threshold of {self.thresholds['performance']['pipeline_success_rate']*100:.1f}%",
                {
                    "Pipeline Success Rate": f"{perf_metrics['pipeline_success_rate']*100:.1f}%",
                    "Threshold": f"{self.thresholds['performance']['pipeline_success_rate']*100:.1f}%",
                    "Completed Tasks": metrics["pipeline"]["tasks_completed"],
                    "Failed Tasks": metrics["pipeline"]["tasks_failed"],
                    "Avg Iterations": f"{metrics['pipeline']['avg_iterations']:.2f}"
                }
            )
        
        # Check system thresholds
        if metrics["system"]["memory_usage_mb"] > self.thresholds["system"]["memory_mb"]:
            self._send_alert(
                "memory_usage",
                f"📈 Memory usage of {metrics['system']['memory_usage_mb']:.1f} MB exceeds threshold of {self.thresholds['system']['memory_mb']} MB",
                {
                    "Memory Usage": f"{metrics['system']['memory_usage_mb']:.1f} MB",
                    "Threshold": f"{self.thresholds['system']['memory_mb']} MB",
                    "Uptime": f"{metrics['system']['uptime'] / 3600:.1f} hours",
                    "CPU Usage": f"{metrics['system']['cpu_usage_percent']}%"
                }
            )
    
    def _send_alert(self, alert_type: str, message: str, fields: Dict[str, str]):
        """
        Send an alert to Slack if cooldown period has passed.
        
        Args:
            alert_type: Type of alert for cooldown tracking
            message: Alert message
            fields: Additional fields to include in the alert
        """
        # Check cooldown
        now = time.time()
        if alert_type in self.last_alert_times:
            time_since_last = now - self.last_alert_times[alert_type]
            if time_since_last < self.alert_cooldown:
                logger.debug(f"Skipping {alert_type} alert due to cooldown ({time_since_last:.1f}s < {self.alert_cooldown}s)")
                return
        
        # Format fields for Slack
        formatted_fields = []
        for name, value in fields.items():
            formatted_fields.append({
                "title": name,
                "value": value,
                "short": True
            })
        
        # Prepare Slack payload
        payload = {
            "channel": self.channel,
            "username": self.username,
            "text": message,
            "attachments": [
                {
                    "color": "danger",
                    "fields": formatted_fields,
                    "footer": f"Claude Agents Monitor | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        }
        
        # Send to Slack
        try:
            import requests
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Sent alert to Slack: {message}")
                self.last_alert_times[alert_type] = now
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code} {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")
    
    def _format_errors(self, error_counts: Dict[str, int]) -> str:
        """Format error counts for Slack message."""
        if not error_counts:
            return "None"
            
        # Sort by count (descending)
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 3
        top_errors = sorted_errors[:3]
        
        # Format
        return ", ".join(f"{error}: {count}" for error, count in top_errors)


class NewRelicExporter(MetricsExporter):
    """Export metrics to New Relic."""
    
    def __init__(
        self,
        agent_monitor,
        api_key: Optional[str] = None,
        app_name: str = "ClaudeAgents"
    ):
        """
        Initialize the New Relic exporter.
        
        Args:
            agent_monitor: AgentMonitor instance to export metrics from
            api_key: New Relic API key (defaults to NEW_RELIC_API_KEY environment variable)
            app_name: Application name for New Relic
        """
        super().__init__(agent_monitor)
        self.api_key = api_key or os.environ.get("NEW_RELIC_API_KEY")
        self.app_name = app_name
        
        # Initialize New Relic if available
        try:
            import newrelic.agent
            self.newrelic_available = True
            
            if not self.api_key:
                logger.warning("New Relic API key not provided. Some features may not work.")
                
            # Initialize New Relic with minimal config
            newrelic.agent.initialize(
                config_file=None,
                environment="production",
                license_key=self.api_key,
                app_name=self.app_name
            )
            self.newrelic = newrelic.agent
            
            logger.info("New Relic metrics exporter initialized")
            
        except ImportError:
            logger.warning("newrelic not available. Install newrelic to export metrics to New Relic.")
            self.newrelic_available = False
    
    def export_metrics(self):
        """Export metrics to New Relic."""
        if not self.newrelic_available:
            return
            
        # Get current metrics
        metrics = self.agent_monitor.get_current_metrics()
        perf_metrics = self.agent_monitor.get_performance_metrics()
        cost_projection = self.agent_monitor.get_daily_cost_projection()
        
        # Record custom metrics
        # API metrics
        self.newrelic.record_custom_metric("Custom/API/Requests/Total", metrics["api"]["total_requests"])
        self.newrelic.record_custom_metric("Custom/API/Requests/Successful", metrics["api"]["successful_requests"])
        self.newrelic.record_custom_metric("Custom/API/Requests/Failed", metrics["api"]["failed_requests"])
        self.newrelic.record_custom_metric("Custom/API/Tokens/Prompt", metrics["api"]["prompt_tokens"])
        self.newrelic.record_custom_metric("Custom/API/Tokens/Completion", metrics["api"]["completion_tokens"])
        self.newrelic.record_custom_metric("Custom/API/Cost/Total", metrics["api"]["total_cost"])
        
        # Agent metrics
        for agent_type, agent_data in metrics["agents"].items():
            self.newrelic.record_custom_metric(f"Custom/Agent/{agent_type}/Invocations", agent_data["invocations"])
            self.newrelic.record_custom_metric(f"Custom/Agent/{agent_type}/Successful", agent_data["successful"])
            self.newrelic.record_custom_metric(f"Custom/Agent/{agent_type}/Failed", agent_data["failed"])
            self.newrelic.record_custom_metric(f"Custom/Agent/{agent_type}/ResponseTime", agent_data["avg_response_time"])
            self.newrelic.record_custom_metric(f"Custom/Agent/{agent_type}/Tokens", agent_data["total_tokens"])
            self.newrelic.record_custom_metric(f"Custom/Agent/{agent_type}/Cost", agent_data["total_cost"])
        
        # Pipeline metrics
        self.newrelic.record_custom_metric("Custom/Pipeline/Tasks/Completed", metrics["pipeline"]["tasks_completed"])
        self.newrelic.record_custom_metric("Custom/Pipeline/Tasks/Failed", metrics["pipeline"]["tasks_failed"])
        self.newrelic.record_custom_metric("Custom/Pipeline/Iterations", metrics["pipeline"]["avg_iterations"])
        self.newrelic.record_custom_metric("Custom/Pipeline/CompletionTime", metrics["pipeline"]["avg_completion_time"])
        self.newrelic.record_custom_metric("Custom/Pipeline/TokenEfficiency", metrics["pipeline"]["token_efficiency"])
        
        # Performance metrics
        self.newrelic.record_custom_metric("Custom/Performance/API/SuccessRate", perf_metrics["api_success_rate"])
        self.newrelic.record_custom_metric("Custom/Performance/Pipeline/SuccessRate", perf_metrics["pipeline_success_rate"])
        
        # Cost projection
        self.newrelic.record_custom_metric("Custom/Cost/Hourly", cost_projection["hourly_cost"])
        self.newrelic.record_custom_metric("Custom/Cost/Daily", cost_projection["daily_cost"])
        self.newrelic.record_custom_metric("Custom/Cost/Monthly", cost_projection["monthly_cost"])
        
        # Add these metrics to the current transaction
        txn = self.newrelic.current_transaction()
        if txn:
            txn.add_custom_parameter("api_success_rate", perf_metrics["api_success_rate"])
            txn.add_custom_parameter("pipeline_success_rate", perf_metrics["pipeline_success_rate"])
            txn.add_custom_parameter("monthly_cost_projection", cost_projection["monthly_cost"])
            txn.add_custom_parameter("api_total_requests", metrics["api"]["total_requests"])