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
- **Hosting:** Any VPS (Linode, DigitalOcean, etc.)
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

### Phase 1: Core Conversion (Complete)
- [x] FastAPI backend
- [x] Playwright scraping with iPhone emulation
- [x] PDF generation
- [x] EPUB generation
- [x] Simple frontend UI
- [x] Deploy backend to VPS
- [x] Deploy frontend to Vercel
- [x] Test with real WeChat articles

### Phase 2: Payments
- [ ] Stripe integration
- [ ] Alipay payment method
- [ ] Credit/token system (no accounts)
- [ ] Payment → conversion flow

### Phase 3: Polish
- [ ] Error handling improvements
- [ ] Rate limiting
- [ ] Basic analytics
- [x] Domain setup (readly.space)

## Non-Goals (Keep It Simple)

- No user accounts
- No subscription model (initially)
- No ICP/blockchain
- No complex features

## Mobile App Strategy (Future Consideration)

### Why Mobile?
The killer UX is Share Sheet integration: user reads WeChat article → taps Share → selects Readly → converts. This requires a native app; PWAs cannot be share targets on iOS.

### Cross-Platform Options (2026 Analysis)

For a solo builder avoiding separate iOS/Android codebases:

| Approach | Effort | Best For |
|----------|--------|----------|
| **Capacitor** | Low | Wrap existing web app, quick to ship |
| **Flutter** | Medium | Starting fresh, native feel, one codebase |
| **React Native** | Medium | JS developers, large ecosystem |
| **Kotlin Multiplatform** | High | Share logic, native UI (still maturing) |

### Native Feature Support via Capacitor

| Feature | Support |
|---------|---------|
| Share Sheet (iOS/Android) | Yes - plugin available |
| Sign in with Apple | Yes - official plugin |
| Sign in with Google | Yes - official plugin |
| Push Notifications | Yes - official plugin |
| Face ID / Touch ID | Yes - community plugin |
| iCloud Storage | Partial - needs custom Swift |
| Widgets | No - requires native code |

### Recommendation

**Start with Capacitor** when ready for mobile:
1. Reuses existing web frontend
2. Readly's UI is simple (form + progress + downloads)
3. Main native feature needed (Share Sheet) has plugins
4. Ship to both app stores in days, not weeks
5. Can migrate to Flutter/native later if needed

### Decision Criteria for Going Mobile

Consider building mobile app when:
- [ ] Web version has proven demand (consistent paying users)
- [ ] Users request mobile/Share Sheet integration
- [ ] Payment system is working and profitable
- [ ] Have bandwidth for app store review process

## Risks

1. **WeChat blocking:** May need to rotate IPs, use proxies, or adjust scraping approach
2. **Content changes:** WeChat page structure may change, requiring scraper updates
3. **Low conversion quality:** Some articles may not convert well (images, formatting)

## Success Metrics

- Works reliably for 80%+ of WeChat articles
- Positive unit economics (revenue > Stripe fees + hosting)
- Low maintenance (< 2 hours/month)
