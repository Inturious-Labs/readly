"""
Readly Backend API
Converts webpage URLs to PDF and EPUB formats.
"""

import hashlib
import hmac
import json
import os
import tempfile
import uuid
from pathlib import Path
from fastapi import Cookie, FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, HttpUrl

from converter import WebConverter
from database import (
    init_db, log_conversion, get_stats, get_recent, increment_download, get_conversion,
    get_device_jobs, check_rate_limit, get_rate_limit_remaining,
    get_engagement_stats, get_top_domains, get_daily_trend, get_error_breakdown
)

# Admin password from environment variable
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Rate limit: max conversions per device per day
RATE_LIMIT_PER_DAY = 50

# Environment indicator (development or production)
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# Jinja2 template setup
TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

app = FastAPI(
    title="Readly API",
    description="Convert webpage URLs to PDF and EPUB",
    version="0.1.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store converted files temporarily
TEMP_DIR = tempfile.gettempdir()
conversions = {}  # job_id -> {pdf_path, epub_path, title}


class ConvertRequest(BaseModel):
    url: HttpUrl


class ConvertResponse(BaseModel):
    job_id: str
    title: str
    pdf_url: str
    epub_url: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/convert", response_model=ConvertResponse)
async def convert_url(request: ConvertRequest):
    """
    Convert a webpage URL to PDF and EPUB.
    Returns download URLs for both formats.
    """
    url = str(request.url)

    try:
        converter = WebConverter()
        result = await converter.convert(url)

        # Generate job ID and store file paths
        job_id = str(uuid.uuid4())[:8]
        conversions[job_id] = {
            "pdf_path": result["pdf_path"],
            "epub_path": result["epub_path"],
            "title": result["title"]
        }

        return ConvertResponse(
            job_id=job_id,
            title=result["title"],
            pdf_url=f"/download/{job_id}/pdf",
            epub_url=f"/download/{job_id}/epub"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/convert/stream")
async def convert_url_stream(url: str, viewport_width: int = 430, viewport_height: int = 932, device_id: str = None):
    """
    Convert a webpage URL to PDF and EPUB with Server-Sent Events progress.
    Returns SSE stream with progress updates.

    Args:
        url: The webpage URL to convert
        viewport_width: User's CSS viewport width (default: iPhone 16 Pro Max)
        viewport_height: User's CSS viewport height (default: iPhone 16 Pro Max)
        device_id: Device fingerprint for tracking and rate limiting
    """
    # Check rate limit if device_id provided
    if device_id and not check_rate_limit(device_id, RATE_LIMIT_PER_DAY):
        async def rate_limit_error():
            error_data = json.dumps({
                "progress": 0,
                "message": f"Rate limit exceeded. Maximum {RATE_LIMIT_PER_DAY} conversions per day.",
                "error": True,
                "rate_limited": True
            })
            yield f"data: {error_data}\n\n"
        return StreamingResponse(
            rate_limit_error(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )

    async def event_generator():
        try:
            converter = WebConverter()
            result = None

            async for progress in converter.convert_with_progress(url, viewport_width, viewport_height):
                # Check if this is the final message with result
                if "result" in progress:
                    result = progress["result"]

                # Send SSE event
                event_data = json.dumps({
                    "progress": progress["progress"],
                    "message": progress["message"]
                })
                yield f"data: {event_data}\n\n"

            # Generate job ID and store file paths
            if result:
                job_id = str(uuid.uuid4())[:8]
                conversions[job_id] = {
                    "pdf_path": result["pdf_path"],
                    "epub_path": result["epub_path"],
                    "title": result["title"]
                }

                # Get file sizes
                pdf_size = os.path.getsize(result["pdf_path"]) if os.path.exists(result["pdf_path"]) else None
                epub_size = os.path.getsize(result["epub_path"]) if os.path.exists(result["epub_path"]) else None

                # Log successful conversion to database
                log_conversion(
                    job_id=job_id,
                    url=url,
                    title=result["title"],
                    status="success",
                    viewport_width=viewport_width,
                    viewport_height=viewport_height,
                    page_size=result["page_size"],
                    pdf_path=result["pdf_path"],
                    epub_path=result["epub_path"],
                    pdf_size_bytes=pdf_size,
                    epub_size_bytes=epub_size,
                    conversion_time=result["conversion_time"],
                    device_id=device_id
                )

                # Send final event with download URLs and extra info
                final_data = json.dumps({
                    "progress": 100,
                    "message": "Complete!",
                    "complete": True,
                    "job_id": job_id,
                    "title": result["title"],
                    "pdf_url": f"/download/{job_id}/pdf",
                    "epub_url": f"/download/{job_id}/epub",
                    "source_url": result["source_url"],
                    "viewport_dimensions": result["viewport_dimensions"],
                    "page_size": result["page_size"],
                    "conversion_time": result["conversion_time"]
                })
                yield f"data: {final_data}\n\n"

        except Exception as e:
            # Log failed conversion to database
            job_id = str(uuid.uuid4())[:8]
            log_conversion(
                job_id=job_id,
                url=url,
                status="failed",
                error_message=str(e),
                viewport_width=viewport_width,
                viewport_height=viewport_height,
                device_id=device_id
            )

            error_data = json.dumps({
                "progress": 0,
                "message": str(e),
                "error": True
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for SSE
        }
    )


@app.get("/jobs")
def get_jobs(device_id: str):
    """Get all jobs for a specific device."""
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    jobs = get_device_jobs(device_id)
    remaining = get_rate_limit_remaining(device_id, RATE_LIMIT_PER_DAY)

    # Transform jobs to include download URLs
    for job in jobs:
        job["pdf_url"] = f"/download/{job['job_id']}/pdf" if job.get("pdf_path") else None
        job["epub_url"] = f"/download/{job['job_id']}/epub" if job.get("epub_path") else None
        # Remove file paths from response (not needed by frontend)
        job.pop("pdf_path", None)
        job.pop("epub_path", None)

    return {
        "jobs": jobs,
        "rate_limit": {
            "remaining": remaining,
            "max_per_day": RATE_LIMIT_PER_DAY
        }
    }


@app.get("/download/{job_id}/{format}")
def download_file(job_id: str, format: str):
    """Download converted PDF or EPUB file."""
    # Try in-memory cache first, then fall back to database
    job = conversions.get(job_id)
    if not job:
        job = get_conversion(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Conversion not found")

    if format == "pdf":
        path = job["pdf_path"]
        media_type = "application/pdf"
        filename = f"{job['title']}.pdf"
    elif format == "epub":
        path = job["epub_path"]
        media_type = "application/epub+zip"
        filename = f"{job['title']}.epub"
    else:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'epub'")

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # Track download count
    increment_download(job_id, format)

    return FileResponse(
        path=path,
        media_type=media_type,
        filename=filename
    )


def _make_admin_token() -> str:
    """Create an HMAC token from the admin password for cookie auth."""
    return hmac.new(ADMIN_PASSWORD.encode(), b"readly-admin", hashlib.sha256).hexdigest()


def verify_admin(password: str = None, admin_token: str = None):
    """Verify admin access via password or cookie token."""
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    if admin_token and hmac.compare_digest(admin_token, _make_admin_token()):
        return
    if password and password == ADMIN_PASSWORD:
        return
    raise HTTPException(status_code=401, detail="Invalid password")


@app.get("/admin", response_class=HTMLResponse)
def admin_login_page(admin_token: str = Cookie(None)):
    """Show login form, or redirect to dashboard if already authenticated."""
    if admin_token:
        try:
            verify_admin(admin_token=admin_token)
            return RedirectResponse(url="/admin/dashboard", status_code=302)
        except HTTPException:
            pass

    template = jinja_env.get_template("login.html")
    return HTMLResponse(content=template.render(error=None))


@app.post("/admin/login")
def admin_login(password: str = Form(...)):
    """Authenticate and set session cookie."""
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    if password != ADMIN_PASSWORD:
        template = jinja_env.get_template("login.html")
        return HTMLResponse(content=template.render(error="Invalid password"), status_code=401)

    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key="admin_token",
        value=_make_admin_token(),
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=86400 * 7,  # 7 days
    )
    return response


@app.get("/admin/logout")
def admin_logout():
    """Clear admin session."""
    response = RedirectResponse(url="/admin", status_code=302)
    response.delete_cookie("admin_token")
    return response


@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(admin_token: str = Cookie(None)):
    """Admin dashboard with conversion statistics."""
    verify_admin(admin_token=admin_token)

    template = jinja_env.get_template("dashboard.html")
    html = template.render(
        stats=get_stats(),
        engagement=get_engagement_stats(),
        daily_trend=get_daily_trend(),
        recent=get_recent(limit=50),
        env=ENVIRONMENT
    )
    return HTMLResponse(content=html)


@app.get("/admin/stats")
def admin_stats(password: str = "", admin_token: str = Cookie(None)):
    """API endpoint for conversion statistics and engagement metrics."""
    verify_admin(password=password or None, admin_token=admin_token)

    return {
        "stats": get_stats(),
        "engagement": get_engagement_stats(),
        "top_domains": get_top_domains(),
        "daily_trend": get_daily_trend(),
        "error_breakdown": get_error_breakdown(),
        "recent": get_recent(limit=20)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
