"""
SQLite database for tracking conversions.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


# Database file location
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "readly.db"


def get_connection():
    """Get a database connection."""
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY,
            job_id TEXT UNIQUE,
            url TEXT,
            title TEXT,
            status TEXT,
            error_message TEXT,
            viewport_width INTEGER,
            viewport_height INTEGER,
            page_size TEXT,
            pdf_path TEXT,
            epub_path TEXT,
            pdf_size_bytes INTEGER,
            epub_size_bytes INTEGER,
            pdf_downloads INTEGER DEFAULT 0,
            epub_downloads INTEGER DEFAULT 0,
            conversion_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add new columns to existing table if they don't exist
    for column, col_type in [
        ("pdf_size_bytes", "INTEGER"),
        ("epub_size_bytes", "INTEGER"),
        ("pdf_downloads", "INTEGER DEFAULT 0"),
        ("epub_downloads", "INTEGER DEFAULT 0"),
        ("pdf_path", "TEXT"),
        ("epub_path", "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE conversions ADD COLUMN {column} {col_type}")
        except:
            pass
    conn.commit()
    conn.close()


def log_conversion(
    job_id: str,
    url: str,
    title: str = None,
    status: str = "success",
    error_message: str = None,
    viewport_width: int = None,
    viewport_height: int = None,
    page_size: str = None,
    pdf_path: str = None,
    epub_path: str = None,
    pdf_size_bytes: int = None,
    epub_size_bytes: int = None,
    conversion_time: float = None
):
    """Log a conversion to the database."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO conversions
        (job_id, url, title, status, error_message, viewport_width, viewport_height, page_size, pdf_path, epub_path, pdf_size_bytes, epub_size_bytes, conversion_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (job_id, url, title, status, error_message, viewport_width, viewport_height, page_size, pdf_path, epub_path, pdf_size_bytes, epub_size_bytes, conversion_time))
    conn.commit()
    conn.close()


def increment_download(job_id: str, format: str):
    """Increment download count for a conversion."""
    conn = get_connection()
    column = "pdf_downloads" if format == "pdf" else "epub_downloads"
    conn.execute(f"UPDATE conversions SET {column} = {column} + 1 WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()


def get_conversion(job_id: str) -> dict:
    """Get a conversion by job_id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT job_id, title, pdf_path, epub_path FROM conversions WHERE job_id = ?",
        (job_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats() -> dict:
    """Get aggregated conversion statistics."""
    conn = get_connection()

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())

    # Total counts
    total = conn.execute("SELECT COUNT(*) FROM conversions").fetchone()[0]
    success = conn.execute("SELECT COUNT(*) FROM conversions WHERE status = 'success'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM conversions WHERE status = 'failed'").fetchone()[0]

    # Today counts
    today_total = conn.execute(
        "SELECT COUNT(*) FROM conversions WHERE created_at >= ?",
        (today_start.isoformat(),)
    ).fetchone()[0]

    # This week counts
    week_total = conn.execute(
        "SELECT COUNT(*) FROM conversions WHERE created_at >= ?",
        (week_start.isoformat(),)
    ).fetchone()[0]

    # Average conversion time (successful only)
    avg_time = conn.execute(
        "SELECT AVG(conversion_time) FROM conversions WHERE status = 'success' AND conversion_time IS NOT NULL"
    ).fetchone()[0]

    # Average file sizes (successful only)
    avg_pdf_size = conn.execute(
        "SELECT AVG(pdf_size_bytes) FROM conversions WHERE status = 'success' AND pdf_size_bytes IS NOT NULL"
    ).fetchone()[0]

    avg_epub_size = conn.execute(
        "SELECT AVG(epub_size_bytes) FROM conversions WHERE status = 'success' AND epub_size_bytes IS NOT NULL"
    ).fetchone()[0]

    # Total downloads
    total_pdf_downloads = conn.execute(
        "SELECT SUM(pdf_downloads) FROM conversions"
    ).fetchone()[0] or 0

    total_epub_downloads = conn.execute(
        "SELECT SUM(epub_downloads) FROM conversions"
    ).fetchone()[0] or 0

    conn.close()

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "success_rate": round(success / total * 100, 1) if total > 0 else 0,
        "today": today_total,
        "this_week": week_total,
        "avg_conversion_time": round(avg_time, 1) if avg_time else 0,
        "avg_pdf_size_mb": round(avg_pdf_size / 1048576, 1) if avg_pdf_size else 0,
        "avg_epub_size_mb": round(avg_epub_size / 1048576, 1) if avg_epub_size else 0,
        "total_pdf_downloads": total_pdf_downloads,
        "total_epub_downloads": total_epub_downloads,
        "total_downloads": total_pdf_downloads + total_epub_downloads
    }


def get_recent(limit: int = 20) -> list:
    """Get recent conversions."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT job_id, url, title, status, error_message, viewport_width, viewport_height,
               page_size, pdf_size_bytes, epub_size_bytes, pdf_downloads, epub_downloads,
               conversion_time,
               datetime(created_at, '+8 hours') as created_at
        FROM conversions
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    return [dict(row) for row in rows]
