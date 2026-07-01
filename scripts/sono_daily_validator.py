#!/usr/bin/env python3
"""
Sono 每日自動化除錯工具
檢查日報生成是否正確，發現問題即報告
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

REPO_PATH = Path("/opt/data/sono-repo")
REPORTS_PATH = REPO_PATH / "reports"

def validate_report(date_str):
    """驗證指定日期嘅日報"""
    errors = []
    warnings = []
    info = []
    
    report_path = REPORTS_PATH / f"sono_{date_str}.html"
    banner_path = REPORTS_PATH / f"weather_banner_{date_str}.png"
    
    # 1. 檢查檔案是否存在
    if not report_path.exists():
        errors.append(f"❌ 日報檔案不存在: {report_path.name}")
        return errors, warnings, info
    else:
        info.append(f"✅ 日報檔案存在: {report_path.name} ({report_path.stat().st_size} bytes)")
    
    if not banner_path.exists():
        warnings.append(f"⚠️ Banner 圖片不存在: {banner_path.name}（可能使用預設）")
    else:
        banner_size = banner_path.stat().st_size
        if banner_size < 10000:
            warnings.append(f"⚠️ Banner 圖片過細: {banner_size} bytes（可能生成失敗）")
        else:
            info.append(f"✅ Banner 圖片存在: {banner_path.name} ({banner_size} bytes)")
    
    # 2. 讀取日報內容
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. 檢查日期標題
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    expected_date = date_obj.strftime("%Y年%-m月%-d日")
    if expected_date not in content:
        errors.append(f"❌ 日期標題錯誤: 搵唔到 '{expected_date}'")
    else:
        info.append(f"✅ 日期標題正確: {expected_date}")
    
    # 4. 檢查天氣數據
    weather_checks = [
        (r'class="weather-main"', "天氣主要區塊"),
        (r'class="temp"', "溫度數據"),
        (r'低 \d+ / 高 \d+', "溫度範圍"),
        (r'濕度.*?value.*?\d+.*?%', "濕度數據"),
        (r'風速.*?value.*?km/h', "風速數據"),
    ]
    
    for pattern, name in weather_checks:
        if not re.search(pattern, content, re.DOTALL):
            errors.append(f"❌ 缺少{name}")
        else:
            info.append(f"✅ {name}存在")
    
    # 5. 檢查 Banner 圖片引用
    if f'weather_banner_{date_str}.png' not in content:
        warnings.append(f"⚠️ 日報無引用今日 Banner")
    else:
        info.append(f"✅ 正確引用今日 Banner")
    
    # 6. 檢查 Sono 專欄（3個部分）
    column_parts = [
        (r'sc-sub-title.*?世界趨勢', "世界趨勢"),
        (r'sc-sub-title.*?蘇蘿預測', "蘇蘿預測"),
        (r'sc-sub-title.*?蘇蘿直覺', "蘇蘿直覺"),
    ]
    
    for pattern, name in column_parts:
        if not re.search(pattern, content):
            errors.append(f"❌ 缺少專欄部分: {name}")
        else:
            info.append(f"✅ 專欄部分存在: {name}")
    
    # 7. 檢查新聞 Tabs（4個主題）
    news_topics = [
        (r'news-tab.*?data-section="ai"', "AI科技 Tab"),
        (r'news-tab.*?data-section="space"', "太空宇宙 Tab"),
        (r'news-tab.*?data-section="ufo"', "UFO外星人 Tab"),
        (r'news-tab.*?data-section="paranormal"', "超自然 Tab"),
        (r'section-panel.*?id="panel-ai"', "AI科技 新聞區"),
        (r'section-panel.*?id="panel-space"', "太空宇宙 新聞區"),
        (r'section-panel.*?id="panel-ufo"', "UFO外星人 新聞區"),
        (r'section-panel.*?id="panel-paranormal"', "超自然 新聞區"),
    ]
    
    for pattern, name in news_topics:
        if not re.search(pattern, content, re.DOTALL):
            errors.append(f"❌ 缺少新聞部分: {name}")
        else:
            info.append(f"✅ 新聞部分存在: {name}")
    
    # 8. 檢查新聞卡片數量
    news_card_count = len(re.findall(r'<div class="news-card', content))
    if news_card_count < 15:
        warnings.append(f"⚠️ 新聞卡片數量偏少: {news_card_count}（建議20個）")
    elif news_card_count > 25:
        warnings.append(f"⚠️ 新聞卡片數量偏多: {news_card_count}（建議20個）")
    else:
        info.append(f"✅ 新聞卡片數量正常: {news_card_count}")
    
    # 9. 檢查導航系統
    nav_checks = [
        (r'上一日', "上一日連結"),
        (r'首頁', "首頁連結"),
        (r'下一日', "下一日連結"),
    ]
    
    for pattern, name in nav_checks:
        if not re.search(pattern, content):
            errors.append(f"❌ 缺少{name}")
        else:
            info.append(f"✅ {name}存在")
    
    # 10. 檢查導航連結指向
    prev_link = re.search(r'href="sono_(\d{8})\.html"[^>]*>.*?上一日', content)
    next_link = re.search(r'上一日.*?href="sono_(\d{8})\.html"', content)
    
    if prev_link:
        prev_date = prev_link.group(1)
        prev_path = REPORTS_PATH / f"sono_{prev_date}.html"
        if prev_path.exists():
            info.append(f"✅ 上一日連結正確: {prev_date}")
        else:
            errors.append(f"❌ 上一日連結指向不存在嘅日期: {prev_date}")
    
    if next_link:
        next_date = next_link.group(1)
        next_path = REPORTS_PATH / f"sono_{next_date}.html"
        if next_path.exists():
            info.append(f"✅ 下一日連結正確: {next_date}")
        else:
            errors.append(f"❌ 下一日連結指向不存在嘅日期: {next_date}")
    
    # 11. 檢查 Footer
    if "Sono每日資訊系統" not in content:
        errors.append("❌ 缺少 Footer 文字")
    else:
        info.append("✅ Footer 存在")
    
    # 12. 檢查 HTML 結構完整性
    open_divs = len(re.findall(r'<div[ >]', content))
    close_divs = len(re.findall(r'</div>', content))
    
    if open_divs != close_divs:
        errors.append(f"❌ HTML div 標籤不匹配: {open_divs} 個 <div>, {close_divs} 個 </div>")
    else:
        info.append(f"✅ HTML div 標籤匹配: {open_divs} 個")
    
    # 13. 檢查首頁連結
    index_path = REPO_PATH / "index.html"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        if f"sono_{date_str}.html" in index_content:
            info.append("✅ 首頁已包含今日連結")
        else:
            warnings.append(f"⚠️ 首頁未包含今日連結: {date_str}")
    
    # 14. 檢查 Git 狀態
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.stdout.strip():
            uncommitted = result.stdout.strip().count('\n') + 1
            warnings.append(f"⚠️ Git 有 {uncommitted} 個未提交嘅變更")
        else:
            info.append("✅ Git 狀態乾淨（無未提交變更）")
    except Exception as e:
        warnings.append(f"⚠️ 無法檢查 Git 狀態: {e}")
    
    return errors, warnings, info


def generate_report(date_str):
    """生成驗證報告"""
    print(f"\n{'='*70}")
    print(f"Sono 每日除錯報告 - {date_str}")
    print(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    errors, warnings, info = validate_report(date_str)
    
    # 輸出結果
    if errors:
        print(f"❌ 發現 {len(errors)} 個錯誤:\n")
        for err in errors:
            print(f"  {err}")
        print()
    
    if warnings:
        print(f"⚠️ 發現 {len(warnings)} 個警告:\n")
        for warn in warnings:
            print(f"  {warn}")
        print()
    
    print(f"✅ 通過 {len(info)} 項檢查:\n")
    for inf in info:
        print(f"  {inf}")
    print()
    
    # 總結
    print(f"{'='*70}")
    if errors:
        print(f"❌ 驗證失敗: {len(errors)} 個錯誤, {len(warnings)} 個警告")
        return False
    elif warnings:
        print(f"⚠️ 驗證通過（有警告）: {len(warnings)} 個警告")
        return True
    else:
        print(f"✅ 驗證完全通過: {len(info)} 項檢查全部正確")
        return True


if __name__ == "__main__":
    # 如果無指定日期，檢查今日
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    success = generate_report(date_str)
    sys.exit(0 if success else 1)
