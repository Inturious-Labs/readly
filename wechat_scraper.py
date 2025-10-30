#!/usr/bin/env python3
"""
WeChat Article Scraper and eBook Converter
Scrapes WeChat articles and converts them to ebook formats
"""

import requests
import re
import os
from bs4 import BeautifulSoup
import argparse
import sys
from datetime import datetime
from ebooklib import epub

def fetch_wechat_article(url):
    """Fetch WeChat article content"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        print(f"Fetching article from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print("Successfully fetched article HTML")
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching article: {e}")
        return None

def extract_article_content(html):
    """Extract article content from WeChat HTML"""
    soup = BeautifulSoup(html, 'html.parser')

    # Extract title
    title_elem = soup.find('h1', {'id': 'activity-name'}) or soup.find('h1', class_='rich_media_title')
    title = title_elem.get_text().strip() if title_elem else "Untitled"

    # Extract author
    author_elem = soup.find('span', class_='rich_media_meta_text') or soup.find('a', class_='account_name')
    author = author_elem.get_text().strip() if author_elem else "Unknown Author"

    # Extract publication date
    date_elem = soup.find('em', {'id': 'publish_time'}) or soup.find('span', class_='rich_media_meta_text')
    pub_date = date_elem.get_text().strip() if date_elem else datetime.now().strftime('%Y-%m-%d')

    # Extract main content
    content_elem = soup.find('div', {'id': 'js_content'}) or soup.find('div', class_='rich_media_content')

    if not content_elem:
        print("Could not find main content element")
        return None

    # Clean up content and preserve formatting
    content_text = ""
    for element in content_elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']):
        text = element.get_text().strip()
        if text:
            if element.name.startswith('h'):
                level = int(element.name[1])
                content_text += f"\n\n{'#' * (level + 1)} {text}\n\n"
            elif element.name == 'blockquote':
                content_text += f"\n> {text}\n\n"
            else:
                content_text += f"{text}\n\n"

    print(f"Extracted article: {title}")
    return {
        'title': title,
        'author': author,
        'date': pub_date,
        'content': content_text.strip(),
        'url': None
    }

def create_markdown(article_data, output_dir="output"):
    """Convert article to Markdown format"""
    os.makedirs(output_dir, exist_ok=True)

    markdown = f"""# {article_data['title']}

**Author:** {article_data['author']}
**Date:** {article_data['date']}

---

{article_data['content']}
"""

    # Create safe filename
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', article_data['title'])
    filename = f"{safe_title}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Markdown saved to: {filepath}")
    return filepath

def create_epub(article_data, output_dir="output"):
    """Create EPUB ebook from article data"""
    os.makedirs(output_dir, exist_ok=True)

    # Create EPUB book
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('wechat_article')
    book.set_title(article_data['title'])
    book.set_language('zh')
    book.add_author(article_data['author'])

    # Create chapter
    content_html = f"""<h1>{article_data['title']}</h1>
<p><strong>Author:</strong> {article_data['author']}</p>
<p><strong>Date:</strong> {article_data['date']}</p>
<hr/>
<div class="content">
{article_data['content'].replace('\n\n', '</p><p>').replace('\n', '<br/>')}
</div>"""

    chapter = epub.EpubHtml(title=article_data['title'], file_name='chapter_01.xhtml', lang='zh')
    chapter.content = f"""<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.1//EN' 'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>{article_data['title']}</title>
<style>
body {{ font-family: serif; line-height: 1.6; margin: 2em; }}
h1 {{ color: #333; border-bottom: 2px solid #333; }}
h2, h3, h4 {{ color: #666; }}
p {{ margin-bottom: 1em; }}
hr {{ margin: 2em 0; }}
blockquote {{ border-left: 3px solid #ccc; padding-left: 1em; margin: 1em 0; }}
</style>
</head>
<body>
{content_html}
</body>
</html>"""

    # Add chapter to book
    book.add_item(chapter)

    # Create table of contents
    book.toc = (epub.Link("chapter_01.xhtml", article_data['title'], "chapter_01"),)

    # Add navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = ['nav', chapter]

    # Create safe filename
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', article_data['title'])
    filename = f"{safe_title}.epub"
    filepath = os.path.join(output_dir, filename)

    # Write EPUB file
    epub.write_epub(filepath, book, {})

    print(f"EPUB saved to: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Convert WeChat articles to ebook formats')
    parser.add_argument('url', help='WeChat article URL')
    parser.add_argument('--format', choices=['markdown', 'epub', 'both'], default='both',
                       help='Output format (default: both)')
    parser.add_argument('--output', '-o', default='output',
                       help='Output directory (default: output)')

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith('https://mp.weixin.qq.com/'):
        print("Error: URL must be a WeChat article (mp.weixin.qq.com)")
        sys.exit(1)

    # Fetch HTML
    html = fetch_wechat_article(args.url)
    if not html:
        print("Failed to fetch article")
        sys.exit(1)

    # Extract content
    article_data = extract_article_content(html)
    if not article_data:
        print("Failed to extract article content")
        sys.exit(1)

    article_data['url'] = args.url

    # Generate output files
    if args.format in ['markdown', 'both']:
        create_markdown(article_data, args.output)

    if args.format in ['epub', 'both']:
        create_epub(article_data, args.output)

    print(f"\nConversion completed!")
    print(f"Title: {article_data['title']}")
    print(f"Author: {article_data['author']}")
    print(f"Date: {article_data['date']}")

if __name__ == "__main__":
    main()