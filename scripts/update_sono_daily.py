#!/usr/bin/env python3
"""
Sono每日全自動化更新 Script
每日自動搵新鮮新聞 → 生成新一日 HTML → push
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 ====================
REPO_DIR = Path("/opt/data/sono-repo")
REPORTS_DIR = REPO_DIR / "reports"
GOLDEN_SKELETON = REPO_DIR / "sono_20260628.html"  # 黃金骨架
SEARX_SCRIPT = "/opt/data/searx_html_search.py"

# 新聞主題
TOPICS = {
    "ai": {
        "name": "AI科技",
        "icon": "🤖",
        "queries": [
            "AI technology OR chip OR data center June 2026",
            "AI OR artificial intelligence news 2026"
        ]
    },
    "space": {
        "name": "太空宇宙",
        "icon": "🚀",
        "queries": [
            "space exploration OR NASA OR rocket June 2026",
            "Mars OR ISS OR satellite news 2026"
        ]
    },
    "ufo": {
        "name": "UFO/外星人",
        "icon": "🛸",
        "queries": [
            "UFO OR UAP OR alien news 2026",
            "extraterrestrial OR disclosure 2026"
        ]
    },
    "paranormal": {
        "name": "超自然現象",
        "icon": "👻",
        "queries": [
            "paranormal OR ghost OR cryptid news 2026",
            "supernatural mystery 2026"
        ]
    }
}

MAX_NEWS_PER_TOPIC = 5

# ==================== 工具函數 ====================
def run_searx_search(query):
    """呼叫 searx_html_search.py 搵新聞"""
    try:
        result = subprocess.run(
            ["python3", SEARX_SCRIPT, query],
            capture_output=True,
            text=True,
            timeout=30
        )
        data = json.loads(result.stdout)
        # 過濾有 URL 嘅結果
        return [item for item in data if item.get("url") and item.get("title")]
    except Exception as e:
        print(f"Search error for '{query}': {e}")
        return []

def fetch_news_for_topic(topic_key, topic_info):
    """為單一主題搵新聞"""
    all_results = []
    for query in topic_info["queries"]:
        results = run_searx_search(query)
        all_results.extend(results)
    
    # 去重 + 限制數量
    seen_urls = set()
    unique_results = []
    for item in all_results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique_results.append(item)
            if len(unique_results) >= MAX_NEWS_PER_TOPIC:
                break
    
    return unique_results[:MAX_NEWS_PER_TOPIC]

def generate_news_card_html(news_item, topic_key):
    """生成單張 news-card HTML"""
    title = news_item.get("title", "無標題")[:80]
    url = news_item.get("url", "#")
    content = news_item.get("content", "")[:200]
    
    # 簡單 tag 分配
    tag = "熱門" if topic_key in ["ai", "space"] else "趨勢"
    tag_class = "breakthrough" if topic_key in ["ai", "space"] else "trend"
    
    html = f'''  <div class="news-card {topic_key}">
    <h3>{title} <span class="tag {tag_class}">{tag}</span></h3>
    <div class="expand-hint">⋯ 點擊展開</div>
    <div class="detail">
    <div class="meta">Jun 30 / 來源 / <a href="{url}" target="_blank">來源</a></div>
    <p>{content}</p>
    </div>
  </div>'''
    return html

def generate_section_html(topic_key, topic_info, news_list):
    """生成整個 section HTML"""
    cards_html = "\n".join([generate_news_card_html(n, topic_key) for n in news_list])
    
    html = f'''<div class="section-panel" id="panel-{topic_key}">
<div class="section" id="{topic_key}">
{cards_html}
</div>
</div>'''
    return html

def create_daily_report(today_str):
    """生成新一日日報（真正替換 4 個 section）"""
    print(f"開始生成 {today_str} 日報...")

    # 讀取黃金骨架
    with open(GOLDEN_SKELETON, "r", encoding="utf-8") as f:
        skeleton = f.read()

    # 為每個主題搵新聞
    all_sections = {}
    for topic_key, topic_info in TOPICS.items():
        print(f"  搵 {topic_info['name']} 新聞...")
        news_list = fetch_news_for_topic(topic_key, topic_info)
        section_html = generate_section_html(topic_key, topic_info, news_list)
        all_sections[topic_key] = section_html
        print(f"    → 搵到 {len(news_list)} 篇")

    # 真正替換 4 個 section
    skeleton = re.sub(
        r'<div class="section-panel active" id="panel-ai">.*?</div>
</div>',
        all_sections["ai"],
        skeleton,
        flags=re.DOTALL
    )
    skeleton = re.sub(
        r'<div class="section-panel" id="panel-space">.*?</div>
</div>',
        all_sections["space"],
        skeleton,
        flags=re.DOTALL
    )
    skeleton = re.sub(
        r'<div class="section-panel" id="panel-ufo">.*?</div>
</div>',
        all_sections["ufo"],
        skeleton,
        flags=re.DOTALL
    )
    skeleton = re.sub(
        r'<div class="section-panel" id="panel-paranormal">.*?</div>
</div>',
        all_sections["paranormal"],
        skeleton,
        flags=re.DOTALL
    )

    # 更新日期
    skeleton = skeleton.replace("2026.06.28", f"2026.{today_str[4:6]}.{today_str[6:8]}")
    skeleton = skeleton.replace("20260628", today_str)

    output_path = REPORTS_DIR / f"sono_{today_str}.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(skeleton)

    print(f"✅ 日報已生成: {output_path}")
    return output_path

def update_index_files(today_str):
    """更新首頁同 reports/index.html 入口"""
    print("更新入口頁面...")
    # TODO: 實際實現
    pass


def backup_reports(today_str):
    """更新前先備份"""
    import shutil
    from datetime import datetime
    
    backup_dir = REPO_DIR / "backups" / today_str
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 備份整個 reports 資料夾
    shutil.copytree(REPORTS_DIR, backup_dir / "reports", dirs_exist_ok=True)
    print(f"✅ 已備份到: {backup_dir}")
    return backup_dir

def git_commit_and_push(today_str):
    """commit 並 push"""
    print("Push 到 GitHub...")
    try:
        subprocess.run(["git", "add", "reports/"], cwd=REPO_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"自動更新 {today_str} 日報（全自動化）"],
            cwd=REPO_DIR,
            check=True
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
        print("✅ Push 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Push 失敗: {e}")
        return False

# ==================== 主流程 ====================
def main():
    today = datetime.now()
    today_str = today.strftime("%Y%m%d")
    
    print(f"=== Sono每日全自動化更新 {today_str} ===")
    
    # 0. 先備份
    backup_reports(today_str)
    
    # 1. 生成日報
    report_path = create_daily_report(today_str)
    
    # 2. 更新入口
    update_index_files(today_str)
    
    # 3. Push
    success = git_commit_and_push(today_str)
    
    if success:
        print(f"\n✅ {today_str} 日報全自動化更新完成！")
    else:
        print(f"\n❌ 更新失敗，請手動檢查")
        sys.exit(1)

if __name__ == "__main__":
    main()