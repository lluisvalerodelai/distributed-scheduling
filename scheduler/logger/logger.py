import threading
import socket
import time
import json
from datetime import datetime


class Logger:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.events = []  # List of all events
        self.tasks = {}  # Dictionary of task data by task_name
        self.task_counters = {}  # Counter for each task type
        self.lock = threading.Lock()
        self.server_socket = None
        self.running = False

    def start(self):
        """Start the TCP server to listen for events"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)

        print(f"Logger started on {self.ip}:{self.port}")

        # Start server thread
        server_thread = threading.Thread(target=self._accept_connections)
        server_thread.daemon = True
        server_thread.start()

    def stop(self):
        """Stop the TCP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def _accept_connections(self):
        """Accept incoming connections and spawn handler threads"""
        while self.running:
            try:
                self.server_socket.settimeout(
                    1.0
                )  # Allow periodic checks of self.running
                try:
                    client_socket, address = self.server_socket.accept()
                    handler = threading.Thread(
                        target=self._handle_client, args=(client_socket, address)
                    )
                    handler.daemon = True
                    handler.start()
                except socket.timeout:
                    continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                break

    def _handle_client(self, client_socket, address):
        """Handle a client connection and parse messages"""
        try:
            data = client_socket.recv(4096).decode('utf-8').strip()
            if data:
                self._parse_and_log_event(data)
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def _parse_and_log_event(self, message):
        """
        Parse message format: NODE [HOSTNAME] EVENT [EVENT_NAME] TIME [TIME] TASK [TASK_NAME]

        Expected events:
        - TASK_REQUESTED: Node asks for a task
        - TASK_ASSIGNED: Scheduler assigns task to node
        - TASK_FINISHED: Node completes task

        Task names: matmul, primes, array, fileIO
        """
        try:
            parts = message.split()
            event_data = {}

            # Parse key-value pairs
            i = 0
            while i < len(parts):
                if parts[i] == 'NODE' and i + 1 < len(parts):
                    event_data['node'] = parts[i + 1]
                    i += 2
                elif parts[i] == 'EVENT' and i + 1 < len(parts):
                    event_data['event'] = parts[i + 1]
                    i += 2
                elif parts[i] == 'TIME' and i + 1 < len(parts):
                    event_data['time'] = float(parts[i + 1])
                    i += 2
                elif parts[i] == 'TASK' and i + 1 < len(parts):
                    event_data['task_name'] = parts[i + 1]
                    i += 2
                else:
                    i += 1

            # Validate required fields
            if 'node' not in event_data or 'event' not in event_data:
                print(f"Invalid event format: {message}")
                return

            # Use current time if not provided
            if 'time' not in event_data:
                event_data['time'] = time.time()

            # Log the event
            with self.lock:
                self.events.append(event_data)
                self._process_event(event_data)

            print(f"Logged: {event_data}")

        except Exception as e:
            print(f"Error parsing message '{message}': {e}")

    def _process_event(self, event_data):
        """Process event and update task tracking"""
        task_name = event_data.get('task_name')
        if task_name is None:
            return

        node = event_data['node']
        event_name = event_data['event']

        # Generate unique task instance key: task_name + instance number
        if event_name == 'TASK_ASSIGNED':
            # Initialize counter for this task type if needed
            if task_name not in self.task_counters:
                self.task_counters[task_name] = 0

            # Increment and create unique task instance
            self.task_counters[task_name] += 1
            task_instance = f"{task_name}_{self.task_counters[task_name]}"
            event_data['task_instance'] = task_instance

            # Create new task entry
            self.tasks[task_instance] = {
                'task_name': task_name,
                'node': node,
                'assigned_time': event_data['time'],
                'events': [event_data],
            }

        elif event_name == 'TASK_REQUESTED':
            # Just log the request event
            pass

        elif event_name == 'TASK_FINISHED':
            # Find the most recent assigned task of this type for this node
            task_instance = None
            for tid, tdata in reversed(list(self.tasks.items())):
                if (
                    tdata.get('task_name') == task_name
                    and tdata.get('node') == node
                    and 'finished_time' not in tdata
                ):
                    task_instance = tid
                    break

            if task_instance:
                event_data['task_instance'] = task_instance
                self.tasks[task_instance]['events'].append(event_data)
                self.tasks[task_instance]['finished_time'] = event_data['time']

                # Calculate duration from assignment to finish
                if 'assigned_time' in self.tasks[task_instance]:
                    duration = (
                        event_data['time'] - self.tasks[task_instance]['assigned_time']
                    )
                    self.tasks[task_instance]['duration'] = duration

    def get_task_stats(self, task_instance):
        """Get statistics for a specific task instance"""
        with self.lock:
            return self.tasks.get(task_instance)

    def get_task_type_stats(self, task_name):
        """Get statistics for all instances of a task type"""
        with self.lock:
            task_instances = {
                tid: data
                for tid, data in self.tasks.items()
                if data.get('task_name') == task_name
            }

            total = len(task_instances)
            completed = sum(1 for t in task_instances.values() if 'duration' in t)
            avg_duration = 0
            if completed > 0:
                durations = [
                    t['duration'] for t in task_instances.values() if 'duration' in t
                ]
                avg_duration = sum(durations) / len(durations)

            return {
                'task_name': task_name,
                'total_instances': total,
                'completed_instances': completed,
                'average_duration': avg_duration,
                'instances': task_instances,
            }

    def get_node_stats(self, node):
        """Get statistics for a specific node"""
        with self.lock:
            node_tasks = {
                tid: data
                for tid, data in self.tasks.items()
                if data.get('node') == node
            }

            # Calculate node-specific statistics
            total_tasks = len(node_tasks)
            completed_tasks = sum(1 for t in node_tasks.values() if 'duration' in t)
            avg_duration = 0
            if completed_tasks > 0:
                durations = [
                    t['duration'] for t in node_tasks.values() if 'duration' in t
                ]
                avg_duration = sum(durations) / len(durations)

            return {
                'node': node,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'average_duration': avg_duration,
                'tasks': node_tasks,
            }

    def get_all_stats(self):
        """Get all statistics"""
        with self.lock:
            return {
                'total_events': len(self.events),
                'total_tasks': len(self.tasks),
                'tasks': dict(self.tasks),
                'events': list(self.events),
            }

    def export_to_file(self, filename):
        """Export all data to a JSON file"""
        with self.lock:
            data = {
                'events': self.events,
                'tasks': self.tasks,
                'export_time': time.time(),
                'export_datetime': datetime.now().isoformat(),
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data exported to {filename}")

    def print_summary(self):
        """Print a summary of logged data"""
        with self.lock:
            print("\n" + "=" * 50)
            print("LOGGER SUMMARY")
            print("=" * 50)
            print(f"Total events: {len(self.events)}")
            print(f"Total tasks: {len(self.tasks)}")

            # Count events by type
            event_counts = {}
            for event in self.events:
                event_type = event.get('event', 'UNKNOWN')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1

            print("\nEvent counts:")
            for event_type, count in sorted(event_counts.items()):
                print(f"  {event_type}: {count}")

            # Calculate average task duration
            completed_tasks = [
                task for task in self.tasks.values() if 'duration' in task
            ]
            if completed_tasks:
                avg_duration = sum(t['duration'] for t in completed_tasks) / len(
                    completed_tasks
                )
                min_duration = min(t['duration'] for t in completed_tasks)
                max_duration = max(t['duration'] for t in completed_tasks)

                print(f"\nCompleted tasks: {len(completed_tasks)}")
                print(f"Average task duration: {avg_duration:.4f} seconds")
                print(f"Min task duration: {min_duration:.4f} seconds")
                print(f"Max task duration: {max_duration:.4f} seconds")

            # Tasks per node
            node_counts = {}
            node_durations = {}
            for task in self.tasks.values():
                node = task.get('node', 'UNKNOWN')
                node_counts[node] = node_counts.get(node, 0) + 1
                if 'duration' in task:
                    if node not in node_durations:
                        node_durations[node] = []
                    node_durations[node].append(task['duration'])

            print("\nTasks per node:")
            for node in sorted(node_counts.keys()):
                count = node_counts[node]
                avg_str = ""
                if node in node_durations:
                    avg = sum(node_durations[node]) / len(node_durations[node])
                    avg_str = f" (avg duration: {avg:.4f}s)"
                print(f"  {node}: {count} tasks{avg_str}")

            # Tasks per type
            task_type_counts = {}
            task_type_durations = {}
            for task in self.tasks.values():
                task_name = task.get('task_name', 'UNKNOWN')
                task_type_counts[task_name] = task_type_counts.get(task_name, 0) + 1
                if 'duration' in task:
                    if task_name not in task_type_durations:
                        task_type_durations[task_name] = []
                    task_type_durations[task_name].append(task['duration'])

            print("\nTasks per type:")
            for task_name in sorted(task_type_counts.keys()):
                count = task_type_counts[task_name]
                avg_str = ""
                if task_name in task_type_durations:
                    avg = sum(task_type_durations[task_name]) / len(
                        task_type_durations[task_name]
                    )
                    min_dur = min(task_type_durations[task_name])
                    max_dur = max(task_type_durations[task_name])
                    avg_str = (
                        f" (avg: {avg:.4f}s, min: {min_dur:.4f}s, max: {max_dur:.4f}s)"
                    )
                print(f"  {task_name}: {count} tasks{avg_str}")

            print("=" * 50 + "\n")
