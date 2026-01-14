# Readly

Convert WeChat articles to PDF and EPUB for reading on e-readers and any device.

## What it does

Paste a WeChat article URL, get PDF and EPUB files. Simple as that.

- Works with any WeChat Official Account (公众号) article
- Outputs both PDF and EPUB formats
- Optimized for e-ink readers (Kindle, Kobo, etc.)
- No account required

## Architecture

```
Frontend (Vercel/Cloudflare)     Backend (VPS)
┌─────────────────────┐          ┌─────────────────────────┐
│  Static HTML/JS     │  ──────> │  FastAPI + Playwright   │
│  URL input form     │          │  PDF/EPUB generation    │
│  Stripe payment     │          │                         │
└─────────────────────┘          └─────────────────────────┘
```

## Tech Stack

**Frontend:**
- Static HTML/CSS/JS
- Hosted on Vercel or Cloudflare Pages

**Backend:**
- Python + FastAPI
- Playwright (headless browser for WeChat scraping)
- ebooklib (EPUB generation)
- Hosted on any VPS (Linode, DigitalOcean, etc.)

**Payments:**
- Stripe + Alipay

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload --port 8000
```

### Frontend

Just open `frontend/index.html` in a browser, or:

```bash
cd frontend
python3 -m http.server 3000
```

## Deployment

See `deploy/README.md` for server deployment instructions.

## License

MIT
