CREATE TABLE IF NOT EXISTS processing_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    archive_path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',
    queued_at TEXT NOT NULL DEFAULT (datetime('now')),
    processed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_status ON processing_queue(status);
