import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, script):
        self.filename = filename
        self.script = script
        self.process = subprocess.Popen(f'python3 {self.script}', shell=True)
        self.scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
        self.scheduler.add_job(self.restart_script, 'cron', hour=12, minute=50)
        self.scheduler.start()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.filename):
            print(f"{self.filename} has changed, restarting {self.script}")
            self.restart_script()

    def restart_script(self):
        self.process.kill()
        self.process = subprocess.Popen(f'python3 {self.script}', shell=True, preexec_fn=os.setsid)

if __name__ == "__main__":
    filename = 'config.json'
    script = 'main.py'
    event_handler = FileChangeHandler(filename, script)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()