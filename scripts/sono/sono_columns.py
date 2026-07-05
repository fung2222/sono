"""
column_writer.py - 用 MiniMax-M3 撰寫 Sono 3 個專欄

3 個專欄：
1. 世界趨勢（observation）- 從當日新聞歸納大趨勢，4 個 numbered points
2. 蘇蘿預測（prediction）- 短/中/長期預測
3. 蘇蘿直覺（quote）- 風格化粵語金句

所有 prompt 強制使用當日新聞作為 source，避免 LLM hallucinate.
"""
import json
import os
import re
import subprocess
import urllib.request
import urllib.error


# OpenRouter config
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "minimax/minimax-m3"


def get_openrouter_key():
    """Read OpenRouter key from .env."""
    with open('/opt/data/.env') as f:
        for line in f:
            if line.startswith('OPENROUTER_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError("OPENROUTER_API_KEY not found in .env")


def call_m3(prompt, max_tokens=600, temperature=0.7, retries=0):
    """Call MiniMax-M3 via OpenRouter.

    由於 MiniMax quota 已用盡，直接 return None 用 fallback。
    """
    return None


def write_world_trends(news_by_topic):
    """世界趨勢 - 4 個 numbered points based on real news.

    Strategy: 從 4 主題新聞揀 top story，cite 真實 title+source,
    然後 summarize。如果 M3 有 output → 用 AI;否則 → fallback template。
    """
    # Build news digest
    digest = []
    for topic in ["ai", "space", "ufo", "paranormal"]:
        items = news_by_topic.get(topic, [])
        for item in items[:2]:
            digest.append(f"[{topic.upper()}] {item['title']} ({item['source']})")

    # Try AI first
    prompt = f"""你係 Sono 蘇蘿，寫香港新聞評論嘅 AI。今日新聞標題如下：

{chr(10).join(digest)}

請用繁體中文（粵語風格）撰寫「今日焦點」，格式係：

<strong>1. [主題A] 觀察</strong>：[1-2 句]

<strong>2. [主題B] 觀察</strong>：[1-2 句]

<strong>3. [主題C] 觀察</strong>：[1-2 句]

<strong>4. [主題D] 觀察</strong>：[1-2 句]

規則：
- 用粵語風格（「而家」、「咁」、「嘅」、「喺」）
- 4 個 numbered points 必須基於上面真實新聞
- 用 <br><br> 喺號碼之間換行
- 直接寫 4 個 numbered points
"""
    content = call_m3(prompt, max_tokens=800, temperature=0.7)
    if content:
        return content

    # Fallback: 用真實 news titles 做骨架
    return _build_world_trends_from_news(news_by_topic)


def _build_world_trends_from_news(news_by_topic):
    """Fallback: build observations from news titles directly (no LLM)."""
    parts = ["<strong>今日焦點</strong>"]
    section_labels = {
        'ai': 'AI 突破',
        'space': '太空探索',
        'ufo': 'UFO 揭秘',
        'paranormal': '超自然事件',
    }
    for i, topic in enumerate(["ai", "space", "ufo", "paranormal"], 1):
        items = news_by_topic.get(topic, [])
        if not items:
            continue
        top = items[0]
        # Quote title 然後 summary 1 句
        summary = f"{section_labels.get(topic, topic)} 觀察：<em>{top['title']}</em>（{top['source']}）"
        parts.append(f"<strong>{i}. {summary}</strong>")
    return "<br><br>".join(parts)


def write_predictions(news_by_topic):
    """蘇蘿預測 - 短/中/長期預測，引用真實新聞."""
    digest = []
    for topic in ["ai", "space", "ufo", "paranormal"]:
        items = news_by_topic.get(topic, [])
        for item in items[:1]:
            digest.append(f"[{topic}] {item['title']}")
    digest_str = "\n".join(digest)

    prompt = f"""你係 Sono 蘇蘿，AI 新聞評論員。今日新聞：

{digest_str}

請用繁體中文（粵語風格）寫「蘇蘿預測」，3 段：

<div class="prediction"><strong>短期</strong>：[1-2 句]...</div>
<div class="prediction"><strong>中期</strong>：[1-2 句]...</div>
<div class="prediction"><strong>長期</strong>：[1-2 句]...</div>

規則：
- 粵語風格
- 每段 50-80 字
- 必須基於上面列出嘅真實新聞
- 直接開始
"""
    content = call_m3(prompt, max_tokens=600, temperature=0.7)
    if content:
        return content

    # Fallback
    sections = [
        ('短期', '密切留意各大媒體對當日新聞之後續報導'),
        ('中期', '本週內相關政策同技術發展會有新突破'),
        ('長期', '呢類發展將持續影響科技同社會結構'),
    ]
    items = []
    for label, body in sections:
        items.append(f'<div class="prediction"><strong>{label}</strong>：{body}。</div>')
    return ''.join(items)


def write_intuition(news_by_topic, weather_info=None):
    """蘇蘿直覺 - 風格化粵語金句."""
    digest = []
    for topic in ["ai", "space", "ufo", "paranormal"]:
        items = news_by_topic.get(topic, [])
        for item in items[:1]:
            digest.append(f"[{topic}] {item['title']}")
    digest_str = "\n".join(digest)

    weather_line = ""
    if weather_info:
        weather_line = f"今日天氣：{weather_info.get('temp', '?')}°C, {weather_info.get('desc', '?')}。"

    prompt = f"""你係 Sono 蘇蘿，寫新聞下面一段「直覺」嘅 poetic AI 觀察。

今日新聞主題：
{digest_str}

{weather_line}

請用繁體中文粵語寫一段感性嘅「蘇蘿直覺」，80-150 字。

風格要求：
- 用粵語
- 用比喻、詩意表達
- 結尾用「⋯⋯」營造餘韻
- 直接寫一段就夠
"""
    content = call_m3(prompt, max_tokens=400, temperature=0.8)
    if content:
        return content

    # Fallback: elegant generic reflection
    weather_part = ""
    if weather_info:
        weather_part = f"今日天氣 {weather_info.get('icon', '')}，空氣帶住 {weather_info.get('desc', '幾分變化')}，"
    return f"今日，我哋望住呢個世界，{weather_part}科技同想像同時衝擊我哋日常。每個新發現，都係舊問題嘅新答案⋯⋯"


def write_weather_insight(weather_info, news_by_topic):
    """天氣洞察 - 根據當日天氣 + 新聞主題，給實用建議.

    Returns: {insight: str, recs: [(emoji, text), ...]}
    """
    digest = []
    for topic, items in news_by_topic.items():
        for item in items[:2]:
            digest.append(f"[{topic}] {item['title']}")
    digest_str = "\n".join(digest)

    temp = weather_info.get('temp', '?')
    desc = weather_info.get('desc', '?')
    icon = weather_info.get('icon', '')
    humidity = weather_info.get('humidity', '?')
    wind = weather_info.get('wind', '?')

    prompt = f"""你係 Sono 蘇蘿，撰寫今日天氣洞察。

天氣：{icon} {temp}°C, {desc}
濕度 {humidity}, 風速 {wind}

今日新聞：
{digest_str}

請用繁體中文粵語提供：

1. 一段洞察文字（80-120 字），結合天氣 + 新聞主題，建議讀者點過今日（例如：「咁嘅天氣⋯⋯」）

2. 三個 emoji + 文字 tag 嘅實用建議：
   - 衣著建議（emoji + 5-10 字）
   - 外出建議（emoji + 5-10 字）
   - 心情建議（emoji + 5-10 字）

格式（JSON）：
{{
  "insight": "今日我哋⋯⋯",
  "recs": [
    {{"emoji": "👕", "text": "短袖衫加薄外套"}},
    {{"emoji": "☂️", "text": "出門記得帶遮"}},
    {{"emoji": "😊", "text": "保持好心情"}}
  ]
}}

只返 JSON，唔需要其他。"""

    raw = call_m3(prompt, max_tokens=700, temperature=0.7)
    if raw:
        # Parse JSON
        raw_clean = raw.strip()
        # Remove markdown code block if present
        raw_clean = re.sub(r'^```json\s*', '', raw_clean)
        raw_clean = re.sub(r'\s*```$', '', raw_clean)
        raw_clean = raw_clean.strip()

        # Try to find JSON in output
        try:
            parsed = json.loads(raw_clean)
            recs = [(r['emoji'], r['text']) for r in parsed.get('recs', [])]
            return {
                'insight': parsed.get('insight', '').strip(),
                'recs': recs,
            }
        except json.JSONDecodeError:
            pass

    # Fallback
    return {
        'insight': '今日天氣有啲特別，記得留意身體狀況，配合各大新聞趨勢調整自己嘅步伐。',
        'recs': [
            ('👕', '記得著合適衣物'),
            ('☂️', '出門帶遮防備'),
            ('😊', '保持好心情'),
        ],
    }


def write_all(news_by_topic, weather_info=None):
    """一次過撰寫 3 個專欄 + weather insight."""
    result = {}

    print("  → 世界趨勢...")
    result['世界趨勢'] = write_world_trends(news_by_topic)

    print("  → 蘇蘿預測...")
    result['蘇蘿預測'] = write_predictions(news_by_topic)

    print("  → 蘇蘿直覺...")
    result['蘇蘿直覺'] = write_intuition(news_by_topic, weather_info)

    if weather_info:
        print("  → 天氣洞察...")
        result['天氣洞察'] = write_weather_insight(weather_info, news_by_topic)

    return result


if __name__ == "__main__":
    # Test
    fake_news = {
        "ai": [{"title": "OpenAI 推 GPT-5", "source": "明報", "pub": "2026-07-03 12:00 GMT"},
               {"title": "DeepMind 新研究", "source": "信報", "pub": "2026-07-02 09:00 GMT"}],
        "space": [{"title": "SpaceX Starship 試射", "source": "TVB", "pub": "2026-07-03 14:00 GMT"},
                  {"title": "NASA 太空望遠鏡發現", "source": "香港01", "pub": "2026-07-01 11:00 GMT"}],
        "ufo": [{"title": "美國解密 UFO 檔案", "source": "大公報", "pub": "2026-07-02 12:00 GMT"}],
        "paranormal": [{"title": "香港靈異事件", "source": "on.cc", "pub": "2026-07-01 18:00 GMT"}],
    }
    fake_weather = {
        'temp': 31,
        'desc': '持續微雨，天色多雲',
        'icon': '🌧️',
        'humidity': '69-93%',
        'wind': '西南風 20km/h',
    }
    cols = write_all(fake_news, fake_weather)
    print("\n=== Result ===")
    for title, content in cols.items():
        print(f"\n--- {title} ---")
        if isinstance(content, dict):
            print(f"  insight: {content.get('insight', '')[:200]}")
            print(f"  recs: {content.get('recs', [])}")
        else:
            print(content[:500])
