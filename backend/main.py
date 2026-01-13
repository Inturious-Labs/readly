"""
Readly Backend API
Converts webpage URLs to PDF and EPUB formats.
"""

import os
import tempfile
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl

from converter import WebConverter

app = FastAPI(
    title="Readly API",
    description="Convert webpage URLs to PDF and EPUB",
    version="0.1.0"
)

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


@app.get("/download/{job_id}/{format}")
def download_file(job_id: str, format: str):
    """Download converted PDF or EPUB file."""
    if job_id not in conversions:
        raise HTTPException(status_code=404, detail="Conversion not found")

    job = conversions[job_id]

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

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        media_type=media_type,
        filename=filename
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
