# Readly

Transform WeChat Official Account articles into EPUB files for reading on e-readers and devices outside the WeChat ecosystem.

## Overview

Readly is a WeChat article converter that enables you to read your favorite WeChat content on Kindle, Kobo, Apple Books, and other e-readers. Currently available as a CLI tool, with plans to evolve into a full web service.

### Current Status

**Available Now (CLI Tool):**
- Convert WeChat articles to EPUB and Markdown formats
- Extract article metadata (title, author, publication date)
- Clean formatting optimized for e-readers
- Full Chinese text support
- Command-line interface for quick conversions

**Future Vision:**
- Web-based service with user-friendly interface
- User accounts and personal library management
- Batch processing and conversion history
- Blockchain-based hosting on Internet Computer (ICP)
- Subscription tiers and monetization features

See [PLAN.md](PLAN.md) for the complete product roadmap.

## Features

- 🔗 Extract articles directly from WeChat URLs
- 📱 Support for EPUB and Markdown formats
- 🎨 Clean formatting with proper styling
- 🇨🇳 Full Chinese text support
- 📚 Compatible with Kindle, Kobo, Apple Books, and most e-readers
- ⚡ Fast CLI tool for instant conversions

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/readly.git
cd readly
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Convert a WeChat article to both EPUB and Markdown formats:

```bash
python wechat_scraper.py "https://mp.weixin.qq.com/s/YOUR_ARTICLE_ID"
```

### Specify Output Format

Convert to EPUB only:
```bash
python wechat_scraper.py --format epub "https://mp.weixin.qq.com/s/YOUR_ARTICLE_ID"
```

Convert to Markdown only:
```bash
python wechat_scraper.py --format markdown "https://mp.weixin.qq.com/s/YOUR_ARTICLE_ID"
```

### Custom Output Directory

```bash
python wechat_scraper.py --output my_articles "https://mp.weixin.qq.com/s/YOUR_ARTICLE_ID"
```

## Command Line Options

- `url`: WeChat article URL (required)
- `--format`: Output format - `epub`, `markdown`, or `both` (default: `both`)
- `--output`: Output directory (default: `output`)
- `--help`: Show help message

## Output Formats

### EPUB
- Standard eBook format compatible with most readers
- Includes proper metadata (title, author, date)
- Clean typography and styling optimized for e-ink displays
- Chapter navigation and table of contents

### Markdown
- Plain text format with formatting preserved
- Compatible with various markdown viewers
- Easy to edit and convert to other formats
- Portable and future-proof

## Example

```bash
$ python wechat_scraper.py "https://mp.weixin.qq.com/s/HG4pZCv0-w6hj5ctT20kOQ"

Fetching article from: https://mp.weixin.qq.com/s/HG4pZCv0-w6hj5ctT20kOQ
Successfully fetched article HTML
Extracted article: OpenAI与英伟达、甲骨文的千亿合作，都在打什么算盘？
Markdown saved to: output/OpenAI与英伟达、甲骨文的千亿合作，都在打什么算盘？.md
EPUB saved to: output/OpenAI与英伟达、甲骨文的千亿合作，都在打什么算盘？.epub

Conversion completed!
Title: OpenAI与英伟达、甲骨文的千亿合作，都在打什么算盘？
Author: 量子位
Date: 2024-09-28
```

## Supported eBook Readers

The generated EPUB files work with:
- Kindle (all models)
- Kobo e-readers
- Apple Books
- Adobe Digital Editions
- Calibre
- FBReader
- Moon+ Reader
- KyBook
- And most other EPUB 3.0-compatible readers

## Requirements

- Python 3.7+
- Internet connection
- Dependencies listed in `requirements.txt`

## Current Limitations

- Only supports publicly accessible WeChat articles
- Some articles may have anti-scraping protection
- Image downloading is not currently supported
- Rate limiting may apply for bulk downloads
- CLI interface only (web interface planned)

## Roadmap

### Phase 1: Enhanced CLI (Current)
- ✅ Basic EPUB and Markdown conversion
- 🔄 Image downloading and optimization
- 🔄 Better anti-scraping handling with Playwright
- 🔄 Batch processing capabilities

### Phase 2: Web Service MVP
- Web interface with URL input
- User accounts via Internet Identity
- Conversion history and personal library
- Responsive design for mobile and desktop

### Phase 3: Premium Features
- Subscription tiers (freemium model)
- Cloud storage for library
- Advanced customization options
- API access for developers

See [PLAN.md](PLAN.md) for detailed feature specifications and technical architecture.

## Technical Architecture

**Current Stack:**
- Python 3.7+
- requests (HTTP client)
- BeautifulSoup4 (HTML parsing)
- ebooklib (EPUB generation)
- lxml (XML/HTML processing)

**Planned Stack:**
- Frontend: React/Svelte + Tailwind CSS on ICP
- Backend: Motoko/Rust on ICP canisters
- Scraping Service: Python (FastAPI + Playwright) on Railway
- Storage: ICP Asset Canisters
- Auth: Internet Identity

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for personal use and educational purposes. Please respect copyright and terms of service of WeChat and article authors. Use responsibly and ensure you have the right to convert and store the content you're accessing.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built to solve a real problem:** WeChat articles are locked within the app ecosystem. Readly liberates your content so you can read it anywhere, on any device.
