#!/usr/bin/env python3
"""
Interactive Logging UI Utility
Provides comprehensive views of all logging statistics from the distributed scheduler
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Optional
import curses
from curses import wrapper


class LogViewer:
    def __init__(self, log_file: Optional[str] = None, logger_instance=None):
        """
        Initialize the log viewer.

        Args:
            log_file: Path to a JSON log file to load
            logger_instance: A live Logger instance to query in real-time
        """
        self.log_file = log_file
        self.logger_instance = logger_instance
        self.data = {'events': [], 'tasks': {}}
        self.current_view = 'main'
        self.scroll_offset = 0
        self.selected_item = None

        if log_file and os.path.exists(log_file):
            self.load_from_file(log_file)
        elif logger_instance:
            self.load_from_logger()

    def load_from_file(self, filename: str):
        """Load data from a JSON log file"""
        try:
            with open(filename, 'r') as f:
                self.data = json.load(f)
            print(f"Loaded data from {filename}")
        except Exception as e:
            print(f"Error loading file: {e}")
            self.data = {'events': [], 'tasks': {}}

    def load_from_logger(self):
        """Load data from a live Logger instance"""
        if self.logger_instance:
            stats = self.logger_instance.get_all_stats()
            self.data = stats

    def refresh_data(self):
        """Refresh data from source"""
        if self.log_file and os.path.exists(self.log_file):
            self.load_from_file(self.log_file)
        elif self.logger_instance:
            self.load_from_logger()

    def get_summary_stats(self):
        """Calculate summary statistics"""
        tasks = self.data.get('tasks', {})
        events = self.data.get('events', [])

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks.values() if 'duration' in t)
        pending_tasks = total_tasks - completed_tasks

        # Event counts
        event_counts = {}
        for event in events:
            event_type = event.get('event', 'UNKNOWN')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Node statistics
        node_stats = {}
        for task in tasks.values():
            node = task.get('node', 'UNKNOWN')
            if node not in node_stats:
                node_stats[node] = {
                    'total': 0,
                    'completed': 0,
                    'durations': []
                }
            node_stats[node]['total'] += 1
            if 'duration' in task:
                node_stats[node]['completed'] += 1
                node_stats[node]['durations'].append(task['duration'])

        # Task type statistics
        task_type_stats = {}
        for task in tasks.values():
            task_name = task.get('task_name', 'UNKNOWN')
            if task_name not in task_type_stats:
                task_type_stats[task_name] = {
                    'total': 0,
                    'completed': 0,
                    'durations': []
                }
            task_type_stats[task_name]['total'] += 1
            if 'duration' in task:
                task_type_stats[task_name]['completed'] += 1
                task_type_stats[task_name]['durations'].append(task['duration'])

        # Duration statistics
        all_durations = [t['duration'] for t in tasks.values() if 'duration' in t]
        avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0
        min_duration = min(all_durations) if all_durations else 0
        max_duration = max(all_durations) if all_durations else 0

        return {
            'total_events': len(events),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'event_counts': event_counts,
            'node_stats': node_stats,
            'task_type_stats': task_type_stats,
            'avg_duration': avg_duration,
            'min_duration': min_duration,
            'max_duration': max_duration,
        }

    def format_time(self, timestamp):
        """Format timestamp as readable datetime"""
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        except:
            return str(timestamp)

    def draw_main_menu(self, stdscr):
        """Draw the main menu view"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = "=== DISTRIBUTED SCHEDULING LOGGER - MAIN MENU ==="
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD)

        stats = self.get_summary_stats()

        # Summary section
        row = 2
        stdscr.addstr(row, 2, "SUMMARY", curses.A_UNDERLINE)
        row += 1
        stdscr.addstr(row, 4, f"Total Events:     {stats['total_events']}")
        row += 1
        stdscr.addstr(row, 4, f"Total Tasks:      {stats['total_tasks']}")
        row += 1
        stdscr.addstr(row, 4, f"Completed Tasks:  {stats['completed_tasks']}")
        row += 1
        stdscr.addstr(row, 4, f"Pending Tasks:    {stats['pending_tasks']}")
        row += 2

        # Duration stats
        if stats['completed_tasks'] > 0:
            stdscr.addstr(row, 2, "TASK DURATION STATS", curses.A_UNDERLINE)
            row += 1
            stdscr.addstr(row, 4, f"Average: {stats['avg_duration']:.4f}s")
            row += 1
            stdscr.addstr(row, 4, f"Min:     {stats['min_duration']:.4f}s")
            row += 1
            stdscr.addstr(row, 4, f"Max:     {stats['max_duration']:.4f}s")
            row += 2

        # Event counts
        stdscr.addstr(row, 2, "EVENT COUNTS", curses.A_UNDERLINE)
        row += 1
        for event_type, count in sorted(stats['event_counts'].items()):
            stdscr.addstr(row, 4, f"{event_type}: {count}")
            row += 1
            if row >= height - 10:
                break

        # Menu options
        row = height - 8
        stdscr.addstr(row, 2, "VIEW OPTIONS:", curses.A_BOLD)
        row += 1
        stdscr.addstr(row, 4, "[1] View All Events")
        row += 1
        stdscr.addstr(row, 4, "[2] View All Tasks")
        row += 1
        stdscr.addstr(row, 4, "[3] View Node Statistics")
        row += 1
        stdscr.addstr(row, 4, "[4] View Task Type Statistics")
        row += 1
        stdscr.addstr(row, 4, "[R] Refresh Data  [Q] Quit")

        stdscr.refresh()

    def draw_events_view(self, stdscr):
        """Draw the events list view"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "=== ALL EVENTS ==="
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD)

        events = self.data.get('events', [])

        # Header
        row = 2
        header = f"{'#':<6} {'Time':<24} {'Node':<15} {'Event':<20} {'Task':<15}"
        stdscr.addstr(row, 2, header, curses.A_UNDERLINE)
        row += 1

        # Events list with scrolling
        max_rows = height - 6
        start_idx = self.scroll_offset
        end_idx = min(start_idx + max_rows, len(events))

        for i in range(start_idx, end_idx):
            event = events[i]
            time_str = self.format_time(event.get('time', 0))
            node = event.get('node', 'N/A')[:14]
            event_type = event.get('event', 'N/A')[:19]
            task = event.get('task_name', 'N/A')[:14]

            line = f"{i+1:<6} {time_str:<24} {node:<15} {event_type:<20} {task:<15}"
            stdscr.addstr(row, 2, line[:width-4])
            row += 1

        # Footer
        stdscr.addstr(height-2, 2, f"Showing {start_idx+1}-{end_idx} of {len(events)} events")
        stdscr.addstr(height-1, 2, "[↑/↓] Scroll  [B] Back  [R] Refresh  [Q] Quit")

        stdscr.refresh()

    def draw_tasks_view(self, stdscr):
        """Draw the tasks list view"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "=== ALL TASKS ==="
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD)

        tasks = self.data.get('tasks', {})
        task_list = list(tasks.items())

        # Header
        row = 2
        header = f"{'Task Instance':<20} {'Type':<15} {'Node':<15} {'Status':<12} {'Duration':<12}"
        stdscr.addstr(row, 2, header, curses.A_UNDERLINE)
        row += 1

        # Tasks list with scrolling
        max_rows = height - 6
        start_idx = self.scroll_offset
        end_idx = min(start_idx + max_rows, len(task_list))

        for i in range(start_idx, end_idx):
            task_id, task_data = task_list[i]
            task_id_short = task_id[:19]
            task_type = task_data.get('task_name', 'N/A')[:14]
            node = task_data.get('node', 'N/A')[:14]
            status = 'COMPLETED' if 'duration' in task_data else 'PENDING'
            duration_str = f"{task_data['duration']:.4f}s" if 'duration' in task_data else 'N/A'

            line = f"{task_id_short:<20} {task_type:<15} {node:<15} {status:<12} {duration_str:<12}"
            stdscr.addstr(row, 2, line[:width-4])
            row += 1

        # Footer
        stdscr.addstr(height-2, 2, f"Showing {start_idx+1}-{end_idx} of {len(task_list)} tasks")
        stdscr.addstr(height-1, 2, "[↑/↓] Scroll  [B] Back  [R] Refresh  [Q] Quit")

        stdscr.refresh()

    def draw_node_stats_view(self, stdscr):
        """Draw the node statistics view"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "=== NODE STATISTICS ==="
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD)

        stats = self.get_summary_stats()
        node_stats = stats['node_stats']

        # Header
        row = 2
        header = f"{'Node':<20} {'Total':<10} {'Completed':<12} {'Pending':<10} {'Avg Duration':<15}"
        stdscr.addstr(row, 2, header, curses.A_UNDERLINE)
        row += 1

        # Node statistics
        for node, data in sorted(node_stats.items()):
            total = data['total']
            completed = data['completed']
            pending = total - completed
            avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 0

            line = f"{node:<20} {total:<10} {completed:<12} {pending:<10} {avg_duration:<15.4f}s"
            stdscr.addstr(row, 2, line[:width-4])
            row += 1

            if row >= height - 3:
                break

        # Footer
        stdscr.addstr(height-1, 2, "[B] Back  [R] Refresh  [Q] Quit")

        stdscr.refresh()

    def draw_task_type_stats_view(self, stdscr):
        """Draw the task type statistics view"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "=== TASK TYPE STATISTICS ==="
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD)

        stats = self.get_summary_stats()
        task_type_stats = stats['task_type_stats']

        row = 2

        # Detailed statistics for each task type
        for task_type, data in sorted(task_type_stats.items()):
            total = data['total']
            completed = data['completed']
            pending = total - completed

            stdscr.addstr(row, 2, f"Task Type: {task_type}", curses.A_BOLD)
            row += 1
            stdscr.addstr(row, 4, f"Total Instances:     {total}")
            row += 1
            stdscr.addstr(row, 4, f"Completed:           {completed}")
            row += 1
            stdscr.addstr(row, 4, f"Pending:             {pending}")
            row += 1

            if data['durations']:
                avg_duration = sum(data['durations']) / len(data['durations'])
                min_duration = min(data['durations'])
                max_duration = max(data['durations'])

                stdscr.addstr(row, 4, f"Average Duration:    {avg_duration:.4f}s")
                row += 1
                stdscr.addstr(row, 4, f"Min Duration:        {min_duration:.4f}s")
                row += 1
                stdscr.addstr(row, 4, f"Max Duration:        {max_duration:.4f}s")
                row += 1

            row += 1

            if row >= height - 3:
                break

        # Footer
        stdscr.addstr(height-1, 2, "[B] Back  [R] Refresh  [Q] Quit")

        stdscr.refresh()

    def run_interactive(self, stdscr):
        """Run the interactive UI"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(0)   # Blocking input
        stdscr.timeout(100) # 100ms timeout for input

        while True:
            # Draw current view
            if self.current_view == 'main':
                self.draw_main_menu(stdscr)
            elif self.current_view == 'events':
                self.draw_events_view(stdscr)
            elif self.current_view == 'tasks':
                self.draw_tasks_view(stdscr)
            elif self.current_view == 'nodes':
                self.draw_node_stats_view(stdscr)
            elif self.current_view == 'task_types':
                self.draw_task_type_stats_view(stdscr)

            # Handle input
            try:
                key = stdscr.getch()

                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('r') or key == ord('R'):
                    self.refresh_data()
                    self.scroll_offset = 0
                elif key == ord('b') or key == ord('B'):
                    self.current_view = 'main'
                    self.scroll_offset = 0
                elif self.current_view == 'main':
                    if key == ord('1'):
                        self.current_view = 'events'
                        self.scroll_offset = 0
                    elif key == ord('2'):
                        self.current_view = 'tasks'
                        self.scroll_offset = 0
                    elif key == ord('3'):
                        self.current_view = 'nodes'
                        self.scroll_offset = 0
                    elif key == ord('4'):
                        self.current_view = 'task_types'
                        self.scroll_offset = 0
                elif key == curses.KEY_UP:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif key == curses.KEY_DOWN:
                    self.scroll_offset += 1
            except:
                pass

    def run_simple_cli(self):
        """Run a simple command-line interface (no curses)"""
        while True:
            print("\n" + "=" * 60)
            print("DISTRIBUTED SCHEDULING LOGGER - VIEWER")
            print("=" * 60)

            stats = self.get_summary_stats()

            print(f"\nTotal Events:     {stats['total_events']}")
            print(f"Total Tasks:      {stats['total_tasks']}")
            print(f"Completed Tasks:  {stats['completed_tasks']}")
            print(f"Pending Tasks:    {stats['pending_tasks']}")

            if stats['completed_tasks'] > 0:
                print(f"\nAverage Duration: {stats['avg_duration']:.4f}s")
                print(f"Min Duration:     {stats['min_duration']:.4f}s")
                print(f"Max Duration:     {stats['max_duration']:.4f}s")

            print("\nOPTIONS:")
            print("  [1] View All Events")
            print("  [2] View All Tasks")
            print("  [3] View Node Statistics")
            print("  [4] View Task Type Statistics")
            print("  [5] Export Summary to File")
            print("  [R] Refresh Data")
            print("  [Q] Quit")

            choice = input("\nEnter choice: ").strip().lower()

            if choice == 'q':
                break
            elif choice == 'r':
                self.refresh_data()
                print("Data refreshed!")
            elif choice == '1':
                self.print_all_events()
            elif choice == '2':
                self.print_all_tasks()
            elif choice == '3':
                self.print_node_stats()
            elif choice == '4':
                self.print_task_type_stats()
            elif choice == '5':
                self.export_summary()

    def print_all_events(self):
        """Print all events to console"""
        events = self.data.get('events', [])
        print(f"\n{'='*80}")
        print(f"ALL EVENTS ({len(events)} total)")
        print("="*80)
        print(f"{'#':<6} {'Time':<24} {'Node':<15} {'Event':<20} {'Task':<15}")
        print("-"*80)

        for i, event in enumerate(events):
            time_str = self.format_time(event.get('time', 0))
            node = event.get('node', 'N/A')
            event_type = event.get('event', 'N/A')
            task = event.get('task_name', 'N/A')

            print(f"{i+1:<6} {time_str:<24} {node:<15} {event_type:<20} {task:<15}")

        input("\nPress Enter to continue...")

    def print_all_tasks(self):
        """Print all tasks to console"""
        tasks = self.data.get('tasks', {})
        print(f"\n{'='*90}")
        print(f"ALL TASKS ({len(tasks)} total)")
        print("="*90)
        print(f"{'Task Instance':<25} {'Type':<15} {'Node':<15} {'Status':<12} {'Duration':<12}")
        print("-"*90)

        for task_id, task_data in tasks.items():
            task_type = task_data.get('task_name', 'N/A')
            node = task_data.get('node', 'N/A')
            status = 'COMPLETED' if 'duration' in task_data else 'PENDING'
            duration_str = f"{task_data['duration']:.4f}s" if 'duration' in task_data else 'N/A'

            print(f"{task_id:<25} {task_type:<15} {node:<15} {status:<12} {duration_str:<12}")

        input("\nPress Enter to continue...")

    def print_node_stats(self):
        """Print node statistics to console"""
        stats = self.get_summary_stats()
        node_stats = stats['node_stats']

        print(f"\n{'='*80}")
        print("NODE STATISTICS")
        print("="*80)

        for node, data in sorted(node_stats.items()):
            print(f"\nNode: {node}")
            print(f"  Total Tasks:      {data['total']}")
            print(f"  Completed Tasks:  {data['completed']}")
            print(f"  Pending Tasks:    {data['total'] - data['completed']}")

            if data['durations']:
                avg_duration = sum(data['durations']) / len(data['durations'])
                min_duration = min(data['durations'])
                max_duration = max(data['durations'])

                print(f"  Average Duration: {avg_duration:.4f}s")
                print(f"  Min Duration:     {min_duration:.4f}s")
                print(f"  Max Duration:     {max_duration:.4f}s")

        input("\nPress Enter to continue...")

    def print_task_type_stats(self):
        """Print task type statistics to console"""
        stats = self.get_summary_stats()
        task_type_stats = stats['task_type_stats']

        print(f"\n{'='*80}")
        print("TASK TYPE STATISTICS")
        print("="*80)

        for task_type, data in sorted(task_type_stats.items()):
            print(f"\nTask Type: {task_type}")
            print(f"  Total Instances:  {data['total']}")
            print(f"  Completed:        {data['completed']}")
            print(f"  Pending:          {data['total'] - data['completed']}")

            if data['durations']:
                avg_duration = sum(data['durations']) / len(data['durations'])
                min_duration = min(data['durations'])
                max_duration = max(data['durations'])

                print(f"  Average Duration: {avg_duration:.4f}s")
                print(f"  Min Duration:     {min_duration:.4f}s")
                print(f"  Max Duration:     {max_duration:.4f}s")

        input("\nPress Enter to continue...")

    def export_summary(self):
        """Export summary to a text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_summary_{timestamp}.txt"

        stats = self.get_summary_stats()

        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DISTRIBUTED SCHEDULING LOGGER - SUMMARY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            f.write("OVERALL STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Events:     {stats['total_events']}\n")
            f.write(f"Total Tasks:      {stats['total_tasks']}\n")
            f.write(f"Completed Tasks:  {stats['completed_tasks']}\n")
            f.write(f"Pending Tasks:    {stats['pending_tasks']}\n\n")

            if stats['completed_tasks'] > 0:
                f.write("DURATION STATISTICS\n")
                f.write("-"*80 + "\n")
                f.write(f"Average Duration: {stats['avg_duration']:.4f}s\n")
                f.write(f"Min Duration:     {stats['min_duration']:.4f}s\n")
                f.write(f"Max Duration:     {stats['max_duration']:.4f}s\n\n")

            f.write("EVENT COUNTS\n")
            f.write("-"*80 + "\n")
            for event_type, count in sorted(stats['event_counts'].items()):
                f.write(f"{event_type}: {count}\n")
            f.write("\n")

            f.write("NODE STATISTICS\n")
            f.write("-"*80 + "\n")
            for node, data in sorted(stats['node_stats'].items()):
                f.write(f"\nNode: {node}\n")
                f.write(f"  Total Tasks:      {data['total']}\n")
                f.write(f"  Completed Tasks:  {data['completed']}\n")
                f.write(f"  Pending Tasks:    {data['total'] - data['completed']}\n")

                if data['durations']:
                    avg = sum(data['durations']) / len(data['durations'])
                    f.write(f"  Average Duration: {avg:.4f}s\n")
            f.write("\n")

            f.write("TASK TYPE STATISTICS\n")
            f.write("-"*80 + "\n")
            for task_type, data in sorted(stats['task_type_stats'].items()):
                f.write(f"\nTask Type: {task_type}\n")
                f.write(f"  Total Instances:  {data['total']}\n")
                f.write(f"  Completed:        {data['completed']}\n")
                f.write(f"  Pending:          {data['total'] - data['completed']}\n")

                if data['durations']:
                    avg = sum(data['durations']) / len(data['durations'])
                    min_dur = min(data['durations'])
                    max_dur = max(data['durations'])
                    f.write(f"  Average Duration: {avg:.4f}s\n")
                    f.write(f"  Min Duration:     {min_dur:.4f}s\n")
                    f.write(f"  Max Duration:     {max_dur:.4f}s\n")

        print(f"\nSummary exported to {filename}")
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Interactive Logging UI Utility for Distributed Scheduler'
    )
    parser.add_argument(
        '-f', '--file',
        help='Path to a JSON log file to view',
        default=None
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Use simple CLI mode instead of interactive curses UI'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Automatically load the latest log file from logs/ directory'
    )

    args = parser.parse_args()

    log_file = args.file

    # Find latest log file if requested
    if args.latest and not log_file:
        log_dir = 'logs'
        if os.path.exists(log_dir):
            log_files = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.startswith('logger_data_') and f.endswith('.json')
            ]
            if log_files:
                log_file = max(log_files, key=os.path.getmtime)
                print(f"Loading latest log file: {log_file}")
            else:
                print("No log files found in logs/ directory")
                sys.exit(1)
        else:
            print("logs/ directory not found")
            sys.exit(1)

    # Create viewer
    viewer = LogViewer(log_file=log_file)

    if not log_file:
        print("No log file specified. Use -f <file> or --latest to load data.")
        print("Example: python log_viewer.py --latest")
        sys.exit(1)

    # Run UI
    if args.simple:
        viewer.run_simple_cli()
    else:
        try:
            wrapper(viewer.run_interactive)
        except KeyboardInterrupt:
            print("\nExiting...")


if __name__ == "__main__":
    main()
