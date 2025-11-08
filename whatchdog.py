from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PDFreader import pdf_reader
import time
from pathlib import Path

WATCH_PATH = r"E:\VENV\rag_system\PDF_keeper" 

class SimpleHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"[CREATED] {event.src_path}")
        filename=event.src_path
        if filename.lower().endswith(".pdf"):
            print("PDF file detected and sent for processing.")
            pdf_reader(filename)

    def on_modified(self, event):
        print(f"[MODIFIED] {event.src_path}")

    def on_deleted(self, event):
        print(f"[DELETED] {event.src_path}")

    def on_moved(self, event):
        print(f"[MOVED] {event.src_path} → {event.dest_path}")

def main():
    # اطمینان از وجود پوشه
    Path(WATCH_PATH).mkdir(exist_ok=True)

    event_handler = SimpleHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=False)

    print(f"Watching: {WATCH_PATH}")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()