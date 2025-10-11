#!/usr/bin/env python3
"""
Real-time Logger Monitor
Connects to a running Logger instance and displays live statistics updates
"""

import sys
import os
import time
import curses
from datetime import datetime

# Add parent directory to path to import Logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger.logger import Logger


class LiveMonitor:
    def __init__(self, logger_ip='127.0.0.1', logger_port=5001):
        """
        Initialize the live monitor.

        Args:
            logger_ip: IP address of the logger server
            logger_port: Port of the logger server
        """
        self.logger_ip = logger_ip
        self.logger_port = logger_port
        self.logger = None
        self.refresh_interval = 1.0  # seconds
        self.last_event_count = 0
        self.last_task_count = 0

    def connect_to_logger(self):
        """
        Connect to or create a shared logger instance.
        In practice, you'd want to connect to an existing logger instance.
        For now, we'll use a file-based approach.
        """
        # Note: In a real scenario, you'd connect to a shared logger instance
        # or use IPC/shared memory. For simplicity, we'll monitor log files.
        pass

    def get_live_stats(self):
        """
        Get current statistics from the logger.
        In a production setup, this would query a live Logger instance.
        For now, we'll read from the latest log file.
        """
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            return None

        # Find the latest log file
        log_files = [
            os.path.join(log_dir, f)
            for f in os.listdir(log_dir)
            if f.startswith('logger_data_') and f.endswith('.json')
        ]

        if not log_files:
            return None

        latest_file = max(log_files, key=os.path.getmtime)

        # Import log_viewer to use its stats calculation
        from log_viewer import LogViewer

        viewer = LogViewer(log_file=latest_file)
        return viewer.get_summary_stats()

    def draw_dashboard(self, stdscr):
        """Draw a real-time dashboard"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = "=== DISTRIBUTED SCHEDULER - LIVE MONITOR ==="
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_REVERSE)
        stdscr.addstr(1, max(0, (width - len(timestamp)) // 2), timestamp)

        stats = self.get_live_stats()

        if not stats:
            stdscr.addstr(3, 2, "No log data available yet...", curses.A_DIM)
            stdscr.addstr(4, 2, "Waiting for logger to generate data...")
            stdscr.addstr(height - 1, 2, "[Q] Quit")
            stdscr.refresh()
            return

        row = 3

        # Real-time metrics
        stdscr.addstr(row, 2, "REAL-TIME METRICS", curses.A_BOLD | curses.A_UNDERLINE)
        row += 1

        # Event rate
        events_delta = stats['total_events'] - self.last_event_count
        tasks_delta = stats['total_tasks'] - self.last_task_count
        event_rate = events_delta / self.refresh_interval
        task_rate = tasks_delta / self.refresh_interval

        stdscr.addstr(row, 4, f"Event Rate:        {event_rate:.2f} events/sec")
        row += 1
        stdscr.addstr(row, 4, f"Task Creation Rate: {task_rate:.2f} tasks/sec")
        row += 2

        # Update counters
        self.last_event_count = stats['total_events']
        self.last_task_count = stats['total_tasks']

        # Overall statistics
        stdscr.addstr(row, 2, "OVERALL STATISTICS", curses.A_BOLD | curses.A_UNDERLINE)
        row += 1
        stdscr.addstr(row, 4, f"Total Events:      {stats['total_events']}")
        row += 1
        stdscr.addstr(row, 4, f"Total Tasks:       {stats['total_tasks']}")
        row += 1
        stdscr.addstr(row, 4, f"Completed Tasks:   {stats['completed_tasks']}")
        row += 1
        stdscr.addstr(row, 4, f"Pending Tasks:     {stats['pending_tasks']}")
        row += 2

        # Progress bar for completion
        if stats['total_tasks'] > 0:
            completion_percent = (stats['completed_tasks'] / stats['total_tasks']) * 100
            bar_width = 40
            filled = int((completion_percent / 100) * bar_width)
            bar = '█' * filled + '░' * (bar_width - filled)
            stdscr.addstr(row, 4, f"Completion: [{bar}] {completion_percent:.1f}%")
            row += 2

        # Duration statistics
        if stats['completed_tasks'] > 0:
            stdscr.addstr(row, 2, "PERFORMANCE METRICS", curses.A_BOLD | curses.A_UNDERLINE)
            row += 1
            stdscr.addstr(row, 4, f"Average Duration:  {stats['avg_duration']:.4f}s")
            row += 1
            stdscr.addstr(row, 4, f"Min Duration:      {stats['min_duration']:.4f}s")
            row += 1
            stdscr.addstr(row, 4, f"Max Duration:      {stats['max_duration']:.4f}s")
            row += 2

        # Event type breakdown
        stdscr.addstr(row, 2, "EVENT BREAKDOWN", curses.A_BOLD | curses.A_UNDERLINE)
        row += 1
        for event_type, count in sorted(stats['event_counts'].items()):
            stdscr.addstr(row, 4, f"{event_type:<20} {count:>6}")
            row += 1
            if row >= height - 12:
                break

        row += 1

        # Node activity (top section)
        if row < height - 8:
            stdscr.addstr(row, 2, "NODE ACTIVITY", curses.A_BOLD | curses.A_UNDERLINE)
            row += 1

            node_stats = stats.get('node_stats', {})
            for node, data in sorted(node_stats.items()):
                if row >= height - 6:
                    break

                completed = data['completed']
                total = data['total']
                percent = (completed / total * 100) if total > 0 else 0

                # Mini progress bar
                bar_width = 20
                filled = int((percent / 100) * bar_width)
                bar = '█' * filled + '░' * (bar_width - filled)

                line = f"{node:<15} [{bar}] {completed}/{total} ({percent:.0f}%)"
                stdscr.addstr(row, 4, line[:width-6])
                row += 1

        # Footer with controls
        footer_row = height - 2
        stdscr.addstr(footer_row, 2, f"Refresh Rate: {self.refresh_interval}s", curses.A_DIM)
        stdscr.addstr(height - 1, 2, "[Q] Quit  [+/-] Adjust refresh rate  [R] Force refresh")

        stdscr.refresh()

    def run(self, stdscr):
        """Run the live monitor"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(int(self.refresh_interval * 1000))

        last_refresh = 0

        while True:
            current_time = time.time()

            # Auto-refresh at interval
            if current_time - last_refresh >= self.refresh_interval:
                self.draw_dashboard(stdscr)
                last_refresh = current_time

            # Handle input
            try:
                key = stdscr.getch()

                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('r') or key == ord('R'):
                    self.draw_dashboard(stdscr)
                    last_refresh = current_time
                elif key == ord('+') or key == ord('='):
                    self.refresh_interval = min(10.0, self.refresh_interval + 0.5)
                    stdscr.timeout(int(self.refresh_interval * 1000))
                elif key == ord('-') or key == ord('_'):
                    self.refresh_interval = max(0.5, self.refresh_interval - 0.5)
                    stdscr.timeout(int(self.refresh_interval * 1000))
            except:
                pass

            time.sleep(0.1)

    def run_simple(self):
        """Run simple text-based live monitor without curses"""
        print("="*80)
        print("DISTRIBUTED SCHEDULER - LIVE MONITOR (Simple Mode)")
        print("="*80)
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                stats = self.get_live_stats()

                if stats:
                    # Clear screen (simple method)
                    os.system('clear' if os.name != 'nt' else 'cls')

                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n[{timestamp}]")
                    print("="*80)

                    print(f"\nTotal Events:     {stats['total_events']}")
                    print(f"Total Tasks:      {stats['total_tasks']}")
                    print(f"Completed Tasks:  {stats['completed_tasks']}")
                    print(f"Pending Tasks:    {stats['pending_tasks']}")

                    if stats['completed_tasks'] > 0:
                        completion_percent = (stats['completed_tasks'] / stats['total_tasks']) * 100
                        print(f"Completion:       {completion_percent:.1f}%")
                        print(f"\nAverage Duration: {stats['avg_duration']:.4f}s")

                    print("\nEvent Breakdown:")
                    for event_type, count in sorted(stats['event_counts'].items()):
                        print(f"  {event_type}: {count}")

                    print("\nNode Activity:")
                    node_stats = stats.get('node_stats', {})
                    for node, data in sorted(node_stats.items()):
                        completed = data['completed']
                        total = data['total']
                        percent = (completed / total * 100) if total > 0 else 0
                        print(f"  {node}: {completed}/{total} ({percent:.0f}%)")

                else:
                    print("Waiting for log data...")

                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Real-time Logger Monitor for Distributed Scheduler'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Use simple text mode instead of curses UI'
    )
    parser.add_argument(
        '--refresh',
        type=float,
        default=1.0,
        help='Refresh interval in seconds (default: 1.0)'
    )

    args = parser.parse_args()

    monitor = LiveMonitor()
    monitor.refresh_interval = args.refresh

    if args.simple:
        monitor.run_simple()
    else:
        try:
            curses.wrapper(monitor.run)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")


if __name__ == "__main__":
    main()
