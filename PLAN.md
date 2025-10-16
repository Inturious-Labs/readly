# Readly - Product Requirements Document (PRD)

## Executive Summary

Readly is a web service that transforms WeChat Official Account articles into EPUB files, enabling users to save and read high-quality Chinese content on e-ink readers and other devices outside the WeChat ecosystem.

---

## 1. Problem Statement

### Current Pain Points
1. **Content Portability**: WeChat articles can only be favorited within WeChat, with no way to access them outside the app
2. **Reading Experience**: Long-form, in-depth articles are difficult to consume on mobile devices within the WeChat interface
3. **Content Preservation**: Users have no reliable way to archive valuable content for long-term reference
4. **Device Flexibility**: No ability to read WeChat articles on preferred devices (e-ink readers, tablets, etc.)

### User Impact
- Chinese readers miss out on optimal reading experiences for quality long-form content
- Valuable articles risk being lost if the original publisher removes them
- Users are locked into the WeChat ecosystem for content consumption

---

## 2. User Personas

### Primary Persona: The Avid Reader
- **Demographics**: 25-45 years old, urban professionals, knowledge workers
- **Behavior**: Regularly follows 10+ WeChat Official Accounts, encounters 2-5 valuable long-form articles per week
- **Goals**: Archive quality content, read on e-ink devices, maintain a personal knowledge library
- **Tech Savvy**: Medium to high, comfortable with web services and file management

### Secondary Persona: The Researcher/Student
- **Demographics**: 20-35 years old, graduate students, academics, journalists
- **Behavior**: Collects WeChat articles for research and reference
- **Goals**: Organize content by topic, annotate on e-readers, cite sources
- **Tech Savvy**: High, familiar with digital research tools

---

## 3. Core Value Proposition

**"Read WeChat articles anywhere, anytime, on any device - especially your favorite e-reader."**

### Key Benefits
- ✅ One-click conversion from WeChat article URL to EPUB
- ✅ Preserve original formatting, images, and structure
- ✅ Read on Kindle, Kobo, iPad, or any EPUB-compatible device
- ✅ Build a personal library of valuable Chinese content
- ✅ Offline reading without WeChat dependency

---

## 4. MVP Feature Scope

### Phase 1: Core Functionality (MVP)
**Target: 2-3 weeks development**

#### Must-Have Features
1. **URL Input & Conversion**
   - Simple web interface with URL input field
   - Support for standard WeChat article URLs (`mp.weixin.qq.com`)
   - One-click conversion to EPUB
   - Download EPUB file directly

2. **Content Extraction**
   - Article title, author, publish date
   - Full text content with formatting (paragraphs, bold, italic)
   - Embedded images (with proper sizing for e-readers)
   - Basic HTML to EPUB conversion

3. **EPUB Generation**
   - Standard EPUB 3.0 format
   - Proper metadata (title, author, date)
   - Table of contents (if article has headers)
   - Optimized for e-ink displays (appropriate image sizing, clean typography)

4. **Basic User Experience**
   - Responsive web interface (mobile + desktop)
   - Loading indicator during conversion
   - Error handling (invalid URL, article unavailable, etc.)
   - Simple success/download page

#### Nice-to-Have (MVP+)
- Preview EPUB contents before download
- Basic usage statistics tracking
- Email delivery option for EPUB file

### Phase 2: Enhanced Features (Post-MVP)
**Target: 1-2 months after MVP**

1. **User Accounts**
   - Registration and login (Internet Identity integration)
   - Conversion history
   - Personal library of converted articles
   - Re-download previously converted articles

2. **Batch Processing**
   - Convert multiple URLs at once
   - Upload list of URLs (CSV, TXT)
   - Create collections/compilations

3. **Quality Improvements**
   - Better image handling (optimization, compression)
   - Custom EPUB styling options
   - Support for article series (multi-part articles)

4. **Content Organization**
   - Tags and categories
   - Search within library
   - Export library as ZIP

### Phase 3: Monetization & Scale (3-6 months)
**Target: Sustainable business model**

1. **Payment Integration**
   - Pay-per-article model (¥1-2 per conversion)
   - Subscription tiers (monthly/yearly)
   - Credit packages (10, 50, 100 conversions)
   - ICP/CKBTC payment integration
   - WeChat Pay + Alipay integration

2. **Premium Features**
   - Unlimited conversions (subscription)
   - Cloud storage for library
   - Advanced formatting options
   - Priority processing
   - API access for power users

3. **Sharing & Social**
   - Share converted EPUB with others
   - Public library of popular articles
   - Follow favorite Official Accounts

---

## 5. Technical Architecture

### High-Level Stack (Internet Computer)

#### Frontend Canister
- **Framework**: React or Svelte (optimized for ICP)
- **Styling**: Tailwind CSS
- **Assets**: Hosted directly in frontend canister
- **Routing**: Client-side routing with History API
- **State Management**: React Context or Zustand

#### Backend Canister
- **Language**: Motoko or Rust
- **Core Functions**:
  - URL validation and queuing
  - Conversion job management
  - User authentication (Internet Identity)
  - File storage coordination
  - Usage tracking and limits

#### External Services (via HTTPS Outcalls)
- **Web Scraping Service (Python)**:
  - Python service hosted on Railway
  - **Tech Stack**: FastAPI + Playwright + BeautifulSoup4 + ebooklib
  - **Functions**:
    - Headless browser rendering with Playwright (handles JavaScript, anti-bot detection)
    - HTML parsing with BeautifulSoup4 (extract article content, images, metadata)
    - Image optimization (resize/compress for e-readers)
    - EPUB generation with ebooklib
  - Exposes REST API for canister to call: `POST /convert`
  - **Why external**: Headless browsers are too resource-intensive for canisters (require Chrome binary, high memory/CPU)
  - **Why Python**: BeautifulSoup4 proven in The Sunday Blender project; mature ecosystem for web scraping and EPUB generation

#### Storage Architecture
1. **Generated EPUBs**:
   - Store in backend canister stable memory (for small files)
   - Or use ICP asset canister for larger files
   - Serve via canister HTTP interface

2. **User Data**:
   - Stable structures (StableBTreeMap) for user records
   - Conversion history and metadata
   - User preferences and quotas

3. **Temporary Data**:
   - Job queue in canister heap memory
   - Rate limiting counters

#### Architecture Diagram
```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ Submit WeChat URL
         ↓
┌─────────────────┐
│ Frontend        │ (React/Svelte + Tailwind CSS)
│ Canister        │ (Asset canister)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Backend         │ (Motoko/Rust)
│ Canister        │ - Auth (Internet Identity)
└────┬───────┬────┘  - Rate limiting
     │       │        - Payments
     │       │
     │       └──────→ ┌──────────────┐
     │                │ Asset        │
     │                │ Canister     │ (EPUB storage)
     │                └──────────────┘
     │
     │ HTTPS Outcall
     ↓
┌─────────────────────────┐
│ Python Scraper Service  │ (Railway - $5-10/month)
│ ├─ FastAPI             │
│ ├─ Playwright          │ (Headless Chrome)
│ ├─ BeautifulSoup4      │ (HTML parsing)
│ ├─ ebooklib            │ (EPUB generation)
│ └─ Pillow              │ (Image optimization)
└────────┬────────────────┘
         │
         ↓
    ┌────────────┐
    │  WeChat    │
    │  Servers   │
    └────────────┘
```

### Technical Workflow

1. **User submits WeChat URL**
   - Frontend validates URL format (must be `mp.weixin.qq.com`)
   - Sends to backend canister

2. **Backend canister processes request**
   - Check user quota/authentication via Internet Identity
   - Generate unique job ID
   - Make HTTPS outcall to Python scraper service: `POST https://readly-scraper.railway.app/convert`

3. **Python scraper service processes article**
   - **Step 3a**: Playwright launches headless Chrome
   - **Step 3b**: Navigate to WeChat URL with proper User-Agent (mimics WeChat browser)
   - **Step 3c**: Wait for JavaScript to execute and content to load
   - **Step 3d**: BeautifulSoup4 parses rendered HTML
   - **Step 3e**: Extract: title, author, date, content, images
   - **Step 3f**: Download and optimize images (resize for e-ink, compress)
   - **Step 3g**: Generate EPUB file with ebooklib
   - **Step 3h**: Return EPUB binary to canister (or upload to temporary storage and return URL)

4. **Backend canister receives EPUB**
   - Store EPUB in asset canister
   - Generate permanent download URL
   - Record conversion in user's history
   - Update usage quota

5. **Serve EPUB to user**
   - Return download link to frontend
   - User clicks to download EPUB file
   - EPUB served from asset canister

### Key Technical Challenges

1. **HTTPS Outcalls Quota**
   - ICP canisters have cycle costs for outcalls
   - **Solution**: Optimize outcall frequency, cache results, use efficient scraper API

2. **Canister Storage Limits**
   - Stable memory has size limits
   - **Solution**: Use asset canister for EPUBs, implement cleanup policy for old files

3. **WeChat Content Extraction**
   - WeChat uses JavaScript for content rendering (requires headless browser)
   - WeChat has anti-bot detection (returns verification/CAPTCHA pages)
   - Images are lazy-loaded and may have CDN access restrictions
   - **Solution**:
     - Playwright with proper User-Agent headers (mimic WeChat in-app browser)
     - Wait for full page load before extraction
     - Residential proxies if IP-based blocking occurs
     - Handle CAPTCHA responses gracefully

4. **EPUB Generation**
   - Need reliable EPUB library that handles Chinese content well
   - Images must be properly embedded and sized for e-readers
   - **Solution**:
     - Use Python's `ebooklib` (mature, EPUB 3.0 compliant)
     - Similar approach to The Sunday Blender's PDF generation
     - Optimize images with Pillow (~800px width for e-ink displays)

5. **Rate Limiting & Abuse**
   - Prevent users from overwhelming system
   - **Solution**: Per-principal rate limits, CAPTCHA for high volume (hCaptcha/Turnstile)

6. **Payment Integration**
   - Need to accept payments for conversions
   - **Solution**:
     - Phase 1: ICP/CKBTC via Internet Identity
     - Phase 2: Integrate WeChat Pay/Alipay via external payment gateway

### Technology Stack Summary

| Component | Technology | Hosting |
|-----------|-----------|---------|
| Frontend | React/Svelte + Tailwind CSS | ICP Frontend Canister |
| Backend API | Motoko or Rust | ICP Backend Canister |
| EPUB Storage | Binary data | ICP Asset Canister |
| User Data | Stable structures | ICP Backend Canister (stable memory) |
| **Scraper Service** | **Python + FastAPI** | **Railway ($5-10/month)** |
| **Headless Browser** | **Playwright (Chromium)** | **Railway (same service)** |
| **HTML Parsing** | **BeautifulSoup4** | **Railway (same service)** |
| **EPUB Generation** | **ebooklib** | **Railway (same service)** |
| **Image Processing** | **Pillow** | **Railway (same service)** |
| Authentication | Internet Identity | ICP |
| Payments (Phase 3) | ICP/CKBTC, WeChat Pay API | ICP + external gateway |

**Python Scraper Service Stack (All-in-One):**
```python
# requirements.txt
fastapi==0.104.1
playwright==1.40.0
beautifulsoup4==4.12.2
ebooklib==0.18
Pillow==10.1.0
uvicorn==0.24.0
requests==2.31.0
```

### Development Approach

**Phase 1 (MVP) - Simplest Path:**
1. **Frontend canister**: Basic React UI with URL input form
2. **Backend canister**: Motoko with HTTPS outcalls to Python service
3. **Python scraper service** (Railway): All-in-one service
   - FastAPI endpoint: `POST /convert`
   - Playwright for rendering
   - BeautifulSoup4 for parsing
   - ebooklib for EPUB generation
   - Returns EPUB binary or download URL
4. **Storage**: Backend canister returns EPUB directly to user (small files < 2MB)

**Phase 2 (Scale):**
1. Separate asset canister for EPUB storage (for larger files)
2. User authentication with Internet Identity
3. Add stable storage for user history and library
4. Implement caching in Python service (Redis/in-memory)

**Phase 3 (Production):**
1. Optimize HTTPS outcalls (reduce frequency, batch if possible)
2. Add health monitoring for Python service
3. Implement payment integration (ICP/CKBTC)
4. Consider multi-canister architecture if traffic grows
5. Add queue system for Python service (Celery + Redis) if load increases

### Python Scraper Service - Example Code Structure

```python
# main.py - FastAPI application
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from ebooklib import epub
import asyncio

app = FastAPI()

class ConvertRequest(BaseModel):
    url: str

@app.post("/convert")
async def convert_article(request: ConvertRequest):
    """
    Main endpoint called by IC canister
    Returns EPUB file as binary or upload URL
    """
    try:
        # Step 1: Scrape article with Playwright
        html = await scrape_wechat_article(request.url)

        # Step 2: Parse content with BeautifulSoup
        article_data = parse_article(html)

        # Step 3: Generate EPUB
        epub_file = generate_epub(article_data)

        # Step 4: Return EPUB (as base64 or upload to temp storage)
        return {
            "success": True,
            "epub_data": epub_file,  # or "epub_url" if uploaded
            "metadata": article_data["metadata"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def scrape_wechat_article(url: str) -> str:
    """Use Playwright to render WeChat article"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Mimic WeChat browser
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0...) MicroMessenger/8.0.38'
        })

        await page.goto(url)
        await page.wait_for_load_state('networkidle')

        html = await page.content()
        await browser.close()
        return html

def parse_article(html: str) -> dict:
    """Extract article content with BeautifulSoup"""
    soup = BeautifulSoup(html, 'html.parser')

    # Extract metadata and content
    # (Similar to what you did in The Sunday Blender!)
    title = soup.find('h1', id='activity-name').text
    author = soup.find('span', id='js_name').text
    content = soup.find('div', id='js_content')

    # Extract and process images
    images = []
    for img in content.find_all('img'):
        img_url = img.get('data-src') or img.get('src')
        images.append(img_url)

    return {
        "metadata": {"title": title, "author": author},
        "content": str(content),
        "images": images
    }

def generate_epub(article_data: dict) -> bytes:
    """Generate EPUB file with ebooklib"""
    book = epub.EpubBook()

    # Set metadata
    book.set_title(article_data["metadata"]["title"])
    book.add_author(article_data["metadata"]["author"])

    # Create chapter
    chapter = epub.EpubHtml(
        title='Article',
        file_name='article.xhtml',
        content=article_data["content"]
    )
    book.add_item(chapter)

    # Add images (download and embed)
    # ... image processing code ...

    # Generate EPUB binary
    epub_bytes = epub.write_epub(book, None)
    return epub_bytes
```

**Deployment to Railway:**
```bash
# In readly-scraper/ directory
railway init
railway up
# Railway auto-detects Python + requirements.txt and deploys!
```

---

## 6. Feature Roadmap

### Month 1: MVP Development
- [ ] Week 1: Project setup, canister scaffolding, basic UI, external scraper service setup
- [ ] Week 2: WeChat scraper implementation, HTTPS outcall integration
- [ ] Week 3: EPUB generation pipeline, testing on various e-readers
- [ ] Week 4: Error handling, UX polish, deployment to IC mainnet

### Month 2: Beta Testing & Iteration
- [ ] Week 5-6: Closed beta with 20-30 users
- [ ] Week 7: Fix bugs, improve conversion quality, optimize cycles usage
- [ ] Week 8: Public launch, marketing to target communities

### Month 3-4: User Accounts & Library
- [ ] Internet Identity integration
- [ ] Conversion history and library
- [ ] Re-download feature
- [ ] Asset canister for EPUB storage
- [ ] Usage analytics and metrics

### Month 5-6: Monetization
- [ ] ICP/CKBTC payment integration
- [ ] Implement tier system (free, pay-per-use, subscription)
- [ ] Premium features development
- [ ] Customer support system

### Month 7-12: Growth & Optimization
- [ ] Batch processing
- [ ] WeChat Pay/Alipay integration
- [ ] API for developers
- [ ] Partnership with e-reader communities/forums
- [ ] SEO and content marketing

---

## 7. Business Model

### Revenue Streams

#### Option A: Pay-Per-Article
- **Price**: ¥1-2 per conversion (~$0.15-0.30 USD)
- **ICP equivalent**: ~0.001-0.002 ICP (variable based on ICP price)
- **Pros**: Low barrier to entry, fair value exchange
- **Cons**: May limit usage, transaction friction

#### Option B: Freemium + Subscription (Recommended)
- **Free Tier**: 3 conversions/month
- **Basic Tier**: ¥9.9/month or 0.01 ICP/month (30 conversions)
- **Pro Tier**: ¥29.9/month or 0.03 ICP/month (unlimited conversions + premium features)
- **Annual Discount**: 20% off

#### Option C: Credit System
- **Starter Pack**: ¥9.9 or 0.01 ICP for 10 credits
- **Value Pack**: ¥39.9 or 0.04 ICP for 50 credits
- **Power Pack**: ¥79.9 or 0.08 ICP for 120 credits
- 1 credit = 1 conversion

**Recommendation**: Start with **Option B** (Freemium + Subscription) for MVP. It balances user acquisition (free tier) with predictable revenue (subscriptions). Add Option C (credits) in Phase 3 for users who prefer one-time purchases.

### Target Metrics (Year 1)
- **Users**: 5,000 registered users
- **Conversion Rate**: 10% free → paid
- **ARPU**: ¥15/month (average across tiers)
- **Monthly Revenue**: ¥7,500 at 500 paying users
- **Goal**: Break-even by Month 6, profitability by Month 12

---

## 8. Success Metrics (KPIs)

### Acquisition
- Weekly active users (WAU)
- New user signups
- Traffic sources

### Engagement
- Conversions per user
- Return usage rate (% users who convert 2+ articles)
- Average time on site

### Quality
- Successful conversion rate (% of attempts that succeed)
- EPUB download completion rate
- User-reported issues per 100 conversions

### Revenue
- Free-to-paid conversion rate
- Monthly Recurring Revenue (MRR)
- Average Revenue Per User (ARPU)
- Churn rate

### Retention
- Day 7, Day 30 retention rates
- Monthly active users (MAU) / WAU ratio

### Technical (ICP-specific)
- Cycle consumption per conversion
- Average HTTPS outcall cost
- Canister storage usage
- Response time / latency

---

## 9. Risks & Mitigations

### Legal & Compliance
**Risk**: Copyright concerns from Official Account owners
- **Mitigation**: Add disclaimer that users should only convert content they have rights to access; include attribution in EPUB; provide DMCA takedown process

**Risk**: WeChat blocking or rate-limiting our service
- **Mitigation**: Implement respectful scraping (delays, user-agent rotation); use residential proxies if needed; have backup extraction methods

### Technical
**Risk**: WeChat changes article page structure
- **Mitigation**: Modular scraper design, automated tests, monitoring for extraction failures

**Risk**: High HTTPS outcall costs on ICP
- **Mitigation**: Optimize outcall frequency, implement caching, monitor cycle consumption

**Risk**: Canister storage limitations
- **Mitigation**: Implement file cleanup policies, use asset canisters efficiently, expire old EPUBs after 30 days

**Risk**: Poor EPUB quality across devices
- **Mitigation**: Extensive testing on popular e-readers, user feedback loop, iterative improvements

**Risk**: External scraper service downtime
- **Mitigation**: Health checks, fallback mechanisms, monitoring and alerts

### Business
**Risk**: Insufficient user willingness to pay
- **Mitigation**: Generous free tier to build habit, clear value demonstration, alternative revenue (ads, affiliates)

**Risk**: Niche market too small
- **Mitigation**: Expand to other content sources (Zhihu, Douban, WeChat moments), explore B2B use cases

---

## 10. Go-to-Market Strategy

### Target Channels
1. **Xiaohongshu (小红书)**: Share "reading hacks" and productivity tips
2. **Douban Reading Groups**: Engage with book lovers and knowledge workers
3. **Weibo**: Technology and productivity influencers
4. **WeChat Groups**: Target e-reader enthusiast communities
5. **Zhihu**: Answer questions about e-reading, knowledge management

### Content Marketing
- Blog posts: "How to build your personal WeChat article library"
- Tutorials: "Best e-readers for Chinese content in 2024"
- Use cases: "Research workflow with Readly + Notion"

### Launch Strategy
1. **Pre-launch** (2 weeks): Build landing page, collect email waitlist
2. **Beta** (2 weeks): Invite 50 beta users from target communities
3. **Soft Launch** (1 month): Limited promotion, gather feedback
4. **Public Launch**: Coordinated posts across all channels, partnerships with tech blogs

---

## 11. Future Considerations

### Potential Expansions
- Support for other Chinese content platforms (Zhihu, Jianshu, Douban)
- Browser extension for one-click conversion
- Integration with read-it-later services (Pocket, Instapaper equivalents)
- AI-powered content summarization and highlights
- Export to other formats (PDF, MOBI, AZW3)
- English content support for international Chinese readers

### Partnerships
- E-reader manufacturers (Kindle, Kobo, Boox)
- Knowledge management tools (Notion, Obsidian Chinese communities)
- Content creators (offer official EPUB exports for premium content)

---

## 12. Development Priorities (Summary)

**Week 1-4 (MVP)**: Core conversion functionality
- Basic React frontend on ICP
- Motoko backend with HTTPS outcalls
- **Python scraper service on Railway** (FastAPI + Playwright + BeautifulSoup4 + ebooklib)
- URL input → scrape → generate EPUB → download
- Works reliably for 80%+ of WeChat articles
- Handles WeChat's anti-bot detection with proper User-Agent

**Month 2-3 (Enhanced MVP)**: User experience improvements
- Internet Identity authentication
- Conversion history and library
- Better error handling and edge case support
- Quality improvements based on beta feedback

**Month 4-6 (Monetization)**: Business sustainability
- ICP/CKBTC payment integration
- Tiered feature access
- Analytics and optimization
- Cycle cost optimization

**Month 7-12 (Growth)**: Scale and expand
- WeChat Pay/Alipay integration
- Additional features (batch, API, etc.)
- Marketing and user acquisition
- Explore new content sources

---

## Appendix: Competitive Landscape

### Direct Competitors
- **WeChat's built-in "Favorites"**: Limited to app, no export
- **InstaPaper / Pocket**: Don't support WeChat articles well
- **Manual copy-paste methods**: Tedious, loses formatting

### Indirect Competitors
- **Screenshot tools**: Poor reading experience, no text selection
- **Web clippers (Notion, Evernote)**: Doesn't solve e-reader use case

### Competitive Advantage
- **Specialized**: Purpose-built for WeChat articles
- **EPUB Focus**: Optimized for e-reader experience
- **Chinese-first**: Proper character encoding, font support
- **Simple**: One-click workflow, no complex setup
- **Web3 Native**: Decentralized hosting, ICP payments, censorship-resistant
