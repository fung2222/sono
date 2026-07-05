#!/usr/bin/env python3
"""
gnews_hk_search.py - Google News RSS 搜尋香港繁中新聞

完全免費、零 API key、零 rate limit。
支援 topic 列表，回傳每條新聞 {title, pub, link, source, desc}。
"""
import urllib.parse
import urllib.request
import re
import xml.etree.ElementTree as ET
from html import unescape
from datetime import datetime, timedelta
import time


# 4 主題最佳 queries (HK 繁中新聞搜到率最高)
TOPIC_QUERIES = {
    "ai": "AI 人工智能",
    "space": "太空 NASA SpaceX",
    "ufo": "UFO 外星人",
    "paranormal": "靈異事件",
}

# 備用 queries (fallback 順序)
FALLBACK_QUERIES = {
    "ai": ["人工智能 科技", "ChatGPT 香港", "機器學習"],
    "space": ["太空探索", "NASA 太空", "SpaceX 火箭"],
    "ufo": ["UAP 幽浮", "外星生命", "五角大樓 UFO"],
    "paranormal": ["都市傳說", "鬼故事", "超自然現象"],
}

# Google News RSS base
BASE_URL = "https://news.google.com/rss/search"


def fetch_rss(query, max_results=100, retries=2):
    """Fetch a single RSS feed."""
    url = f"{BASE_URL}?q={urllib.parse.quote(query)}&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return ET.fromstring(r.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            raise e


def parse_items(root):
    """Parse RSS items, return clean dicts."""
    items = []
    for it in root.findall('.//item'):
        # Google uses 3-letter prefix in title like "<b>AI</b> 突破..."
        title = re.sub(r'<[^>]+>', '', it.findtext('title', '') or '')
        # Unescape HTML entities
        title = unescape(title)
        desc = re.sub(r'<[^>]+>', '', it.findtext('description', '') or '')
        desc = unescape(desc)
        link = it.findtext('link', '') or ''
        pub = it.findtext('pubDate', '') or ''
        source_elem = it.find('source')
        source = source_elem.text if source_elem is not None else ''

        items.append({
            'title': title,
            'pub': pub,
            'link': link,
            'source': source,
            'desc': desc[:300] if desc else '',
        })
    return items


def filter_recent(items, days_back=7):
    """Filter to only items within last N days (based on pubDate)."""
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    filtered = []
    for item in items:
        pub = item.get('pub', '')
        if not pub:
            filtered.append(item)
            continue
        try:
            # Parse RFC 2822 date format (e.g. "Sun, 14 Jun 2026 07:00:00 GMT")
            from email.utils import parsedate_to_datetime
            pub_dt = parsedate_to_datetime(pub)
            pub_dt = pub_dt.replace(tzinfo=None)
            if pub_dt >= cutoff:
                filtered.append(item)
        except Exception:
            filtered.append(item)  # Keep if can't parse
    return filtered


def fetch_topic(topic, max_results=5, days_back=7, use_fallback=True):
    """Fetch top N recent news for a topic."""
    if topic not in TOPIC_QUERIES:
        return []

    queries_to_try = [TOPIC_QUERIES[topic]]
    if use_fallback:
        queries_to_try.extend(FALLBACK_QUERIES.get(topic, []))

    all_items = []
    seen_titles = set()

    for query in queries_to_try:
        try:
            root = fetch_rss(query)
            items = parse_items(root)
            items = filter_recent(items, days_back=days_back)
            for item in items:
                # Dedupe by title
                title_key = item['title'][:50].lower().strip()
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)
                item['_query'] = query
                all_items.append(item)
            if len(all_items) >= max_results * 2:
                break
        except Exception as e:
            print(f"  ⚠ Query '{query}' failed: {e}")
            continue

    # Return top N
    return all_items[:max_results]


def fetch_all_topics(max_per_topic=5, days_back=7):
    """Fetch news for all 4 topics."""
    results = {}
    for topic, query in TOPIC_QUERIES.items():
        print(f"  Fetching {topic} ({query})...")
        results[topic] = fetch_topic(topic, max_results=max_per_topic, days_back=days_back)
        print(f"    → {len(results[topic])} articles")
    return results


if __name__ == "__main__":
    import sys
    print("=== Google News RSS HK Search Test ===\n")
    results = fetch_all_topics(max_per_topic=5, days_back=30)
    print(f"\n=== Summary ===")
    for topic, items in results.items():
        print(f"\n{topic} ({len(items)} articles):")
        for i, item in enumerate(items[:3], 1):
            print(f"  {i}. {item['title'][:80]}")
            print(f"     {item['source']} | {item['pub'][:30]}")
