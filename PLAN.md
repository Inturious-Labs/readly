# Readly - Product Plan

## Vision

A simple, low-maintenance utility that converts WeChat articles to PDF/EPUB. Pay-per-use model. No accounts, no complexity.

## Problem

WeChat articles are locked in the WeChat app. Users want to:
- Read on e-ink readers (Kindle, Kobo)
- Archive articles for offline access
- Read without the WeChat app

## Solution

Website where users paste a WeChat URL and get PDF + EPUB downloads.

## Business Model

**Pricing:** Pay-per-conversion via Stripe + Alipay

Exact pricing TBD (need to balance Stripe fees with user value). Options:
- Credit packs (e.g., 10 conversions for ¥10)
- Per-conversion (e.g., ¥5 per conversion)

**Target:** Small, profitable, low-maintenance cash-flow business.

## Technical Architecture

### Frontend
- **Stack:** Static HTML/CSS/JS
- **Hosting:** Vercel or Cloudflare Pages (free tier)
- **Features:**
  - URL input form
  - Stripe checkout integration
  - Download links for PDF/EPUB

### Backend
- **Stack:** Python + FastAPI
- **Hosting:** Existing Linode server (Singapore)
- **Features:**
  - `/convert` endpoint
  - Playwright for WeChat scraping (iPhone emulation)
  - PDF generation (via Playwright)
  - EPUB generation (via ebooklib)

### Payments
- **Provider:** Stripe
- **Methods:** Alipay (primary for Chinese users)
- **Flow:** Pay first, then convert

## MVP Scope

### Phase 1: Core Conversion (Current)
- [x] FastAPI backend
- [x] Playwright scraping with iPhone emulation
- [x] PDF generation
- [x] EPUB generation
- [x] Simple frontend UI
- [ ] Deploy backend to Linode
- [ ] Deploy frontend to Vercel/Cloudflare
- [ ] Test with real WeChat articles

### Phase 2: Payments
- [ ] Stripe integration
- [ ] Alipay payment method
- [ ] Credit/token system (no accounts)
- [ ] Payment → conversion flow

### Phase 3: Polish
- [ ] Error handling improvements
- [ ] Rate limiting
- [ ] Basic analytics
- [ ] Domain setup (readly.xxx)

## Non-Goals (Keep It Simple)

- No user accounts
- No subscription model (initially)
- No ICP/blockchain
- No complex features
- No mobile app

## Risks

1. **WeChat blocking:** May need to rotate IPs, use proxies, or adjust scraping approach
2. **Content changes:** WeChat page structure may change, requiring scraper updates
3. **Low conversion quality:** Some articles may not convert well (images, formatting)

## Success Metrics

- Works reliably for 80%+ of WeChat articles
- Positive unit economics (revenue > Stripe fees + hosting)
- Low maintenance (< 2 hours/month)
