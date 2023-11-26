import threading
import sys

# Create a mutex object
mutex = threading.Mutex()

def handle_log_message(record):
    # Acquire the mutex before writing to stderr
    with mutex:
        # Write the formatted log message to stderr
        sys.stderr.write(record.msg + record.terminator)