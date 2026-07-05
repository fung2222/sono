#!/usr/bin/env python3
"""
generate_news_cards.py - 由 Google News RSS 結果 產生 20 個 HTML news cards

輸入: news_by_topic dict {topic: [items]}
輸出: HTML 4 個 sections × 5 cards = 20 cards

Source 路徑 wrap 邏輯：Google News 用 wrapper URL (https://news.google.com/rss/articles/CBMi...)
用戶 click 自動跳轉，<a href> 直接用 wrapper URL 都 work。
"""
import re
import html as html_module


# 主題中文 + emoji
TOPIC_LABELS = {
    "ai": ("AI 科技", "🤖"),
    "space": ("太空宇宙", "🚀"),
    "ufo": ("UFO 外星人", "👽"),
    "paranormal": ("超自然現象", "🔮"),
}


def _classify_tag(title: str, source: str = "") -> tuple:
    """根據 title classify 到 tag class + 中文標籤.

    Returns: (css_class, label)
    """
    title_lower = title.lower()

    # Priority keywords (most specific first)
    if any(k in title for k in ['突破', '突破性', '突破性嘅', '首次']):
        return 'breakthrough', '突破'
    if any(k in title for k in ['警告', '危機', '緊急', '威脅']):
        return 'warning', '警告'
    if any(k in title for k in ['預測', '未來', '將會', '預計', '預估']):
        return 'prediction', '預測'
    if any(k in title for k in ['發現', '解密', '公開', '曝光']):
        return 'discovery', '發現'
    if any(k in title for k in ['創新', '新', '推出', '發布', '發佈']):
        return 'innovation', '創新'
    return 'update', '消息'


def make_card(item: dict, index: int) -> str:
    """Create ONE news card HTML string.

    格式參考 6/23 黃金骨架的 .news-card 結構。
    """
    title = item.get('title', '').strip()
    source = item.get('source', '新聞').strip()
    link = item.get('link', '').strip()
    pub = item.get('pub', '').strip()

    # Clean title - remove HTML entities / tags
    title = html_module.unescape(title)

    # Parse pub date for display
    date_str = ''
    if pub:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(pub)
            date_str = f"{dt.month}/{dt.day}"
        except Exception:
            date_str = pub[:6]

    # Classify tag
    tag_class, tag_label = _classify_tag(title, source)

    # Build card HTML (參考 golden skeleton format)
    card_html = f'''<div class="news-card {tag_class}">
      <h3>{title} <span class="tag {tag_class}">{tag_label}</span></h3>
      <div class="meta">{date_str} / <a href="{link}" target="_blank" rel="noopener">{source}</a></div>
      <p>{item.get('desc', '').strip()}</p>
    </div>'''
    return card_html


def make_section(topic: str, items: list, panel_id: str) -> str:
    """Build one panel with 5 cards (or fewer if not enough)."""
    label, emoji = TOPIC_LABELS.get(topic, (topic.title(), '📰'))

    cards_html = '\n'.join(make_card(item, i) for i, item in enumerate(items[:5], 1))

    section_html = f'''<div class="section-panel" id="panel-{panel_id}">
  <div class="section-header">
    <span class="section-icon">{emoji}</span>
    <span>{label}</span>
  </div>
{cards_html}
</div>'''
    return section_html


def make_news_tab(topic: str, panel_id: str, is_active: bool = False) -> str:
    """Build one news tab button."""
    label, emoji = TOPIC_LABELS.get(topic, (topic.title(), '📰'))
    active_cls = ' active' if is_active else ''
    return f'<button class="news-tab{active_cls}" data-section="{panel_id}"><span class="tab-icon">{emoji}</span> <span>{label}</span></button>'


def make_tabs(active_topic: str = 'ai') -> str:
    """Build news tab bar with active topic highlighted."""
    tabs = []
    for topic in ['ai', 'space', 'ufo', 'paranormal']:
        tabs.append(make_news_tab(topic, topic, is_active=(topic == active_topic)))
    return '\n'.join(tabs)


def render_news_block(news_by_topic: dict, active_topic: str = 'ai') -> dict:
    """Render the full news section: tabs + 4 panel sections.

    Returns dict with keys:
      - 'tabs': HTML for tab buttons
      - 'sections': combined HTML for all 4 panel sections
      - 'ai_panel', 'space_panel', 'ufo_panel', 'paranormal_panel': individual panel HTMLs
    """
    tabs = make_tabs(active_topic)
    panels = {}
    for topic in ['ai', 'space', 'ufo', 'paranormal']:
        panels[topic] = make_section(topic, news_by_topic.get(topic, []), topic)

    return {
        'tabs': tabs,
        'sections': '\n'.join(panels.values()),
        **panels,
    }


# === Standalone test ===
if __name__ == "__main__":
    fake_news = {
        'ai': [
            {'title': 'OpenAI 推出 GPT-5 全面升級', 'source': '明報', 'link': 'https://example.com/1', 'pub': 'Mon, 04 Jul 2026 10:00:00 GMT', 'desc': 'OpenAI 公佈...'},
            {'title': '香港創科局啟動 AI 教育計畫', 'source': '香港商報', 'link': 'https://example.com/2', 'pub': 'Tue, 28 Jun 2026 12:00:00 GMT', 'desc': '創科局推出...'},
            {'title': 'DeepMind 新 AI 研究突破', 'source': '信報', 'link': 'https://example.com/3', 'pub': 'Tue, 02 Jul 2026 18:00:00 GMT', 'desc': 'DeepMind 突破...'},
            {'title': 'AI 預測量子計算突破', 'source': 'TVB', 'link': 'https://example.com/4', 'pub': 'Wed, 03 Jul 2026 09:00:00 GMT', 'desc': 'AI 預測...'},
            {'title': 'Microsoft AI 服務遇到危機', 'source': '大公報', 'link': 'https://example.com/5', 'pub': 'Wed, 03 Jul 2026 14:00:00 GMT', 'desc': 'Microsoft 警告...'},
        ],
        'space': [], 'ufo': [], 'paranormal': [],
    }

    out = render_news_block(fake_news)
    print('--- TABS ---')
    print(out['tabs'])
    print('\n--- AI PANEL ---')
    print(out['ai_panel'][:500])
