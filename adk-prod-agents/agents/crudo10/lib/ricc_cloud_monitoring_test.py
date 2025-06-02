

# Example Usage (in a separate file like main.py or example.py)
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now you can import from 'lib'
from lib.ricc_cloud_monitoring import *

if __name__ == "__main__":
    service_name = 'gemini-news-crawler-dev'
    # Initialize (loads from .env or args) - Project ID is mandatory
    monitor = RiccCloudMonitoring(default_hours_back=48) # Override default hours

    # dashboard 4
    monitor.generate_cloud_run_cpu_memory_chart()

    print(f"Testing come se fosse Geminani for service_name={service_name}")
    gfc_generate_cloud_run_requests_vs_latency_chart(service_name=service_name)
    gfc_generate_cloud_run_instance_chart(service_name=service_name)
    gfc_generate_cloud_run_network_chart(service_name=service_name)
    gfc_generate_cloud_run_cpu_memory_chart(service_name=service_name)

    try:

        # --- Cloud Run Examples ---
        # Generate charts using defaults stored in the instance (from env vars)
        monitor.generate_cloud_run_network_chart()
        #exit(42)
        monitor.generate_cloud_run_instance_chart()
        monitor.generate_cloud_run_requests_vs_latency_chart(latency_percentile=99) # Override percentile


        # Generate chart for a specific service/location overriding defaults
        monitor.generate_cloud_run_instance_chart(
            service_name='gemini-news-crawler-dev', # "my-other-service",
            location="europe-west1",
            hours_back=12
        )

        # --- Generic Chart Example ---
        print("\nTEST() --- Generating Example Generic Chart (GCE CPU Utilization - Class Based) ---")
        cpu_aggregation = monitoring_v3.Aggregation(
            alignment_period={"seconds": 60 * 10}, # 10 min alignment
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_MEAN,
            group_by_fields = ["resource.label.\"instance_id\""]
        )
        if monitor.default_region:
            zone_suffix = "-b" # Assuming a standard zone suffix, adjust if needed
            cpu_filter = f'resource.type="gce_instance" AND resource.labels.zone="{monitor.default_region}{zone_suffix}"'
            # Define output path using instance's base dir
            duration_days = 3
            generic_output_file = monitor.default_output_dir / "generic" / f"gce_cpu_zone_{monitor.default_region}{zone_suffix}_{duration_days}d_custom.png"

            monitor.generate_generic_metric_chart(
                metric_type="compute.googleapis.com/instance/cpu/utilization",
                aggregation=cpu_aggregation,
                output_filename=generic_output_file,
                filter_str=cpu_filter,
                duration_hours=duration_days * 24, # Use specific duration
                plot_title=f"GCE CPU Util (%) [zone={monitor.default_region}{zone_suffix}] - Last {duration_days} Days (Class)",
                y_axis_label="CPU % Utilization (Class)",
            )
        else:
             print("\nSkipping generic GCE chart example: Default region not set in monitor instance.")

        print("\nClass-based chart generation examples finished! ✨")

    except ValueError as e:
         print(f"Configuration Error: {e}")
    except ConnectionError as e:
         print(f"Connection Error: {e}")
    except Exception as e:
         print(f"An unexpected error occurred: {e}")

