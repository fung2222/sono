#!/usr/bin/env python3
"""
update_sono_daily.py - 用 6/23 黃金骨架做 template，生成當日日報

流程:
1. 從 Google News RSS 拉 4 主題新聞
2. 從 Open-Meteo 拉當日天氣 + 5 日預報
3. 用 news-based fallback 生成 3 個專欄 + weather insight
4. 生成 new cards HTML
5. 全部注入 template → auto save + push

Usage:
  python3 update_sono_daily.py                 # 今日 (2026-07-05)
  python3 update_sono_daily.py 2026-07-03      # 指定日期
"""
import sys
import os
import re
import json
import shutil
from datetime import datetime
from email.utils import parsedate_to_datetime

# ── 內部 modules ──
sys.path.insert(0, '/opt/data/scripts/sono')
from gnews_hk_search import fetch_all_topics
from weather_fetcher import fetch_weather
from generate_news_cards import render_news_block
from sono_columns import write_all as write_columns

# ── Paths ──
SONO_DIR = '/opt/data/github-repos/sono'
GOLDEN = os.path.join(SONO_DIR, 'reports/sono_20260623.html')
REPORTS_DIR = os.path.join(SONO_DIR, 'reports')

# ── Weekday names ──
WEEKDAY_NAMES = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']


def load_golden_template():
    """Load 6/23 as base template."""
    with open(GOLDEN) as f:
        return f.read()


def replace_date(template, date_obj):
    """Replace date placeholder in title, header, footer."""
    date_str = date_obj.strftime('%Y.%m.%d')
    date_weekday = WEEKDAY_NAMES[date_obj.weekday()]
    date_full = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日（{date_weekday}）"

    # Title
    template = re.sub(
        r'<title>Sono每日 \d{4}\.\d{2}\.\d{2}</title>',
        f'<title>Sono每日 {date_str}</title>',
        template
    )
    # Head date line - only the main header date (not forecast day dates)
    template = re.sub(
        r'<div style="font-size:0\.78em; color:#888;">\d{4}年\d{1,2}月\d{1,2}日（[^）]*）</span>',
        f'<div style="font-size:0.78em; color:#888;">{date_full}</span>',
        template
    )
    # Footer date - only first occurrence outside weather context
    template = re.sub(
        r'\d{4}年\d{1,2}月\d{1,2}日（[^）]*）',
        date_full,
        template,
        count=1  # Only first (header), skip forecast
    )

    return template


def replace_weather(template, weather):
    """Replace weather block + forecast + insight from weather data.

    Uses the golden's weather-box structure but fills in new values.
    """
    # Weather icon
    icon = weather.get('icon', '🌤️')
    temp_max = weather.get('temp_max', 30)
    temp_min = weather.get('temp_min', 28)
    desc = weather.get('desc', '多雲')
    humidity = weather.get('humidity', '70-85%')
    wind = weather.get('wind', '風 20km/h')
    uv = weather.get('uv', '中等')
    vis = weather.get('visibility', '良好')

    # Weather header
    template = re.sub(
        r'<span>🌧️ 香港天氣</span>',
        f'<span>{icon} 香港天氣</span>',
        template
    )
    template = re.sub(
        r'<div class="icon">🌧️</div>',
        f'<div class="icon">{icon}</div>',
        template
    )
    template = re.sub(
        r'<div class="temp">\d+</div>',
        f'<div class="temp">{temp_max}</div>',
        template
    )
    template = re.sub(
        r'低 \d+ / 高 \d+',
        f'低 {temp_min} / 高 {temp_max}',
        template
    )
    template = re.sub(
        r'<div class="desc">[^<]*</div>',
        f'<div class="desc">{desc}</div>',
        template
    )

    # Weather details
    template = re.sub(
        r'<div class="label">濕度</div><div class="value">[^<]*</div>',
        f'<div class="label">濕度</div><div class="value">{humidity}</div>',
        template
    )
    template = re.sub(
        r'<div class="label">風速</div><div class="value">[^<]*</div>',
        f'<div class="label">風速</div><div class="value">{wind}</div>',
        template
    )
    template = re.sub(
        r'<div class="label">紫外線</div><div class="value">[^<]*</div>',
        f'<div class="label">紫外線</div><div class="value">{uv}</div>',
        template
    )
    template = re.sub(
        r'<div class="label">能見度</div><div class="value">[^<]*</div>',
        f'<div class="label">能見度</div><div class="value">{vis}</div>',
        template
    )

    # 5-day forecast
    forecast = weather.get('forecast', [])
    forecast_html_parts = []
    for day in forecast[:5]:
        forecast_html_parts.append(
            f'<div class="forecast-day"><div class="weekday">{day["weekday"]}</div>'
            f'<div class="date">{day["date"]}</div>'
            f'<div class="ficon">{day["icon"]}</div>'
            f'<div class="ftemp">{day["temp_max"]}</div>'
            f'<div class="ftemp-lo">{day["temp_min"]}</div></div>'
        )
    forecast_html = '\n        '.join(forecast_html_parts)

    # Replace forecast grid - match from <div class="forecast-grid"> to </div>\n      </div>
    template = re.sub(
        r'<div class="forecast-grid">.*?</div>\s*</div>(?=\s*<div class="weather-links">)',
        f'<div class="forecast-grid">\n        {forecast_html}\n      </div>\n    </div>',
        template,
        flags=re.DOTALL
    )

    return template


def replace_weather_insight(template, news_by_topic, weather):
    """Replace weather insight block with news+weather based insight."""
    # Generate insight from news + weather
    from sono_columns import write_weather_insight
    insight_data = write_weather_insight(weather, news_by_topic)

    # Build insight HTML
    insight_text = insight_data.get('insight', '留意天氣變化，保持好心情。')
    recs = insight_data.get('recs', [])

    insight_html = f'''  <div class="weather-insight">
    <h3>☔ Sono 天氣洞察</h3>
    <p class="insight-text">{insight_text}</p>'''

    for emoji, text in recs:
        insight_html += f'\n    <div class="recommendation"><span class="emoji">{emoji}</span><span class="text">{text}</span></div>'

    insight_html += '\n  </div>'

    # Find the weather-insight block in template and replace
    match = re.search(r'<div class="weather-insight">.*?</div>\s*</div>(?=\s*<!-- SONO 專欄)', template, re.DOTALL)
    if match:
        template = template[:match.start()] + insight_html + template[match.end():]
    else:
        # No insight block yet - add before sono-column
        template = template.replace(
            '<!-- SONO 專欄 (accordion) -->',
            f'{insight_html}\n\n<!-- SONO 專欄 (accordion) -->'
        )

    return template


def replace_news(template, news_by_topic):
    """Replace news tabs + 4 panels with generated cards."""
    news_block = render_news_block(news_by_topic, active_topic='ai')

    # Replace tabs
    template = re.sub(
        r'<div class="news-tab-bar">.*?</div>(?=\s*<div class="section-panel)',
        f'<div class="news-tab-bar">\n{news_block["tabs"]}\n    </div>',
        template,
        flags=re.DOTALL
    )

    # Replace 4 panels (ai, space, ufo, paranormal) individually
    panels = news_block['sections']
    # Find the "sections" area: from first panel to the footer
    match = re.search(
        r'(<div class="section-panel[^>]*id="panel-ai"[^>]*>).*?(?=<div class="footer")',
        template, re.DOTALL
    )
    if match:
        template = template[:match.start()] + panels + template[match.end():]
    else:
        # Fallback: replace each panel
        for topic in ['ai', 'space', 'ufo', 'paranormal']:
            topic_html = news_block.get(f'{topic}_panel', '')
            template = re.sub(
                rf'<div class="section-panel[^>]*id="panel-{topic}"[^>]*>.*?(?=<div class="section-panel|<div class="footer")',
                topic_html,
                template,
                flags=re.DOTALL
            )

    return template


def replace_columns(template, news_by_topic, weather):
    """Replace 3 sono columns with generated fallback content."""
    cols = write_columns(news_by_topic, weather)

    # Replace 世界趨勢 (observation)
    world_trend_html = cols.get('世界趨勢', '<strong>今日焦點</strong><br>留意最新發展。')
    template = re.sub(
        r'(<span class="sc-sub-title">🌍 世界趨勢</span>.*?<div class="sc-sub-body">).*?(</div>\s*</div>\s*<div class="sc-sub")',
        f'\\1<div class="observation">{world_trend_html}</div>\\2',
        template,
        flags=re.DOTALL
    )

    # Replace 蘇蘿預測 (prediction)
    prediction_html = cols.get('蘇蘿預測', '')
    template = re.sub(
        r'(<span class="sc-sub-title">📡 蘇蘿預測</span>.*?<div class="sc-sub-body">).*?(</div>\s*</div>\s*<div class="sc-sub")',
        f'\\1<div class="prediction">{prediction_html}</div>\\2',
        template,
        flags=re.DOTALL
    )

    # Replace 蘇蘿直覺 (quote + prediction mix)
    intuition_html = cols.get('蘇蘿直覺', '')
    template = re.sub(
        r'(<span class="sc-sub-title">🔮 蘇蘿直覺</span>.*?<div class="sc-sub-body">).*?(</div>\s*</div>\s*</div>)',
        f'\\1<div class="quote" style="font-style:italic;color:#e0e0e0;padding:15px;background:rgba(255,107,157,0.05);border-radius:8px;line-height:1.8;">{intuition_html}</div>\\2',
        template,
        flags=re.DOTALL
    )

    return template


def remove_banner_img(template):
    """Remove weather_banner img reference (since we deleted the PNGs)."""
    template = re.sub(
        r'<img src="/sono/reports/weather_banner_\d{8}\.png"[^>]*>',
        '',
        template
    )
    return template


def generate_report(date_str):
    """
    Main: fetch news + weather, generate full report HTML.

    Args:
        date_str: YYYY-MM-DD format date
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    report_date = date_obj.strftime('%Y%m%d')
    print(f"\n{'='*60}")
    print(f"  Generating Sono Daily Report for {date_str}")
    print(f"{'='*60}\n")

    # 1. Fetch news
    print("📰 Fetching news from Google RSS...")
    news = fetch_all_topics(max_per_topic=5, days_back=30)
    print(f"   Total: {sum(len(v) for v in news.values())} articles")

    # 2. Fetch weather
    print("\n🌤️ Fetching weather from Open-Meteo...")
    weather = fetch_weather(date_str)
    print(f"   {weather['icon']} {weather['desc']} {weather['temp_max']}°C")

    # 3. Load template
    print("\n📋 Loading 6/23 golden template...")
    html = load_golden_template()

    # 4. Replace sections
    print("\n🔧 Replacing sections...")
    html = replace_date(html, date_obj)
    print("   ✓ Date replaced")

    html = replace_weather(html, weather)
    print("   ✓ Weather replaced")

    html = replace_weather_insight(html, news, weather)
    print("   ✓ Weather insight replaced")

    html = replace_columns(html, news, weather)
    print("   ✓ Sono columns replaced")

    html = replace_news(html, news)
    print("   ✓ News replaced")

    html = remove_banner_img(html)
    print("   ✓ Banner removed")

    # 5. Write file
    output_file = os.path.join(REPORTS_DIR, f'sono_{report_date}.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(output_file) / 1024
    print(f"\n✅ Written: {output_file} ({size_kb:.1f} KB)")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        # Default: today in HKT
        from datetime import timezone, timedelta
        hkt = datetime.now(timezone.utc) + timedelta(hours=8)
        date_str = hkt.strftime('%Y-%m-%d')

    generate_report(date_str)
