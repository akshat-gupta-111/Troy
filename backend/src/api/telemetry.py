import os
import logging

from azure.monitor.opentelemetry import configure_azure_monitor

logger = logging.getLogger("troy-telemetry")

def setup_telemetry():

    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning("No instrumentation key found, Telemetry Disabled.")
        return
    try:
        configure_azure_monitor(
            connection_string =connection_string,
            logger_name = "troy-tracer",
        )
        logger.info("Azure Monitor tracking enabled")
    except Exception as e:
        logger.error(f"Faild to initialize Azure monitor : {e}")


