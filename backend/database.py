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
        ("device_id", "TEXT"),
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
    conversion_time: float = None,
    device_id: str = None
):
    """Log a conversion to the database."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO conversions
        (job_id, url, title, status, error_message, viewport_width, viewport_height, page_size, pdf_path, epub_path, pdf_size_bytes, epub_size_bytes, conversion_time, device_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (job_id, url, title, status, error_message, viewport_width, viewport_height, page_size, pdf_path, epub_path, pdf_size_bytes, epub_size_bytes, conversion_time, device_id))
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

    # Use UTC+8 for "Today" and "This Week" calculations
    # SQLite stores UTC, so we calculate UTC+8 boundaries then convert back to UTC
    from datetime import timezone
    utc_plus_8 = timezone(timedelta(hours=8))
    now_local = datetime.now(utc_plus_8)
    today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start_local = today_start_local - timedelta(days=today_start_local.weekday())

    # Convert to UTC for database comparison
    today_start_utc = (today_start_local - timedelta(hours=8)).replace(tzinfo=None)
    week_start_utc = (week_start_local - timedelta(hours=8)).replace(tzinfo=None)

    # Total counts
    total = conn.execute("SELECT COUNT(*) FROM conversions").fetchone()[0]
    success = conn.execute("SELECT COUNT(*) FROM conversions WHERE status = 'success'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM conversions WHERE status = 'failed'").fetchone()[0]

    # Today counts (UTC) - use strftime to match SQLite format (space separator, not T)
    today_total = conn.execute(
        "SELECT COUNT(*) FROM conversions WHERE created_at >= ?",
        (today_start_utc.strftime("%Y-%m-%d %H:%M:%S"),)
    ).fetchone()[0]

    # This week counts (UTC)
    week_total = conn.execute(
        "SELECT COUNT(*) FROM conversions WHERE created_at >= ?",
        (week_start_utc.strftime("%Y-%m-%d %H:%M:%S"),)
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


def get_device_jobs(device_id: str, limit: int = 50) -> list:
    """Get all jobs for a specific device."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT job_id, url, title, status, error_message,
               pdf_path, epub_path, pdf_size_bytes, epub_size_bytes,
               conversion_time,
               datetime(created_at, '+8 hours') as created_at
        FROM conversions
        WHERE device_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (device_id, limit)).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def check_rate_limit(device_id: str, max_per_day: int = 50) -> bool:
    """Check if device has exceeded rate limit. Returns True if within limit."""
    conn = get_connection()
    # Count conversions in last 24 hours
    count = conn.execute("""
        SELECT COUNT(*) FROM conversions
        WHERE device_id = ?
        AND created_at >= datetime('now', '-24 hours')
    """, (device_id,)).fetchone()[0]
    conn.close()

    return count < max_per_day


def get_rate_limit_remaining(device_id: str, max_per_day: int = 50) -> int:
    """Get number of conversions remaining for device today."""
    conn = get_connection()
    count = conn.execute("""
        SELECT COUNT(*) FROM conversions
        WHERE device_id = ?
        AND created_at >= datetime('now', '-24 hours')
    """, (device_id,)).fetchone()[0]
    conn.close()

    return max(0, max_per_day - count)


def get_engagement_stats() -> dict:
    """Get user engagement metrics."""
    conn = get_connection()

    active_7d = conn.execute("""
        SELECT COUNT(DISTINCT device_id) FROM conversions
        WHERE device_id IS NOT NULL
        AND created_at >= datetime('now', '-7 days')
    """).fetchone()[0]

    active_30d = conn.execute("""
        SELECT COUNT(DISTINCT device_id) FROM conversions
        WHERE device_id IS NOT NULL
        AND created_at >= datetime('now', '-30 days')
    """).fetchone()[0]

    total_devices = conn.execute("""
        SELECT COUNT(DISTINCT device_id) FROM conversions
        WHERE device_id IS NOT NULL
    """).fetchone()[0]

    repeat_users = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT device_id FROM conversions
            WHERE device_id IS NOT NULL
            GROUP BY device_id
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]

    retention_rate = round(repeat_users / total_devices * 100, 1) if total_devices > 0 else 0

    avg_per_device = conn.execute("""
        SELECT AVG(cnt) FROM (
            SELECT COUNT(*) as cnt FROM conversions
            WHERE device_id IS NOT NULL
            GROUP BY device_id
        )
    """).fetchone()[0]

    conn.close()

    return {
        "active_devices_7d": active_7d,
        "active_devices_30d": active_30d,
        "total_devices": total_devices,
        "repeat_users": repeat_users,
        "retention_rate": retention_rate,
        "avg_conversions_per_device": round(avg_per_device, 1) if avg_per_device else 0,
    }


def get_top_domains(limit: int = 10) -> list:
    """Get most converted domains."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            CASE
                WHEN url LIKE 'https://%' THEN
                    SUBSTR(url, 9, INSTR(SUBSTR(url, 9), '/') - 1)
                WHEN url LIKE 'http://%' THEN
                    SUBSTR(url, 8, INSTR(SUBSTR(url, 8), '/') - 1)
                ELSE url
            END as domain,
            COUNT(*) as count,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count
        FROM conversions
        WHERE url IS NOT NULL
        GROUP BY domain
        ORDER BY count DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_daily_trend(days: int = 30) -> list:
    """Get daily conversion counts for the last N days."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            DATE(created_at, '+8 hours') as date,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            COUNT(DISTINCT device_id) as unique_devices
        FROM conversions
        WHERE created_at >= datetime('now', ? || ' days')
        GROUP BY DATE(created_at, '+8 hours')
        ORDER BY date ASC
    """, (f"-{days}",)).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_error_breakdown() -> list:
    """Get categorized error messages."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            CASE
                WHEN error_message LIKE '%timeout%' OR error_message LIKE '%Timeout%' THEN 'Timeout'
                WHEN error_message LIKE '%rate%limit%' THEN 'Rate Limited'
                WHEN error_message LIKE '%net::ERR%' OR error_message LIKE '%Connection%' THEN 'Network Error'
                WHEN error_message LIKE '%navigation%' OR error_message LIKE '%goto%' THEN 'Page Load Failed'
                ELSE 'Other'
            END as error_category,
            COUNT(*) as count
        FROM conversions
        WHERE status = 'failed' AND error_message IS NOT NULL
        GROUP BY error_category
        ORDER BY count DESC
    """).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def cleanup_old_jobs(days: int = 7) -> int:
    """Delete jobs and their files older than specified days. Returns count of deleted jobs."""
    conn = get_connection()

    # Get file paths before deleting
    rows = conn.execute("""
        SELECT pdf_path, epub_path FROM conversions
        WHERE created_at < datetime('now', ? || ' days')
    """, (f"-{days}",)).fetchall()

    # Delete old files
    deleted_files = 0
    for row in rows:
        for path in [row["pdf_path"], row["epub_path"]]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    deleted_files += 1
                except:
                    pass

    # Delete database records
    cursor = conn.execute("""
        DELETE FROM conversions
        WHERE created_at < datetime('now', ? || ' days')
    """, (f"-{days}",))
    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count
