"""
File watcher for the Obsidian vault bot.
Watches the raw/ folder for new or modified Markdown files, copies each
one to archive/raw_copy/ immediately (before any processing), then
inserts a row into the processing_queue table (Phase 2 picks these up).
"""

import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

RAW_DIR = Path("./raw")
ARCHIVE_DIR = Path("./archive/raw_copy")
DB_PATH = Path("./vault.db")

# Debounce window: ignore repeat events for the same source path within
# this many seconds, since a single file write can fire both a "created"
# and a "modified" event.
DEBOUNCE_SECONDS = 2


class RawNoteHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._recent = {}  # src_path -> last handled timestamp

    def on_created(self, event):
        self._handle(event)

    def on_modified(self, event):
        self._handle(event)

    def _handle(self, event):
        if event.is_directory:
            return
        src = Path(event.src_path)
        if src.suffix.lower() != ".md":
            return

        now = time.monotonic()
        last = self._recent.get(str(src))
        if last is not None and (now - last) < DEBOUNCE_SECONDS:
            return  # duplicate event for the same write, skip
        self._recent[str(src)] = now

        self._archive_and_queue(src)

    def _archive_and_queue(self, src: Path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_name = f"{src.stem}_{timestamp}{src.suffix}"
        dest = ARCHIVE_DIR / dest_name

        try:
            shutil.copy2(src, dest)
        except FileNotFoundError:
            print(f"[{datetime.now().isoformat(timespec='seconds')}] "
                  f"Skipped (file gone): {src.name}")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO processing_queue (original_filename, archive_path) "
                "VALUES (?, ?)",
                (src.name, str(dest)),
            )
            conn.commit()
            conn.close()
            print(f"[{datetime.now().isoformat(timespec='seconds')}] "
                  f"Archived + queued: {src.name} -> {dest.name}")
        except sqlite3.IntegrityError:
            print(f"[{datetime.now().isoformat(timespec='seconds')}] "
                  f"Already queued: {dest.name}")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists():
        raise SystemExit(
            f"{DB_PATH} not found — run schema.sql against it first."
        )

    handler = RawNoteHandler()
    observer = Observer()
    observer.schedule(handler, str(RAW_DIR), recursive=False)
    observer.start()
    print(f"Watching {RAW_DIR.resolve()} for new/changed .md files. "
          f"Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
