import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import signal

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, script):
        self.filename = filename
        self.script = script
        self.process = subprocess.Popen(['./run.sh'])
        self.scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
        self.scheduler.add_job(self.restart_script, 'cron', hour=13, minute=21)
        self.scheduler.start()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.filename):
            print(f"{self.filename} has changed, restarting {self.script}")
            self.restart_script()

    def restart_script(self):
        os.kill(self.process.pid, signal.SIGINT)  # send SIGINT to the process
        self.process.wait()  # wait for the process to terminate
        self.process = subprocess.Popen(['./run.sh'])  # start the shell script again
if __name__ == "__main__":
    filename = 'config.json'
    script = 'main.py'
    event_handler = FileChangeHandler(filename, script)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()