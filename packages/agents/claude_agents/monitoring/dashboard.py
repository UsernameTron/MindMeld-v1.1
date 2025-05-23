import datetime
import json
import logging
import os
import threading
import time
from collections import defaultdict
from typing import Any, Dict, Optional

# Optional dependencies for web dashboard
try:
    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from dash.dependencies import Input, Output
    from plotly.subplots import make_subplots

    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False

logger = logging.getLogger(__name__)


class AgentMonitor:
    """
    Monitoring system for Claude Agents that tracks performance metrics
    and API costs. Can output metrics to log files, JSON, or a web dashboard.
    """

    def __init__(
        self,
        log_dir: str = "logs",
        metrics_file: str = "agent_metrics.jsonl",
        log_interval: int = 60,  # seconds
        enable_dashboard: bool = False,
        dashboard_port: int = 8050,
        retention_days: int = 30,
    ):
        """
        Initialize the monitoring system.

        Args:
            log_dir: Directory to store logs and metrics
            metrics_file: File to store metrics data
            log_interval: Interval in seconds for periodic logging
            enable_dashboard: Whether to start the web dashboard
            dashboard_port: Port for the web dashboard
            retention_days: Number of days to retain metrics data
        """
        self.log_dir = log_dir
        self.metrics_file = os.path.join(log_dir, metrics_file)
        self.log_interval = log_interval
        self.enable_dashboard = enable_dashboard and DASH_AVAILABLE
        self.dashboard_port = dashboard_port
        self.retention_days = retention_days

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Initialize metrics storage
        self.metrics = {
            "api": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_cost": 0.0,
                "hourly_costs": defaultdict(float),
                "daily_costs": defaultdict(float),
                "model_usage": defaultdict(int),
                "response_times": [],
                "error_counts": defaultdict(int),
            },
            "agents": {
                "planner": {
                    "invocations": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_response_time": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                },
                "executor": {
                    "invocations": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_response_time": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                },
                "critic": {
                    "invocations": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_response_time": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                },
            },
            "pipeline": {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "avg_iterations": 0,
                "avg_completion_time": 0,
                "token_efficiency": 0,  # tokens per successful task
            },
            "system": {
                "uptime": 0,
                "start_time": time.time(),
                "last_update": time.time(),
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
            },
        }

        # Initialize historical metrics
        self.historical_metrics = []
        self._load_historical_metrics()

        # Set up periodic logging
        self._setup_periodic_logging()

        # Set up dashboard if enabled
        if self.enable_dashboard:
            self._setup_dashboard()

    def track_api_call(
        self,
        success: bool,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
        response_time: float,
        cost: float,
        error: Optional[str] = None,
    ) -> None:
        """
        Track an API call to Claude.

        Args:
            success: Whether the call was successful
            prompt_tokens: Number of prompt tokens used
            completion_tokens: Number of completion tokens used
            model: Claude model used
            response_time: Time taken for the API call in seconds
            cost: Estimated cost of the API call
            error: Error message if the call failed
        """
        # Update API metrics
        self.metrics["api"]["total_requests"] += 1

        if success:
            self.metrics["api"]["successful_requests"] += 1
        else:
            self.metrics["api"]["failed_requests"] += 1
            if error:
                self.metrics["api"]["error_counts"][error] += 1

        # Update token and cost metrics
        self.metrics["api"]["prompt_tokens"] += prompt_tokens
        self.metrics["api"]["completion_tokens"] += completion_tokens
        self.metrics["api"]["total_tokens"] += prompt_tokens + completion_tokens
        self.metrics["api"]["total_cost"] += cost

        # Update model usage
        self.metrics["api"]["model_usage"][model] += 1

        # Update response times
        self.metrics["api"]["response_times"].append(response_time)

        # Update hourly and daily costs
        now = datetime.datetime.now()
        hour_key = now.strftime("%Y-%m-%d %H:00")
        day_key = now.strftime("%Y-%m-%d")

        self.metrics["api"]["hourly_costs"][hour_key] += cost
        self.metrics["api"]["daily_costs"][day_key] += cost

        # Update system metrics
        self.metrics["system"]["last_update"] = time.time()
        self.metrics["system"]["uptime"] = (
            time.time() - self.metrics["system"]["start_time"]
        )

        # Update memory and CPU usage if psutil is available
        try:
            import psutil

            process = psutil.Process(os.getpid())
            self.metrics["system"]["memory_usage_mb"] = process.memory_info().rss / (
                1024 * 1024
            )
            self.metrics["system"]["cpu_usage_percent"] = process.cpu_percent(
                interval=0.1
            )
        except ImportError:
            pass

    def track_agent_invocation(
        self,
        agent_type: str,
        success: bool,
        response_time: float,
        tokens_used: int,
        cost: float,
    ) -> None:
        """
        Track an agent invocation.

        Args:
            agent_type: Type of agent (planner, executor, critic)
            success: Whether the invocation was successful
            response_time: Time taken for the invocation in seconds
            tokens_used: Total tokens used
            cost: Estimated cost of the invocation
        """
        if agent_type not in self.metrics["agents"]:
            self.metrics["agents"][agent_type] = {
                "invocations": 0,
                "successful": 0,
                "failed": 0,
                "avg_response_time": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
            }

        # Update agent metrics
        agent_metrics = self.metrics["agents"][agent_type]
        agent_metrics["invocations"] += 1

        if success:
            agent_metrics["successful"] += 1
        else:
            agent_metrics["failed"] += 1

        # Update rolling average response time
        if agent_metrics["invocations"] == 1:
            agent_metrics["avg_response_time"] = response_time
        else:
            agent_metrics["avg_response_time"] = (
                agent_metrics["avg_response_time"] * (agent_metrics["invocations"] - 1)
                + response_time
            ) / agent_metrics["invocations"]

        # Update tokens and cost
        agent_metrics["total_tokens"] += tokens_used
        agent_metrics["total_cost"] += cost

    def track_pipeline_task(
        self, success: bool, iterations: int, completion_time: float, total_tokens: int
    ) -> None:
        """
        Track a pipeline task execution.

        Args:
            success: Whether the task was completed successfully
            iterations: Number of iterations taken
            completion_time: Time taken to complete the task in seconds
            total_tokens: Total tokens used across all agents
        """
        # Update pipeline metrics
        if success:
            self.metrics["pipeline"]["tasks_completed"] += 1
        else:
            self.metrics["pipeline"]["tasks_failed"] += 1

        total_tasks = (
            self.metrics["pipeline"]["tasks_completed"]
            + self.metrics["pipeline"]["tasks_failed"]
        )

        # Update rolling average metrics
        if total_tasks == 1:
            self.metrics["pipeline"]["avg_iterations"] = iterations
            self.metrics["pipeline"]["avg_completion_time"] = completion_time
        else:
            self.metrics["pipeline"]["avg_iterations"] = (
                self.metrics["pipeline"]["avg_iterations"] * (total_tasks - 1)
                + iterations
            ) / total_tasks

            self.metrics["pipeline"]["avg_completion_time"] = (
                self.metrics["pipeline"]["avg_completion_time"] * (total_tasks - 1)
                + completion_time
            ) / total_tasks

        # Update token efficiency
        if self.metrics["pipeline"]["tasks_completed"] > 0:
            self.metrics["pipeline"]["token_efficiency"] = (
                self.metrics["api"]["total_tokens"]
                / self.metrics["pipeline"]["tasks_completed"]
            )

    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get the current metrics.

        Returns:
            Current metrics dictionary
        """
        # Update system metrics before returning
        self.metrics["system"]["uptime"] = (
            time.time() - self.metrics["system"]["start_time"]
        )

        # Create a copy to avoid external modification
        return json.loads(json.dumps(self.metrics))

    def get_daily_cost_projection(self) -> Dict[str, Any]:
        """
        Get cost projection based on current usage.

        Returns:
            Dictionary with cost projections
        """
        # Calculate cost rate
        uptime_hours = self.metrics["system"]["uptime"] / 3600
        if uptime_hours < 1:
            uptime_hours = 1  # Avoid division by zero

        hourly_cost = self.metrics["api"]["total_cost"] / uptime_hours
        daily_cost = hourly_cost * 24
        monthly_cost = daily_cost * 30.44  # Average days in month
        annual_cost = monthly_cost * 12

        # Calculate request rate
        requests_per_hour = self.metrics["api"]["total_requests"] / uptime_hours

        return {
            "current_cost": self.metrics["api"]["total_cost"],
            "uptime_hours": uptime_hours,
            "hourly_cost": hourly_cost,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "annual_cost": annual_cost,
            "requests_per_hour": requests_per_hour,
            "within_budget": monthly_cost <= 500,  # Check against $500 monthly budget
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance-related metrics.

        Returns:
            Dictionary with performance metrics
        """
        # Calculate success rates
        api_success_rate = 0
        if self.metrics["api"]["total_requests"] > 0:
            api_success_rate = (
                self.metrics["api"]["successful_requests"]
                / self.metrics["api"]["total_requests"]
            )

        pipeline_success_rate = 0
        total_tasks = (
            self.metrics["pipeline"]["tasks_completed"]
            + self.metrics["pipeline"]["tasks_failed"]
        )
        if total_tasks > 0:
            pipeline_success_rate = (
                self.metrics["pipeline"]["tasks_completed"] / total_tasks
            )

        # Calculate average response time
        avg_response_time = 0
        if self.metrics["api"]["response_times"]:
            avg_response_time = sum(self.metrics["api"]["response_times"]) / len(
                self.metrics["api"]["response_times"]
            )

        # Return performance metrics
        return {
            "api_success_rate": api_success_rate,
            "pipeline_success_rate": pipeline_success_rate,
            "avg_response_time": avg_response_time,
            "avg_task_completion_time": self.metrics["pipeline"]["avg_completion_time"],
            "avg_iterations_per_task": self.metrics["pipeline"]["avg_iterations"],
            "token_efficiency": self.metrics["pipeline"]["token_efficiency"],
        }

    def log_current_metrics(self) -> None:
        """Log current metrics to file."""
        # Get current metrics with timestamp
        current_metrics = self.get_current_metrics()
        timestamp = datetime.datetime.now().isoformat()

        metrics_entry = {"timestamp": timestamp, "metrics": current_metrics}

        # Add to historical metrics
        self.historical_metrics.append(metrics_entry)

        # Write to metrics file
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(metrics_entry) + "\n")

        # Log summary to system log
        logger.info(
            f"Metrics update: API calls={current_metrics['api']['total_requests']}, "
            f"Cost=${current_metrics['api']['total_cost']:.2f}, "
            f"Tasks completed={current_metrics['pipeline']['tasks_completed']}"
        )

        # Clean up old metrics data
        self._cleanup_old_metrics()

    def _load_historical_metrics(self) -> None:
        """Load historical metrics from file."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, "r") as f:
                    for line in f:
                        try:
                            metrics_entry = json.loads(line.strip())
                            self.historical_metrics.append(metrics_entry)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse metrics line: {line}")

                logger.info(
                    f"Loaded {len(self.historical_metrics)} historical metrics entries"
                )
            except Exception as e:
                logger.error(f"Error loading historical metrics: {str(e)}")

    def _cleanup_old_metrics(self) -> None:
        """Clean up metrics data older than retention_days."""
        if not self.historical_metrics:
            return

        now = datetime.datetime.now()
        cutoff_date = now - datetime.timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.isoformat()

        # Filter out old metrics
        self.historical_metrics = [
            entry
            for entry in self.historical_metrics
            if entry.get("timestamp", "") >= cutoff_str
        ]

        # Rewrite metrics file if we removed any entries
        original_count = len(self.historical_metrics)
        if original_count < len(self.historical_metrics):
            with open(self.metrics_file, "w") as f:
                for entry in self.historical_metrics:
                    f.write(json.dumps(entry) + "\n")

            logger.info(
                f"Cleaned up {original_count - len(self.historical_metrics)} old metrics entries"
            )

    def _setup_periodic_logging(self) -> None:
        """Set up periodic logging of metrics."""

        def log_periodically():
            while True:
                time.sleep(self.log_interval)
                self.log_current_metrics()

        # Start logging thread
        logging_thread = threading.Thread(target=log_periodically, daemon=True)
        logging_thread.start()

    def _setup_dashboard(self) -> None:
        """Set up the web dashboard if Dash is available."""
        if not DASH_AVAILABLE:
            logger.warning(
                "Dash not available. Install dash, pandas, and plotly to enable the web dashboard."
            )
            return

        # Create Dash app
        app = dash.Dash(__name__, title="Claude Agents Monitoring")

        # Define layout
        app.layout = html.Div(
            [
                html.H1("Claude Agents Monitoring Dashboard"),
                dcc.Tabs(
                    [
                        # Overview tab
                        dcc.Tab(
                            label="Overview",
                            children=[
                                html.Div(
                                    [
                                        html.H2("System Overview"),
                                        html.Div(id="overview-stats"),
                                        html.H3("Cost Projection"),
                                        html.Div(id="cost-projection"),
                                        dcc.Graph(id="daily-cost-chart"),
                                    ]
                                )
                            ],
                        ),
                        # API metrics tab
                        dcc.Tab(
                            label="API Metrics",
                            children=[
                                html.Div(
                                    [
                                        html.H2("API Usage"),
                                        html.Div(id="api-stats"),
                                        dcc.Graph(id="api-usage-chart"),
                                        dcc.Graph(id="model-usage-chart"),
                                    ]
                                )
                            ],
                        ),
                        # Agent metrics tab
                        dcc.Tab(
                            label="Agent Metrics",
                            children=[
                                html.Div(
                                    [
                                        html.H2("Agent Performance"),
                                        html.Div(id="agent-stats"),
                                        dcc.Graph(id="agent-performance-chart"),
                                    ]
                                )
                            ],
                        ),
                        # Pipeline metrics tab
                        dcc.Tab(
                            label="Pipeline Metrics",
                            children=[
                                html.Div(
                                    [
                                        html.H2("Pipeline Performance"),
                                        html.Div(id="pipeline-stats"),
                                        dcc.Graph(id="pipeline-performance-chart"),
                                    ]
                                )
                            ],
                        ),
                    ]
                ),
                # Refresh interval
                dcc.Interval(
                    id="interval-component",
                    interval=5 * 1000,  # 5 seconds in milliseconds
                    n_intervals=0,
                ),
            ]
        )

        # Define callbacks
        @app.callback(
            Output("overview-stats", "children"),
            Input("interval-component", "n_intervals"),
        )
        def update_overview_stats(n):
            metrics = self.get_current_metrics()

            return html.Div(
                [
                    html.P(f"Uptime: {metrics['system']['uptime'] / 3600:.1f} hours"),
                    html.P(f"Total API calls: {metrics['api']['total_requests']}"),
                    html.P(f"Total cost: ${metrics['api']['total_cost']:.2f}"),
                    html.P(f"Total tokens: {metrics['api']['total_tokens']}"),
                    html.P(
                        f"Tasks completed: {metrics['pipeline']['tasks_completed']}"
                    ),
                    html.P(
                        f"Memory usage: {metrics['system']['memory_usage_mb']:.1f} MB"
                    ),
                ]
            )

        @app.callback(
            Output("cost-projection", "children"),
            Input("interval-component", "n_intervals"),
        )
        def update_cost_projection(n):
            projection = self.get_daily_cost_projection()
            budget_status = (
                "Within budget" if projection["within_budget"] else "Exceeding budget"
            )

            return html.Div(
                [
                    html.P(f"Hourly cost: ${projection['hourly_cost']:.2f}"),
                    html.P(f"Daily cost: ${projection['daily_cost']:.2f}"),
                    html.P(f"Monthly projection: ${projection['monthly_cost']:.2f}"),
                    html.P(f"Annual projection: ${projection['annual_cost']:.2f}"),
                    html.P(
                        f"Budget status: {budget_status}",
                        style={
                            "color": "green" if projection["within_budget"] else "red"
                        },
                    ),
                ]
            )

        @app.callback(
            Output("daily-cost-chart", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_daily_cost_chart(n):
            metrics = self.get_current_metrics()
            daily_costs = metrics["api"]["daily_costs"]

            if not daily_costs:
                # Return empty chart if no data
                return go.Figure()

            # Convert to dataframe
            df = pd.DataFrame(
                [{"date": date, "cost": cost} for date, cost in daily_costs.items()]
            )

            fig = px.bar(
                df,
                x="date",
                y="cost",
                title="Daily API Costs",
                labels={"date": "Date", "cost": "Cost ($)"},
            )

            return fig

        @app.callback(
            Output("api-stats", "children"), Input("interval-component", "n_intervals")
        )
        def update_api_stats(n):
            metrics = self.get_current_metrics()
            api_metrics = metrics["api"]

            success_rate = 0
            if api_metrics["total_requests"] > 0:
                success_rate = (
                    api_metrics["successful_requests"]
                    / api_metrics["total_requests"]
                    * 100
                )

            return html.Div(
                [
                    html.P(f"Total requests: {api_metrics['total_requests']}"),
                    html.P(
                        f"Successful requests: {api_metrics['successful_requests']}"
                    ),
                    html.P(f"Failed requests: {api_metrics['failed_requests']}"),
                    html.P(f"Success rate: {success_rate:.1f}%"),
                    html.P(f"Prompt tokens: {api_metrics['prompt_tokens']}"),
                    html.P(f"Completion tokens: {api_metrics['completion_tokens']}"),
                ]
            )

        @app.callback(
            Output("api-usage-chart", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_api_usage_chart(n):
            # Convert historical metrics to dataframe
            if not self.historical_metrics:
                return go.Figure()

            data = []
            for entry in self.historical_metrics:
                metrics = entry["metrics"]
                data.append(
                    {
                        "timestamp": entry["timestamp"],
                        "total_requests": metrics["api"]["total_requests"],
                        "successful_requests": metrics["api"]["successful_requests"],
                        "failed_requests": metrics["api"]["failed_requests"],
                    }
                )

            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            fig = px.line(
                df,
                x="timestamp",
                y=["total_requests", "successful_requests", "failed_requests"],
                title="API Usage Over Time",
                labels={"timestamp": "Time", "value": "Count", "variable": "Metric"},
            )

            return fig

        @app.callback(
            Output("model-usage-chart", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_model_usage_chart(n):
            metrics = self.get_current_metrics()
            model_usage = metrics["api"]["model_usage"]

            if not model_usage:
                return go.Figure()

            # Convert to dataframe
            df = pd.DataFrame(
                [
                    {"model": model, "count": count}
                    for model, count in model_usage.items()
                ]
            )

            fig = px.pie(
                df, values="count", names="model", title="Model Usage Distribution"
            )

            return fig

        @app.callback(
            Output("agent-stats", "children"),
            Input("interval-component", "n_intervals"),
        )
        def update_agent_stats(n):
            metrics = self.get_current_metrics()
            agent_metrics = metrics["agents"]

            # Create stats for each agent
            agent_stats = []
            for agent_type, agent_data in agent_metrics.items():
                success_rate = 0
                if agent_data["invocations"] > 0:
                    success_rate = (
                        agent_data["successful"] / agent_data["invocations"] * 100
                    )

                agent_stats.append(
                    html.Div(
                        [
                            html.H4(f"{agent_type.capitalize()} Agent"),
                            html.P(f"Invocations: {agent_data['invocations']}"),
                            html.P(f"Success rate: {success_rate:.1f}%"),
                            html.P(
                                f"Avg response time: {agent_data['avg_response_time']:.2f} sec"
                            ),
                            html.P(f"Total tokens: {agent_data['total_tokens']}"),
                            html.P(f"Total cost: ${agent_data['total_cost']:.2f}"),
                        ]
                    )
                )

            return html.Div(agent_stats)

        @app.callback(
            Output("agent-performance-chart", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_agent_performance_chart(n):
            metrics = self.get_current_metrics()
            agent_metrics = metrics["agents"]

            # Create data for chart
            data = []
            for agent_type, agent_data in agent_metrics.items():
                if agent_data["invocations"] > 0:
                    success_rate = (
                        agent_data["successful"] / agent_data["invocations"] * 100
                    )
                    data.append(
                        {
                            "agent": agent_type,
                            "success_rate": success_rate,
                            "avg_response_time": agent_data["avg_response_time"],
                            "invocations": agent_data["invocations"],
                        }
                    )

            if not data:
                return go.Figure()

            df = pd.DataFrame(data)

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=df["agent"],
                    y=df["success_rate"],
                    name="Success Rate (%)",
                    marker_color="green",
                )
            )

            fig.add_trace(
                go.Bar(
                    x=df["agent"],
                    y=df["avg_response_time"],
                    name="Avg Response Time (sec)",
                    marker_color="blue",
                    yaxis="y2",
                )
            )

            fig.update_layout(
                title="Agent Performance Metrics",
                yaxis=dict(title="Success Rate (%)"),
                yaxis2=dict(
                    title="Avg Response Time (sec)", overlaying="y", side="right"
                ),
                barmode="group",
            )

            return fig

        @app.callback(
            Output("pipeline-stats", "children"),
            Input("interval-component", "n_intervals"),
        )
        def update_pipeline_stats(n):
            metrics = self.get_current_metrics()
            pipeline_metrics = metrics["pipeline"]

            success_rate = 0
            total_tasks = (
                pipeline_metrics["tasks_completed"] + pipeline_metrics["tasks_failed"]
            )
            if total_tasks > 0:
                success_rate = pipeline_metrics["tasks_completed"] / total_tasks * 100

            return html.Div(
                [
                    html.P(f"Tasks completed: {pipeline_metrics['tasks_completed']}"),
                    html.P(f"Tasks failed: {pipeline_metrics['tasks_failed']}"),
                    html.P(f"Success rate: {success_rate:.1f}%"),
                    html.P(
                        f"Avg iterations per task: {pipeline_metrics['avg_iterations']:.2f}"
                    ),
                    html.P(
                        f"Avg completion time: {pipeline_metrics['avg_completion_time']:.2f} sec"
                    ),
                    html.P(
                        f"Token efficiency: {pipeline_metrics['token_efficiency']:.1f} tokens/task"
                    ),
                ]
            )

        @app.callback(
            Output("pipeline-performance-chart", "figure"),
            Input("interval-component", "n_intervals"),
        )
        def update_pipeline_performance_chart(n):
            # Convert historical metrics to dataframe
            if not self.historical_metrics:
                return go.Figure()

            data = []
            for entry in self.historical_metrics:
                metrics = entry["metrics"]
                pipeline = metrics["pipeline"]

                total_tasks = pipeline["tasks_completed"] + pipeline["tasks_failed"]
                success_rate = 0
                if total_tasks > 0:
                    success_rate = pipeline["tasks_completed"] / total_tasks * 100

                data.append(
                    {
                        "timestamp": entry["timestamp"],
                        "tasks_completed": pipeline["tasks_completed"],
                        "avg_iterations": pipeline["avg_iterations"],
                        "avg_completion_time": pipeline["avg_completion_time"],
                        "success_rate": success_rate,
                    }
                )

            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Create dual-axis figure
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["success_rate"],
                    name="Success Rate (%)",
                    line=dict(color="green"),
                ),
                secondary_y=False,
            )

            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["avg_completion_time"],
                    name="Avg Completion Time (sec)",
                    line=dict(color="blue"),
                ),
                secondary_y=True,
            )

            fig.update_layout(
                title="Pipeline Performance Over Time",
                xaxis=dict(title="Time"),
                yaxis=dict(title="Success Rate (%)"),
                yaxis2=dict(title="Avg Completion Time (sec)"),
            )

            return fig

        # Run the dashboard server in a separate thread
        def run_dashboard():
            app.run_server(debug=False, port=self.dashboard_port)

        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()

        logger.info(
            f"Monitoring dashboard running at http://localhost:{self.dashboard_port}"
        )


# Decorator for tracking agent invocations
def track_agent(monitor: AgentMonitor):
    """
    Decorator for tracking agent invocations.

    Args:
        monitor: AgentMonitor instance

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            success = True
            tokens_used = 0
            cost = 0.0

            try:
                result = func(self, *args, **kwargs)

                # Try to extract token usage and cost from result
                if hasattr(self, "token_counter") and hasattr(self, "last_tokens_used"):
                    tokens_used = self.last_tokens_used
                    cost = self.last_cost

                return result
            except Exception as e:
                success = False
                raise
            finally:
                response_time = time.time() - start_time
                agent_type = self.__class__.__name__.lower().replace("agent", "")
                monitor.track_agent_invocation(
                    agent_type=agent_type,
                    success=success,
                    response_time=response_time,
                    tokens_used=tokens_used,
                    cost=cost,
                )

        return wrapper

    return decorator


# Decorator for tracking pipeline tasks
def track_pipeline(monitor: AgentMonitor):
    """
    Decorator for tracking pipeline tasks.

    Args:
        monitor: AgentMonitor instance

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            success = True
            iterations = 0
            total_tokens = 0

            try:
                result = func(self, *args, **kwargs)

                # Try to extract data from result
                if isinstance(result, dict):
                    success = result.get("status") == "completed"
                    iterations = result.get("iterations", 0)

                    # Try to extract token usage
                    if (
                        "final_results" in result
                        and "step_results" in result["final_results"]
                    ):
                        for step_result in result["final_results"][
                            "step_results"
                        ].values():
                            if (
                                isinstance(step_result, dict)
                                and "tokens" in step_result
                            ):
                                total_tokens += step_result.get("tokens", 0)

                return result
            except Exception as e:
                success = False
                raise
            finally:
                completion_time = time.time() - start_time
                monitor.track_pipeline_task(
                    success=success,
                    iterations=iterations,
                    completion_time=completion_time,
                    total_tokens=total_tokens,
                )

        return wrapper

    return decorator
