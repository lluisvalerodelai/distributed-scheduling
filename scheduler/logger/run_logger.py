#!/usr/bin/env python3
import sys
import signal
import time
from datetime import datetime
from logger import Logger

# Configuration
LOGGER_IP = '0.0.0.0'  # Listen on all interfaces
LOGGER_PORT = 5001
OUTPUT_DIR = 'logs'

# Create output directory if it doesn't exist
import os
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize logger
logger = Logger(LOGGER_IP, LOGGER_PORT)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutting down logger...")

    # Print summary
    logger.print_summary()

    # Export data to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"logger_data_{timestamp}.json")
    logger.export_to_file(filename)

    # Stop the logger
    logger.stop()

    print("Logger stopped successfully.")
    sys.exit(0)

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("="*50)
    print("DISTRIBUTED SCHEDULING LOGGER")
    print("="*50)
    print(f"Listening on {LOGGER_IP}:{LOGGER_PORT}")
    print(f"Logs will be saved to: {OUTPUT_DIR}/")
    print("Press Ctrl+C to stop and save data")
    print("="*50 + "\n")

    # Start the logger
    logger.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
