"""
Readly Backend API
Converts webpage URLs to PDF and EPUB formats.
"""

import json
import os
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, HttpUrl

from converter import WebConverter
from database import init_db, log_conversion, get_stats, get_recent, increment_download, get_conversion

# Admin password from environment variable
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

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
async def convert_url_stream(url: str, viewport_width: int = 430, viewport_height: int = 932):
    """
    Convert a webpage URL to PDF and EPUB with Server-Sent Events progress.
    Returns SSE stream with progress updates.

    Args:
        url: The webpage URL to convert
        viewport_width: User's CSS viewport width (default: iPhone 16 Pro Max)
        viewport_height: User's CSS viewport height (default: iPhone 16 Pro Max)
    """
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
                    conversion_time=result["conversion_time"]
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
                viewport_height=viewport_height
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


def verify_admin_password(password: str):
    """Verify the admin password."""
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")


@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(password: str = ""):
    """Admin dashboard with conversion statistics."""
    verify_admin_password(password)

    template = jinja_env.get_template("dashboard.html")
    html = template.render(
        stats=get_stats(),
        recent=get_recent(limit=50),
        env=ENVIRONMENT
    )
    return HTMLResponse(content=html)


@app.get("/admin/stats")
def admin_stats(password: str = ""):
    """API endpoint for conversion statistics."""
    verify_admin_password(password)

    return {
        "stats": get_stats(),
        "recent": get_recent(limit=20)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
