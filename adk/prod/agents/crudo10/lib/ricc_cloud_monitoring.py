# ricc_cloud_monitoring.py

import os
import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from google.cloud import monitoring_v3, run_v2
from google.protobuf.timestamp_pb2 import Timestamp
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from .ricc_system import * # log_function_called, log_function_call_output
#from .ricc_funcall_wrapper import ricc_fun_call_wrapper
# Required imports (ensure these are available in the scope where this function is defined)
import datetime

# --- Constants ---
DEFAULT_HOURS_BACK_GLOBAL = 24
# Default alignment for most metrics
DEFAULT_ALIGNMENT_SECONDS = 60 # * 5
# Specific shorter alignment for potentially "spiky" network traffic
NETWORK_ALIGNMENT_SECONDS = 60 # Use 1 minute for network traffic
LATENCY_PERCENTILE_DEFAULT = 95.0

class RiccCloudMonitoring:
    """
    A class to simplify fetching Cloud Monitoring metrics and generating charts.
    Handles GCP client initialization, project context, and default settings.
    """

    def __init__(self,
                 project_id: Optional[str] = None,
                 default_region: Optional[str] = None,
                 default_cloud_run_service: Optional[str] = None,
                 default_hours_back: float = DEFAULT_HOURS_BACK_GLOBAL,
                 output_dir_base: Union[str, Path] = ".cache"):
        """Initializes the RiccCloudMonitoring instance."""
        load_dotenv()
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.default_region = default_region or os.getenv("GOOGLE_CLOUD_LOCATION")
        self.default_cloud_run_service = default_cloud_run_service or os.getenv("FAVORITE_CLOUD_RUN_SERVICE")
        self.default_hours_back = default_hours_back
        if not self.project_id: raise ValueError("Project ID required.")
        if not self.default_region: print("Warning: Default region not set.")
        self.output_dir_base = Path(output_dir_base)
        self.default_output_dir = self.output_dir_base / self.project_id / "cloud-monitoring-charts"
        print(f"Default output directory base set to: {self.default_output_dir}")
        print("Initializing Google Cloud clients...")
        try:
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.run_client = run_v2.ServicesClient()
            print("Google Cloud clients initialized successfully.")
        except Exception as e:
            print(f"🛑 Error initializing Google Cloud clients: {e}")
            raise ConnectionError(f"Failed to initialize Google Cloud clients: {e}") from e

    # --- Private Helper Methods ---
    # _get_cloud_run_config, _fetch_time_series, _plot_instance_chart, _plot_requests_vs_latency_chart
    # (Keep these exactly as they were in the previous version with corrected keywords)
    def _get_cloud_run_config(self, location: str, service_name: str) -> tuple[int, int]:
        """Fetches the Min/Max instance configuration for a Cloud Run service."""
        logger.info(f"Fetching Cloud Run service config for: {service_name} in {location}...")
        min_instances, max_instances = 0, 100
        try:
            service_full_name = f"projects/{self.project_id}/locations/{location}/services/{service_name}"
            service_info = self.run_client.get_service(name=service_full_name)
            min_instances = service_info.template.scaling.min_instance_count
            max_instances = service_info.template.scaling.max_instance_count
            print(f"  - Found Min Instances: {min_instances}, Max Instances: {max_instances}")
        except Exception as e: print(f"⚠️ Error fetching service config: {e}.")
        return min_instances, max_instances

    def _get_cache_dir(self, service_name: str, project_id: Optional[str]= None): # ,location: Optional[str],
        '''Gives a CloudRun-specific monitoring subfolder.
        This is BUGGY since some is cloud runny, some instead is GCE-ey.

        Note this is currently not used. It was arated when Gemini produced yet another magic table.

        TODO(ricc): restore its glory

        Note: Location/region is for now useless for now, given the regional-averse nature of CRun.
        '''
        #if project_id is None:
        project_id = project_id or self.project_id
        print(f"🫣 _get_cache_dir(project_id={project_id}, service_name={service_name})")
        return Path('.cache') /  project_id / 'cloud-run' / service_name / 'ricc_mon'


    def _fetch_time_series(self, filter_str: str, metric_type: str,
                           aggregation: monitoring_v3.Aggregation,
                           start_time: datetime.datetime, end_time: datetime.datetime) -> tuple[list, list]:
        """Fetches time series data from Cloud Monitoring."""
        logger.warn(f"_fetch_time_series(): Fetching metric: {C.cyan(metric_type)}...")
        project_name = f"projects/{self.project_id}"
        start_timestamp = Timestamp(); start_timestamp.FromDatetime(start_time)
        end_timestamp = Timestamp(); end_timestamp.FromDatetime(end_time)
        request = {"name": project_name, "filter": filter_str, "interval": monitoring_v3.TimeInterval(start_time=start_timestamp, end_time=end_timestamp), "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL, "aggregation": aggregation}
        results = self.monitoring_client.list_time_series(request=request)
        timestamps, values = [], []; found_data = False
        for result in results:
            points = result.points; point_timestamps, point_values = [], []
            for p in points:
                dt = p.interval.end_time
                try:
                    if isinstance(dt, datetime.datetime):
                        if dt.tzinfo is None: dt = dt.replace(tzinfo=pytz.utc)
                    else: dt = dt.ToDatetime().replace(tzinfo=pytz.utc)
                except Exception as time_e: print(f"Warning: Could not process timestamp {p.interval.end_time}: {time_e}"); continue
                point_timestamps.append(dt)
                value = None; val_obj = p.value; agg_aligner = aggregation.per_series_aligner if aggregation else None
                if val_obj.double_value is not None:
                    value = val_obj.double_value
                    if value == 0.0 and agg_aligner not in [monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95, monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_50, monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_05, monitoring_v3.Aggregation.Aligner.ALIGN_MEAN, monitoring_v3.Aggregation.Aligner.ALIGN_RATE]: value = None
                if value is None and val_obj.int64_value is not None:
                    value = val_obj.int64_value
                    if value == 0 and agg_aligner not in [monitoring_v3.Aggregation.Aligner.ALIGN_SUM, monitoring_v3.Aggregation.Aligner.ALIGN_COUNT, monitoring_v3.Aggregation.Aligner.ALIGN_COUNT_TRUE, monitoring_v3.Aggregation.Aligner.ALIGN_COUNT_FALSE]: value = None
                if value is None and val_obj.bool_value is not None: value = val_obj.bool_value
                if value is None and val_obj.string_value is not None and val_obj.string_value != "": value = val_obj.string_value
                if value is None and val_obj.distribution_value is not None: dist = val_obj.distribution_value; print(f"Warning: Distribution value found for {metric_type}. Falling back to mean."); value = dist.mean if dist.count > 0 else 0
                if value is not None: point_values.append(value)
                else: point_values.append(None)
            timestamps = point_timestamps[::-1]; values = point_values[::-1]; found_data = True; break
        if not found_data: print(f"⚠️ No data found for metric: {metric_type}")
        return timestamps, values

    def _plot_instance_chart(self, timestamps, values, min_instances, max_instances, service_name, hours_back, output_filename):
        """Generates and saves the Cloud Run instance count chart using a step plot.
        """
        print("Generating Plot 1: Instances (Step Plot)...")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.step(timestamps, values, where='pre', label='Effective Instances', color='blue')
        ax.axhline(y=min_instances, color='green', linestyle='--', label=f'Min Instances ({min_instances})')
        if max_instances > 0: ax.axhline(y=max_instances, color='red', linestyle='--', label=f'Max Instances ({max_instances})')
        ax.set_xlabel("Time (UTC)"); ax.set_ylabel("Container Instances"); ax.set_title(f"Cloud Run Instances: {service_name}\nLast {hours_back} Hours")
        ax.legend(); ax.grid(True)
        if values and any(v is not None for v in values): data_max = max(v for v in values if v is not None); plot_max_y = max(data_max, max_instances if max_instances > 0 else data_max); ax.set_ylim(bottom=-0.5, top=plot_max_y * 1.1 + 1)
        else: ax.set_ylim(bottom=-0.5, top=max(1, max_instances * 1.1))
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=pytz.utc); formatter = mdates.ConciseDateFormatter(locator, tz=pytz.utc)
        ax.xaxis.set_major_locator(locator); ax.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate(); plt.tight_layout(); plt.savefig(output_filename); print(f"✅ Chart 1 saved to {output_filename}"); plt.close(fig)
        return {
            'chart_filename': str(output_filename),
            'summary': f"Chart generated for service '{service_name}' showing effective instances for the last {hours_back} hours.",
            'metrics_data': {
                'effective_instances': [
                    {'timestamp': ts.isoformat(), 'value': val}
                    for ts, val in zip(timestamps, values)
                    if val is not None
                ]},
        }

# In class RiccCloudMonitoring:

    # (Keep _get_cloud_run_config, _fetch_time_series, _plot_instance_chart as before)



    # Assuming this function is part of a class, hence the 'self' parameter
    def _plot_requests_vs_latency_chart(
        self, # Keep 'self' if it's a method within a class
        req_ts: List[datetime.datetime],
        req_vals: List[Optional[float]],
        lat_ts: List[datetime.datetime],
        lat_vals: List[Optional[float]],
        percentile: float,
        service_name: str,
        investigation_date: Optional[datetime.date] = None, # New parameter
        hours_back: int = DEFAULT_HOURS_BACK_GLOBAL,
        output_filename: Union[str, Path] = "traffic_vs_latency_chart_ng.png" # Added default filename with date
    ) -> Dict[str, Any]: # Changed return type hint for flexibility
        """
        Generates and saves the traffic vs. latency chart using step plots for a specific period.

        Args:
            req_ts: List of timestamps for request rate data. Assumed to be timezone-aware (e.g., UTC).
            req_vals: List of request rate values (requests/second). Can contain None.
            lat_ts: List of timestamps for latency data. Assumed to be timezone-aware (e.g., UTC).
            lat_vals: List of latency values (ms). Can contain None.
            percentile: The latency percentile (e.g., 95, 99).
            service_name: The name of the Cloud Run service.
            investigation_date: The end date for the monitoring period. Defaults to today.
                                The time window will be `hours_back` ending on this date.
            hours_back: The duration of the monitoring window in hours, ending at `investigation_date`.
            output_filename: The path (string or Path object) where the chart image will be saved.

        Returns:
            dict: A dictionary containing the chart filename, structured time series data,
                and a summary of the chart's scope. Returns None for filename if no data.
                Example:
                {
                    "chart_filename": "/path/to/chart.png",
                    "metrics_data": {
                        "request_rate_per_second": [
                            {"timestamp": "2023-10-27T10:00:00+00:00", "value": 15.5}, ...
                        ],
                        "latency_p95_ms": [
                            {"timestamp": "2023-10-27T10:00:00+00:00", "value": 120.0}, ...
                        ]
                    },
                    "summary": "Chart generated for service 'X' showing request rate and P95 latency for 24 hours ending on 2025-04-14."
                }
        """
        # --- Handle investigation_date ---
        if investigation_date is None:
            investigation_date = datetime.date.today()
            print(f"🕵️‍♀️ Investigation date not specified, defaulting to today: {investigation_date.isoformat()}")
        else:
            # Ensure investigation_date is a date object if a datetime object was passed
            if isinstance(investigation_date, datetime.datetime):
                investigation_date = investigation_date.date()
            print(f"🕵️‍♀️ Investigation date set to: {investigation_date.isoformat()}")

        # Define the conceptual end time based on investigation_date
        # Note: The *actual* data range depends on what was fetched and passed in req_ts/lat_ts.
        # This date is mainly for title/summary context. We assume input ts are UTC.
        print(f"📊 Generating Plot: Traffic vs Latency for '{service_name}' ({hours_back}h ending {investigation_date.isoformat()})...")
        fig, ax_traffic = plt.subplots(figsize=(12, 6))
        color_traffic = 'tab:blue'
        ax_traffic.set_xlabel("Time (UTC)") # Label axis clearly
        ax_traffic.set_ylabel("Requests / Second", color=color_traffic)

        # Filter None values for plotting AND data export
        # Ensure timestamps are timezone-aware (UTC assumed) for correct plotting
        valid_req_ts = [t for i, t in enumerate(req_ts) if req_vals[i] is not None and t]
        valid_req_vals = [v for i, v in enumerate(req_vals) if v is not None and req_ts[i]]
        valid_lat_ts = [t for i, t in enumerate(lat_ts) if lat_vals[i] is not None and t]
        valid_lat_vals = [v for i, v in enumerate(lat_vals) if v is not None and lat_ts[i]]

        # Check if we have any valid data points to plot
        if not valid_req_ts and not valid_lat_ts:
            print(f"⚠️ No valid data points found for service '{service_name}' in the provided timeseries. Skipping plot generation.")
            plt.close(fig)
            latency_key = f"latency_p{int(percentile)}_ms"
            return {
                "chart_filename": None, # Indicate no chart was generated
                "metrics_data": {"request_rate_per_second": [], latency_key: []},
                "summary": f"No data to generate chart for service '{service_name}' for {hours_back} hours ending on {investigation_date.isoformat()}."
            }

        # Plotting using valid data
        if valid_req_ts:
            ax_traffic.step(valid_req_ts, valid_req_vals, where='pre', color=color_traffic, label='Request Rate')
        ax_traffic.tick_params(axis='y', labelcolor=color_traffic)
        ax_traffic.grid(True, axis='y', linestyle=':', color=color_traffic, alpha=0.5)
        ax_traffic.set_ylim(bottom=0) # Start y-axis at 0

        ax_latency = ax_traffic.twinx() # Share the same x-axis
        color_latency = 'tab:red'
        ax_latency.set_ylabel(f"P{int(percentile)} Latency (ms)", color=color_latency)

        if valid_lat_ts:
            ax_latency.step(valid_lat_ts, valid_lat_vals, where='pre', color=color_latency, label=f'P{int(percentile)} Latency')
        ax_latency.tick_params(axis='y', labelcolor=color_latency)
        ax_latency.set_ylim(bottom=0) # Start y-axis at 0

        # Combine legends from both axes
        lines, labels = ax_traffic.get_legend_handles_labels()
        lines2, labels2 = ax_latency.get_legend_handles_labels()
        if lines or lines2: # Only show legend if there's something to label
            ax_latency.legend(lines + lines2, labels + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False) # Adjusted bbox slightly

        # --- Title reflecting the new parameter ---
        title = (f"Cloud Run: {service_name}\n"
                f"Request Rate vs. P{int(percentile)} Latency\n"
                f"{hours_back} Hours Ending {investigation_date.isoformat()}")
        ax_traffic.set_title(title)

        # --- X-axis formatting (assuming UTC) ---
        # Use UTC timezone for formatting x-axis labels
        utc_tz = pytz.utc
        locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=utc_tz)
        formatter = mdates.ConciseDateFormatter(locator, tz=utc_tz)
        formatter.formats = ['%Y', '%b', '%d', '%H:%M', '%H:%M', '%S.%f'] # Default formats
        formatter.offset_formats = ['', '%Y', '%b %Y', '%d %b %Y', '%d %b %Y', '%d %b %Y %H:%M'] # Default offset formats
        formatter.zero_formats = [''] + formatter.formats[:-1] # Use clarity for zero values
        formatter.show_offset = True # Show offset (like date) when needed

        ax_traffic.xaxis.set_major_locator(locator)
        ax_traffic.xaxis.set_major_formatter(formatter)

        # Adjust layout and save
        fig.autofmt_xdate() # Rotate date labels nicely
        plt.tight_layout(rect=[0, 0.05, 1, 0.95]) # Adjust rect to prevent title/legend overlap

        output_filepath = Path(output_filename) # Ensure it's a Path object
        try:
            output_filepath.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
            plt.savefig(output_filepath)
            print(f"✅ Chart saved to {output_filepath}")
            saved_filename = str(output_filepath)
        except Exception as e:
            print(f"❌ Error saving chart to {output_filepath}: {e}")
            saved_filename = None # Indicate error saving file

        plt.close(fig) # Close the figure to free memory

        # --- Prepare Data for Return ---
        # Convert valid timestamps to ISO 8601 format strings (ensure they are UTC)
        request_rate_data = [
            {"timestamp": ts.isoformat(), "value": round(val, 3) if val is not None else None} # Round for cleaner output
            for ts, val in zip(valid_req_ts, valid_req_vals)
        ]
        latency_data = [
            {"timestamp": ts.isoformat(), "value": round(val, 3) if val is not None else None} # Round for cleaner output
            for ts, val in zip(valid_lat_ts, valid_lat_vals)
        ]

        # Structure the return dictionary
        latency_key = f"latency_p{int(percentile)}_ms" # Dynamic key based on percentile
        summary_text = (f"Chart generated for service '{service_name}' showing request rate "
                        f"and P{int(percentile)} latency for the {hours_back} hours "
                        f"ending on {investigation_date.isoformat()}.")
        return_data = {
            "chart_filename": saved_filename, # Use the actual saved path or None
            "metrics_data": {
                "request_rate_per_second": request_rate_data,
                latency_key: latency_data
            },
            "summary": summary_text
        }

        print(f"📈 Data prepared: {len(request_rate_data)} req points, {len(latency_data)} lat points.")
        return return_data

    # def _plot_requests_vs_latency_chart_VECCHIO(self, req_ts, req_vals, lat_ts, lat_vals, percentile, service_name, hours_back: int, output_filename):
    #     """
    #     Generates and saves the traffic vs. latency chart using step plots.

    #     Returns:
    #         dict: A dictionary containing the chart filename and structured time series data.
    #               Example:
    #               {
    #                   "chart_filename": "/path/to/chart.png",
    #                   "metrics_data": {
    #                       "request_rate_per_second": [
    #                           {"timestamp": "2023-10-27T10:00:00Z", "value": 15.5}, ...
    #                       ],
    #                       "latency_p95_ms": [
    #                           {"timestamp": "2023-10-27T10:00:00Z", "value": 120.0}, ...
    #                       ]
    #                   },
    #                   "summary": "Chart for service 'X' showing request rate and P95 latency for last 24 hours."
    #               }
    #     """
    #     print("Generating Plot 2: Traffic vs Latency (Step Plot)...")
    #     fig, ax_traffic = plt.subplots(figsize=(12, 6)); color_traffic = 'tab:blue'; ax_traffic.set_xlabel("Time (UTC)")
    #     ax_traffic.set_ylabel("Requests / Second", color=color_traffic)
    #     # Filter None values for plotting AND data export
    #     valid_req_vals = [v for v in req_vals if v is not None]
    #     valid_req_ts = [t for i, t in enumerate(req_ts) if req_vals[i] is not None]
    #     valid_lat_vals = [v for v in lat_vals if v is not None]
    #     valid_lat_ts = [t for i, t in enumerate(lat_ts) if lat_vals[i] is not None]

    #     # Plotting using valid data
    #     ax_traffic.step(valid_req_ts, valid_req_vals, where='pre', color=color_traffic, label='Request Rate')
    #     ax_traffic.tick_params(axis='y', labelcolor=color_traffic); ax_traffic.grid(True, axis='y', linestyle=':', color=color_traffic, alpha=0.5); ax_traffic.set_ylim(bottom=0)
    #     ax_latency = ax_traffic.twinx(); color_latency = 'tab:red'; ax_latency.set_ylabel(f"P{int(percentile)} Latency (ms)", color=color_latency)
    #     ax_latency.step(valid_lat_ts, valid_lat_vals, where='pre', color=color_latency, label=f'P{int(percentile)} Latency'); ax_latency.tick_params(axis='y', labelcolor=color_latency); ax_latency.set_ylim(bottom=0)
    #     lines, labels = ax_traffic.get_legend_handles_labels(); lines2, labels2 = ax_latency.get_legend_handles_labels()
    #     ax_latency.legend(lines + lines2, labels + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2); ax_traffic.set_title(f"Cloud Run Traffic vs. Latency: {service_name}\nLast {hours_back} Hours")
    #     locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=pytz.utc); formatter = mdates.ConciseDateFormatter(locator, tz=pytz.utc)
    #     ax_traffic.xaxis.set_major_locator(locator); ax_traffic.xaxis.set_major_formatter(formatter)
    #     fig.autofmt_xdate(); plt.tight_layout(rect=[0, 0.05, 1, 1]);

    #     # Save the chart
    #     plt.savefig(output_filename);
    #     print(f"✅ Chart 2 saved to {output_filename}");
    #     plt.close(fig)

    #     # --- Prepare Data for Return ---
    #     # Convert timestamps to ISO 8601 format strings
    #     request_rate_data = [
    #         {"timestamp": ts.isoformat(), "value": val}
    #         for ts, val in zip(valid_req_ts, valid_req_vals) # Use already filtered lists
    #     ]
    #     latency_data = [
    #         {"timestamp": ts.isoformat(), "value": val}
    #         for ts, val in zip(valid_lat_ts, valid_lat_vals) # Use already filtered lists
    #     ]

    #     # Structure the return dictionary
    #     latency_key = f"latency_p{int(percentile)}_ms" # Dynamic key based on percentile
    #     return_data = {
    #         "chart_filename": str(output_filename), # Ensure Path is converted to string
    #         "metrics_data": {
    #             "request_rate_per_second": request_rate_data,
    #             latency_key: latency_data
    #         },
    #         "summary": f"Chart generated for service '{service_name}' showing request rate and P{int(percentile)} latency for the last {hours_back} hours."
    #     }

    #     print(f"Data prepared for return: {len(request_rate_data)} request points, {len(latency_data)} latency points.")
    #     return return_data

    # (Other methods like _plot_instance_chart, generate_... etc. remain as before for now)
    # --- Public Methods ---

    def generate_cloud_run_instance_chart(self,
                                          service_name: Optional[str] = None,
                                          location: Optional[str] = None,
                                          hours_back: Optional[float] = None,
                                          output_dir: Optional[Union[str, Path]] = None):
        '''Generates a Cloud Run instance Chart.

        Arguments:
            service_name: The Cloud Run Service name.
            location: The GCP Region where the service runs.
        '''
        # (Implementation remains the same as previous version with corrected keywords)
        loc = location or self.default_region; srv_name = service_name or self.default_cloud_run_service
        hrs_back = hours_back if hours_back is not None else self.default_hours_back
        out_dir = Path(output_dir) if output_dir else (self.default_output_dir / "cloud-run" / (srv_name or "default_service"))
        if not loc: raise ValueError("Region/Location required.");
        if not srv_name: raise ValueError("Cloud Run Service name required.")
        print(f"\n--- Generating Cloud Run Instance Chart for {srv_name} in {loc} ---"); out_dir.mkdir(parents=True, exist_ok=True)
        min_instances, max_instances = self._get_cloud_run_config(loc, srv_name)
        end_time = datetime.datetime.now(pytz.utc); start_time = end_time - datetime.timedelta(hours=hrs_back)
        base_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{srv_name}" AND resource.labels.location="{loc}"'
        instance_metric = "run.googleapis.com/container/instance_count"
        instance_aggregation = monitoring_v3.Aggregation(
            alignment_period={"seconds": DEFAULT_ALIGNMENT_SECONDS}, # Use default alignment here
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            group_by_fields=["resource.label.\"revision_name\""]
        )
        instance_timestamps, instance_values = self._fetch_time_series(base_filter + f' AND metric.type="{instance_metric}"', instance_metric, instance_aggregation, start_time, end_time)
        if instance_timestamps:
            filename = out_dir / f"{srv_name}_instances_{hrs_back}h.png"
            structrued_ret = self._plot_instance_chart(instance_timestamps, instance_values, min_instances, max_instances, srv_name, hrs_back, filename)
            return structrued_ret
        else:
            print("Skipping instance chart: missing data.")
            return {'error': "Skipping instance chart: missing data." }


    def generate_cloud_run_requests_vs_latency_chart(self,
                                                 service_name: Optional[str] = None,
                                                 location: Optional[str] = None,
                                                 hours_back: Optional[float] = None,
                                                 output_dir: Optional[Union[str, Path]] = None,
                                                 latency_percentile: float = LATENCY_PERCENTILE_DEFAULT):
        # (Implementation remains the same as previous version with corrected keywords)
        loc = location or self.default_region; srv_name = service_name or self.default_cloud_run_service
        hrs_back = hours_back if hours_back is not None else self.default_hours_back
        out_dir = Path(output_dir) if output_dir else (self.default_output_dir / "cloud-run" / (srv_name or "default_service"))
        if not loc: raise ValueError("Region/Location required.");
        if not srv_name: raise ValueError("Cloud Run Service name required.")
        print(f"\n--- Generating Cloud Run Traffic/Latency Chart for {srv_name} in {loc} ---"); out_dir.mkdir(parents=True, exist_ok=True)
        end_time = datetime.datetime.now(pytz.utc); start_time = end_time - datetime.timedelta(hours=hrs_back)
        base_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{srv_name}" AND resource.labels.location="{loc}"'
        req_count_metric = "run.googleapis.com/request_count"
        req_rate_aggregation = monitoring_v3.Aggregation(alignment_period={"seconds": DEFAULT_ALIGNMENT_SECONDS}, per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE, cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_SUM, group_by_fields=["resource.label.\"revision_name\""])
        if int(latency_percentile) == 99: latency_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_99
        elif int(latency_percentile) == 95: latency_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95
        elif int(latency_percentile) == 50: latency_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_50
        else: print(f"Warning: Unsupported percentile {latency_percentile}. Defaulting P95."); latency_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95; latency_percentile = 95.0
        latency_metric = "run.googleapis.com/request_latencies"
        latency_aggregation = monitoring_v3.Aggregation(alignment_period={"seconds": DEFAULT_ALIGNMENT_SECONDS}, per_series_aligner=latency_aligner, cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_SUM, group_by_fields=["resource.label.\"revision_name\""])
        req_timestamps, req_values = self._fetch_time_series(base_filter + f' AND metric.type="{req_count_metric}"', req_count_metric, req_rate_aggregation, start_time, end_time)
        latency_timestamps, latency_values_ms = self._fetch_time_series(base_filter + f' AND metric.type="{latency_metric}"', latency_metric, latency_aggregation, start_time, end_time)
        latency_values_ms_filtered = [v for v in latency_values_ms if v is not None]; latency_timestamps_filtered = [t for i, t in enumerate(latency_timestamps) if latency_values_ms[i] is not None]
        if req_timestamps and latency_timestamps_filtered:
             filename = out_dir / f"{srv_name}_requests_vs_latency_{hrs_back}h_p{int(latency_percentile)}.png"
             structured_ret = self._plot_requests_vs_latency_chart(req_timestamps, req_values, latency_timestamps_filtered, latency_values_ms_filtered, latency_percentile, srv_name, hrs_back, filename)
             return structured_ret
        else: print("Skipping traffic/latency chart: missing data.")
        return {'error': 'missing data from generate_cloud_run_requests_vs_latency_chart()' }


# In class RiccCloudMonitoring:

    # ... (other methods remain the same) ...

    def generate_cloud_run_network_chart(self,
                                         service_name: Optional[str] = None,
                                         location: Optional[str] = None,
                                         hours_back: Optional[float] = None,
                                         output_dir: Optional[Union[str, Path]] = None):
        """
        Generates and saves a chart showing Cloud Run network Ingress vs. Egress traffic rate.
        Uses a shorter alignment period (NETWORK_ALIGNMENT_SECONDS) for more granular results.

        Returns:
            dict or None: A dictionary containing the chart filename and structured time series data,
                          or None if no data was found to plot.
                          Example:
                          {
                              "chart_filename": "/path/to/chart.png",
                              "metrics_data": {
                                  "network_ingress_bytes_per_second": [
                                      {"timestamp": "2023-10-27T10:00:00Z", "value": 500.0}, ...
                                  ],
                                  "network_egress_bytes_per_second": [
                                      {"timestamp": "2023-10-27T10:00:00Z", "value": 8500.0}, ...
                                  ]
                              },
                              "summary": "Chart for service 'X' showing network ingress/egress rate for last Y hours."
                          }
        """
        # Remove the placeholder ret = {'todo': 'implement me later'}
        loc = location or self.default_region
        srv_name = service_name or self.default_cloud_run_service
        hrs_back = hours_back if hours_back is not None else self.default_hours_back
        out_dir = Path(output_dir) if output_dir else (self.default_output_dir / "cloud-run" / (srv_name or "default_service"))
        if not loc: raise ValueError("Region/Location required.")
        if not srv_name: raise ValueError("Cloud Run Service name required.")
        print(f"\n--- Generating Cloud Run Network Traffic Chart for {srv_name} in {loc} ---")
        out_dir.mkdir(parents=True, exist_ok=True)
        end_time = datetime.datetime.now(pytz.utc); start_time = end_time - datetime.timedelta(hours=hrs_back)
        base_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{srv_name}" AND resource.labels.location="{loc}"'

        network_rate_aggregation = monitoring_v3.Aggregation(
            alignment_period={"seconds": NETWORK_ALIGNMENT_SECONDS}, # Use shorter period
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
            cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            group_by_fields=["resource.label.\"revision_name\""]
        )
        ingress_metric = 'run.googleapis.com/container/network/received_bytes_count'
        egress_metric = 'run.googleapis.com/container/network/sent_bytes_count'

        ingress_ts, ingress_vals = self._fetch_time_series(base_filter + f' AND metric.type="{ingress_metric}"', ingress_metric, network_rate_aggregation, start_time, end_time)
        egress_ts, egress_vals = self._fetch_time_series(base_filter + f' AND metric.type="{egress_metric}"', egress_metric, network_rate_aggregation, start_time, end_time)

        # Initialize return data in case plotting is skipped
        return_data = None
        filename = None # Initialize filename

        if ingress_ts or egress_ts:
            filename = out_dir / f"{srv_name}_network_traffic_{hrs_back}h.png"
            print(f"Generating plot: {filename}...")
            fig, ax = plt.subplots(figsize=(12, 6))

            # Filter None values for plotting AND data export
            valid_ingress_vals = [v for v in ingress_vals if v is not None]
            valid_ingress_ts = [t for i, t in enumerate(ingress_ts) if ingress_vals[i] is not None]
            valid_egress_vals = [v for v in egress_vals if v is not None]
            valid_egress_ts = [t for i, t in enumerate(egress_ts) if egress_vals[i] is not None]

            # --- Plotting ---
            if valid_ingress_ts: ax.step(valid_ingress_ts, valid_ingress_vals, where='pre', label='Ingress (Received)', color='blue')
            if valid_egress_ts: ax.step(valid_egress_ts, valid_egress_vals, where='pre', label='Egress (Sent)', color='red')
            ax.set_xlabel("Time (UTC)"); ax.set_ylabel("Bytes / Second"); ax.set_title(f"Cloud Run Network Traffic Rate: {srv_name}\nLast {hrs_back} Hours (1 min alignment)")
            ax.legend(); ax.grid(True); ax.set_ylim(bottom=0)
            locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=pytz.utc); formatter = mdates.ConciseDateFormatter(locator, tz=pytz.utc)
            ax.xaxis.set_major_locator(locator); ax.xaxis.set_major_formatter(formatter)
            fig.autofmt_xdate(); plt.tight_layout();

            # --- Save Plot ---
            plt.savefig(filename); print(f"✅ Network chart saved to {filename}"); plt.close(fig)

            # --- Prepare Data for Return ---
            ingress_data = [
                {"timestamp": ts.isoformat(), "value": val}
                for ts, val in zip(valid_ingress_ts, valid_ingress_vals)
            ]
            egress_data = [
                {"timestamp": ts.isoformat(), "value": val}
                for ts, val in zip(valid_egress_ts, valid_egress_vals)
            ]

            # --- Structure the return dictionary ---
            return_data = {
                "chart_filename": str(filename), # Ensure Path is converted to string
                "metrics_data": {
                    "network_ingress_bytes_per_second": ingress_data,
                    "network_egress_bytes_per_second": egress_data
                },
                "summary": f"Chart generated for service '{srv_name}' showing network ingress and egress rate (Bytes/Second) for the last {hrs_back} hours."
            }
            print(f"Data prepared for return: {len(ingress_data)} ingress points, {len(egress_data)} egress points.")

        else:
            print("Skipping network traffic chart generation due to missing data for both ingress and egress.")

        # Return the dictionary (or None if plotting was skipped)
        return return_data




    # --- NEW METHOD: Cloud Run CPU & Memory Utilization Chart ---
    def generate_cloud_run_cpu_memory_chart(self,
                                            service_name: Optional[str] = None,
                                            location: Optional[str] = None,
                                            hours_back: Optional[float] = None,
                                            percentile: float = 95.0, # Default to P95
                                            output_dir: Optional[Union[str, Path]] = None):
        """
        Generates a chart showing Cloud Run PXX CPU and Memory utilization percentage.

        Uses a shorter alignment period (NETWORK_ALIGNMENT_SECONDS) for more granular results.

        Args:
            service_name: Cloud Run service name. Uses instance default if None.
            location: Cloud Run service region. Uses instance default if None.
            hours_back: How many hours back from now to fetch data for. Uses instance default if None.
            percentile: The percentile to use for aggregation (e.g., 95, 99). Defaults to 95.
            output_dir: Directory to save the chart image. Uses instance default structure if None.

        Returns:
            dict or None: A dictionary containing the chart filename and structured time series data,
                          or None if no data was found to plot.
        """
        loc = location or self.default_region
        srv_name = service_name or self.default_cloud_run_service
        hrs_back = hours_back if hours_back is not None else self.default_hours_back
        out_dir = Path(output_dir) if output_dir else (self.default_output_dir / "cloud-run" / (srv_name or "default_service"))

        if not loc: raise ValueError("Region/Location required.")
        if not srv_name: raise ValueError("Cloud Run Service name required.")

        print(f"\n--- Generating Cloud Run CPU/Memory P{int(percentile)} Chart for {srv_name} in {loc} ---")
        out_dir.mkdir(parents=True, exist_ok=True)

        end_time = datetime.datetime.now(pytz.utc)
        start_time = end_time - datetime.timedelta(hours=hrs_back)
        base_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{srv_name}" AND resource.labels.location="{loc}"'

        # Determine Aligner and Reducer based on percentile for Pxx view
        # Note: Reducer PXX might not be directly available, using MAX as a common fallback for peak usage across series
        if int(percentile) == 99:
            util_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_99
            util_reducer = monitoring_v3.Aggregation.Reducer.REDUCE_PERCENTILE_99 # Or REDUCE_MAX
        elif int(percentile) == 95:
            util_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95
            util_reducer = monitoring_v3.Aggregation.Reducer.REDUCE_PERCENTILE_95 # Or REDUCE_MAX
        elif int(percentile) == 50:
            util_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_50
            util_reducer = monitoring_v3.Aggregation.Reducer.REDUCE_PERCENTILE_50 # Or REDUCE_MEAN
        else:
            print(f"Warning: Unsupported utilization percentile {percentile}. Defaulting to P95.")
            util_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95
            util_reducer = monitoring_v3.Aggregation.Reducer.REDUCE_PERCENTILE_95
            percentile = 95.0

        # Define aggregation using short alignment period and percentile aligner/reducer
        util_aggregation = monitoring_v3.Aggregation(
            alignment_period={"seconds": NETWORK_ALIGNMENT_SECONDS}, # Use shorter period for spikiness
            per_series_aligner=util_aligner,
            cross_series_reducer=util_reducer, # Show peak usage across instances
            group_by_fields=["resource.label.\"revision_name\""] # Can remove group_by if reducing fully
        )

        # Define Metrics
        cpu_metric = 'run.googleapis.com/container/cpu/utilizations'
        memory_metric = 'run.googleapis.com/container/memory/utilizations'

        # Fetch Data
        cpu_ts, cpu_vals_ratio = self._fetch_time_series(base_filter + f' AND metric.type="{cpu_metric}"', cpu_metric, util_aggregation, start_time, end_time)
        mem_ts, mem_vals_ratio = self._fetch_time_series(base_filter + f' AND metric.type="{memory_metric}"', memory_metric, util_aggregation, start_time, end_time)

        # Initialize return data
        return_data = None
        filename = None

        # Plotting (only if we have data for at least one)
        if cpu_ts or mem_ts:
            filename = out_dir / f"{srv_name}_cpu_memory_p{int(percentile)}_{hrs_back}h.png"
            print(f"Generating plot: {filename}...")
            fig, ax = plt.subplots(figsize=(12, 6))

            # Filter None values and convert ratios (0-1) to percentages (0-100)
            cpu_vals_percent = [(v * 100) for v in cpu_vals_ratio if v is not None]
            valid_cpu_ts = [t for i, t in enumerate(cpu_ts) if cpu_vals_ratio[i] is not None]
            mem_vals_percent = [(v * 100) for v in mem_vals_ratio if v is not None]
            valid_mem_ts = [t for i, t in enumerate(mem_ts) if mem_vals_ratio[i] is not None]

            # --- Plotting ---
            if valid_cpu_ts: ax.step(valid_cpu_ts, cpu_vals_percent, where='pre', label=f'CPU Utilization % (P{int(percentile)})', color='blue')
            if valid_mem_ts: ax.step(valid_mem_ts, mem_vals_percent, where='pre', label=f'Memory Utilization % (P{int(percentile)})', color='green')

            # Formatting
            ax.set_xlabel("Time (UTC)")
            ax.set_ylabel(f"Utilization % (P{int(percentile)})")
            ax.set_title(f"Cloud Run CPU & Memory Utilization: {srv_name}\nLast {hrs_back} Hours (P{int(percentile)}, 1 min alignment)")
            ax.legend(); ax.grid(True); ax.set_ylim(bottom=-5, top=105) # Percentage axis 0-100

            # Apply Concise Date Formatting
            locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=pytz.utc)
            formatter = mdates.ConciseDateFormatter(locator, tz=pytz.utc)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)

            fig.autofmt_xdate(); plt.tight_layout()

            # --- Save Plot ---
            plt.savefig(filename); print(f"✅ CPU/Memory chart saved to {filename}"); plt.close(fig)

            # --- Prepare Data for Return ---
            cpu_data = [
                {"timestamp": ts.isoformat(), "value": val} # Use percentage value
                for ts, val in zip(valid_cpu_ts, cpu_vals_percent)
            ]
            memory_data = [
                {"timestamp": ts.isoformat(), "value": val} # Use percentage value
                for ts, val in zip(valid_mem_ts, mem_vals_percent)
            ]

            # --- Structure the return dictionary ---
            cpu_key = f"cpu_utilization_percent_p{int(percentile)}"
            mem_key = f"memory_utilization_percent_p{int(percentile)}"
            return_data = {
                "chart_filename": str(filename),
                "metrics_data": {
                    cpu_key: cpu_data,
                    mem_key: memory_data
                },
                "summary": f"Chart generated for service '{srv_name}' showing P{int(percentile)} CPU and Memory utilization percentage for the last {hrs_back} hours (1 min alignment)."
            }
            print(f"Data prepared for return: {len(cpu_data)} CPU points, {len(memory_data)} Memory points.")

        else:
            print("Skipping CPU/Memory chart generation due to missing data.")

        return return_data


    # ... existing generate_generic_metric_chart method ...

# --- End of Class Definition ---



    # --- UPDATED METHOD ---
    def generate_cloud_run_network_chart_vecchio_removeme(self,
                                         service_name: Optional[str] = None,
                                         location: Optional[str] = None,
                                         hours_back: Optional[float] = None,
                                         output_dir: Optional[Union[str, Path]] = None):
        """
        Generates and saves a chart showing Cloud Run network Ingress vs. Egress traffic rate.
        Uses a shorter alignment period (NETWORK_ALIGNMENT_SECONDS) for more granular ("spiky") results.
        """
        ret = {}
        ret['todo': 'implement me later']
        loc = location or self.default_region
        srv_name = service_name or self.default_cloud_run_service
        hrs_back = hours_back if hours_back is not None else self.default_hours_back
        out_dir = Path(output_dir) if output_dir else (self.default_output_dir / "cloud-run" / (srv_name or "default_service"))
        if not loc: raise ValueError("Region/Location required.")
        if not srv_name: raise ValueError("Cloud Run Service name required.")
        print(f"\n--- Generating Cloud Run Network Traffic Chart for {srv_name} in {loc} ---")
        out_dir.mkdir(parents=True, exist_ok=True)
        end_time = datetime.datetime.now(pytz.utc); start_time = end_time - datetime.timedelta(hours=hrs_back)
        base_filter = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{srv_name}" AND resource.labels.location="{loc}"'

        # --- Define aggregation with SHORTER alignment period ---
        network_rate_aggregation = monitoring_v3.Aggregation(
            alignment_period={"seconds": NETWORK_ALIGNMENT_SECONDS}, # Use shorter period
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
            cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            group_by_fields=["resource.label.\"revision_name\""]
        )

        # --- Use CORRECTED Metric Names ---
        ingress_metric = 'run.googleapis.com/container/network/received_bytes_count'
        egress_metric = 'run.googleapis.com/container/network/sent_bytes_count'
        # --- End Correction ---

        ingress_ts, ingress_vals = self._fetch_time_series(base_filter + f' AND metric.type="{ingress_metric}"', ingress_metric, network_rate_aggregation, start_time, end_time)
        egress_ts, egress_vals = self._fetch_time_series(base_filter + f' AND metric.type="{egress_metric}"', egress_metric, network_rate_aggregation, start_time, end_time)

        if ingress_ts or egress_ts:
            filename = out_dir / f"{srv_name}_network_traffic_{hrs_back}h.png"
            print(f"Generating plot: {filename}...")
            fig, ax = plt.subplots(figsize=(12, 6))
            valid_ingress_vals = [v for v in ingress_vals if v is not None]; valid_ingress_ts = [t for i, t in enumerate(ingress_ts) if ingress_vals[i] is not None]
            valid_egress_vals = [v for v in egress_vals if v is not None]; valid_egress_ts = [t for i, t in enumerate(egress_ts) if egress_vals[i] is not None]
            if valid_ingress_ts: ax.step(valid_ingress_ts, valid_ingress_vals, where='pre', label='Ingress (Received)', color='blue')
            if valid_egress_ts: ax.step(valid_egress_ts, valid_egress_vals, where='pre', label='Egress (Sent)', color='red')
            ax.set_xlabel("Time (UTC)"); ax.set_ylabel("Bytes / Second"); ax.set_title(f"Cloud Run Network Traffic Rate: {srv_name}\nLast {hrs_back} Hours (1 min alignment)") # Updated title
            ax.legend(); ax.grid(True); ax.set_ylim(bottom=0)
            locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=pytz.utc); formatter = mdates.ConciseDateFormatter(locator, tz=pytz.utc)
            ax.xaxis.set_major_locator(locator); ax.xaxis.set_major_formatter(formatter)
            fig.autofmt_xdate(); plt.tight_layout(); plt.savefig(filename); print(f"✅ Network chart saved to {filename}"); plt.close(fig)
        else: print("Skipping network chart: missing data.")

        return ret


    def generate_generic_metric_chart(self,
                                      metric_type: str,
                                      aggregation: monitoring_v3.Aggregation,
                                      output_filename: Union[str, Path],
                                      filter_str: str = "",
                                      end_time: Optional[datetime.datetime] = None,
                                      duration_hours: Optional[float] = None,
                                      plot_title: Optional[str] = None,
                                      y_axis_label: Optional[str] = None,
                                      plot_style: str = 'step'):
        # (Implementation remains the same as previous version)
        print(f"\n--- Generating Generic Chart for {metric_type} ---")
        out_filename_path = Path(output_filename); output_dir = out_filename_path.parent; output_dir.mkdir(parents=True, exist_ok=True)
        effective_duration_hours = duration_hours if duration_hours is not None else self.default_hours_back
        if end_time is None: end_time = datetime.datetime.now(pytz.utc)
        elif end_time.tzinfo is None: print("Warning: end_time is naive. Assuming UTC."); end_time = end_time.replace(tzinfo=pytz.utc)
        start_time = end_time - datetime.timedelta(hours=effective_duration_hours); full_filter = f'metric.type="{metric_type}"';
        if filter_str: full_filter += f' AND ({filter_str})'
        timestamps, values = self._fetch_time_series(full_filter, metric_type, aggregation, start_time, end_time)
        if timestamps:
            print(f"Generating plot: {out_filename_path}...")
            fig, ax = plt.subplots(figsize=(12, 6)); valid_values = [v for v in values if v is not None]; valid_timestamps = [t for i, t in enumerate(timestamps) if values[i] is not None]
            if not valid_timestamps: print("⚠️ No valid data points. Skipping plot."); plt.close(fig); return
            if plot_style == 'step': ax.step(valid_timestamps, valid_values, where='pre', color='purple')
            elif plot_style == 'line': ax.plot(valid_timestamps, valid_values, marker='.', linestyle='-', color='purple')
            else: print(f"Warning: Unknown plot_style '{plot_style}'. Defaulting 'step'."); ax.step(valid_timestamps, valid_values, where='pre', color='purple')
            ax.set_xlabel("Time (UTC)"); effective_y_label = y_axis_label if y_axis_label else metric_type.split('/')[-1]; ax.set_ylabel(effective_y_label); effective_title = plot_title if plot_title else f"{metric_type}\nLast {effective_duration_hours} Hours"; ax.set_title(effective_title); ax.grid(True)
            try: min_val = min(valid_values); max_val = max(valid_values); padding = (max_val - min_val) * 0.05 if max_val > min_val else 0.5; ax.set_ylim(bottom=min_val - padding, top=max_val + padding)
            except Exception: pass
            locator = mdates.AutoDateLocator(minticks=5, maxticks=10, tz=pytz.utc); formatter = mdates.ConciseDateFormatter(locator, tz=pytz.utc)
            ax.xaxis.set_major_locator(locator); ax.xaxis.set_major_formatter(formatter)
            fig.autofmt_xdate(); plt.tight_layout(); plt.savefig(out_filename_path); print(f"✅ Generic chart saved to {out_filename_path}"); plt.close(fig)
        else: print("Skipping generic chart: missing data.")

# --- End of Class Definition ---



GeminiMonitoring = RiccCloudMonitoring()

#Gemini can call this function to produce a chart file.
#@ricc_fun_call_wrapper
def gfc_generate_cloud_run_requests_vs_latency_chart(
                                                 service_name: str,
                                                 location: Optional[str] = None,
                                                 hours_back: Optional[int] = None,
                                                 investigation_date_str: Optional[str] = None,
                                                 #output_dir: Optional[Union[str, Path]] = None,
                                                 latency_percentile: float = LATENCY_PERCENTILE_DEFAULT
                                                 ):
    '''Gemini can call this function to produce a chart file.
    It fecthes Monitoring Data, and it draws/creates a PNG file containing all data for the last N hours.
    This shows the inbound/outbound traffic in red/blue colors, for the user to see.
    When in doubt, use 24 hours.

    Arguments:
        service_name: the Cloud Run service
        location: the Cloud Run location (region)
        hours_back: how many hours back should the graph look to (default: 24)
    '''

    log_function_called(f"gfc_generate_cloud_run_requests_vs_latency_chart(service_name='{service_name}',location='{location}', investigation_date={investigation_date})")
    if investigation_date_str is not None:
        investigation_date = datetime.datetime.strptime(investigation_date_str, "%Y-%m-%d")
    else:
        investigation_date = datetime.datetime.now(pytz.utc).strftime("%Y-%m-%d")

    ret = GeminiMonitoring.generate_cloud_run_requests_vs_latency_chart(
            service_name=service_name,
            hours_back=hours_back,
            latency_percentile=latency_percentile,
            investigation_date=investigation_date,
            location=location,
            )
    #print(f"DEB: ret = {ret}")
    log_function_call_output('gfc_generate_cloud_run_requests_vs_latency_chart', ret)
    return ret


def gfc_generate_cloud_run_instance_chart(service_name: str): #, location: str=None, hours_back: float=None):
    '''Gemini can call this function to produce a chart file.


    Arguments:
        service_name: the Cloud Run service
    '''
    print("=== TODO function called: gfc_generate_cloud_run_instance_chart ===")
    log_function_called(f"gfc_generate_cloud_run_instance_chart(service_name='{service_name}')")
    ret = GeminiMonitoring.generate_cloud_run_instance_chart(
        service_name=service_name,
        # location=location,
        # hours_back=hours_back,
        # latency_percentile=latency_percentile
        )
    log_function_call_output('gfc_generate_cloud_run_instance_chart', ret)
    return ret # { 'csv_data': "a,b,c\n1,2,3", 'file_name': '.cache/todo.png' , 'ret': ret}


def gfc_generate_cloud_run_network_chart(service_name: str):
    '''generates a Cloud Run network chart with IN/OUT bytes


    Arguments:
        service_name: the Cloud Run service
        '''
    log_function_called(f"gfc_generate_cloud_run_network_chart(service_name='{service_name}')")

    ret = GeminiMonitoring.generate_cloud_run_network_chart(
        service_name=service_name,
        # location=location,
        hours_back=DEFAULT_HOURS_BACK_GLOBAL,
        # hours_back=hours_back,
        # latency_percentile=latency_percentile
        )
    print(f"DEB: ret = {ret}")
    log_function_call_output('gfc_generate_cloud_run_network_chart', ret)
    return ret # { 'csv_data': "a,b,c\n1,2,3", 'file_name': '.cache/todo.png' , 'ret': ret}

def gfc_generate_cloud_run_cpu_memory_chart(service_name: str):
    '''Generates a chart containing CPU and MEM %age info, with a percentile.

    TODO: add more params.

    Arguments:
        service_name: the Cloud Run service
    '''
    log_function_called(f"gfc_generate_cloud_run_network_chart(service_name='{service_name}')")
    ret = GeminiMonitoring.generate_cloud_run_cpu_memory_chart(
        service_name=service_name,
        hours_back=DEFAULT_HOURS_BACK_GLOBAL,
    )
    print(f"DEB: ret = {ret}")
    log_function_call_output('gfc_generate_cloud_run_network_chart', ret)
    return ret



def get_monitoring_chart_paths(project_id, region, service_id):
    '''Needed'''
    return ['boh todo implement me riccardo']
