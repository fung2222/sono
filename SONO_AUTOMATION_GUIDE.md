# 📖 Sono每日網站自動化指南

## 概覽
Sono每日 (fung2222.github.io/sono) 係一個香港天氣/新聞/AI洞察 app，每日自動更新。

**GitHub Repo**: `fung2222/sono`
**本地路徑**: `/opt/data/sono-repo`
**自動化腳本**: `/opt/data/scripts/sono_daily_automation.py`
**Cron Job**: `ea9af07ed35e` — 每日 HKT 06:00 (UTC 22:00)

---

## 🏗️ 網站架構

```
sono-repo/
├── index.html          ← 首頁（含日報列表、工具箱、遊戲）
├── reports/
│   ├── sono_YYYYMMDD.html      ← 每日日報
│   └── weather_banner_YYYYMMDD.png  ← 每日天氣 banner
├── 2048/, snake/, fighter/ ... ← 遊戲
├── tools/              ← 實用工具
├── scripts/
│   ├── search_today_news.py    ← 新聞搜尋輔助腳本
│   └── sono_daily_validator.py ← 自動除錯腳本
└── images/, favicon.*  ← 靜態資源
```

---

## 📋 每日日報結構

每個日報 `sono_YYYYMMDD.html` 包含：

1. **Header** — Logo + 副標題 + Chat Widget
2. **天氣 Box** — 當日香港天氣詳情
3. **天氣 Banner** — 16:9 比例圖片 (1920×1080)
4. **未來5天預報** — 根據真實數據
5. **天氣連結** — 天文台 + 熱帶氣旋
6. **Sono 天氣洞察** — AI 生成嘅天氣建議
7. **Sono 專欄** — 3大標題（世界趨勢/蘇蘿預測/蘇蘿直覺）
8. **新聞 Tabs** — 4大主題（AI科技/太空宇宙/UFO外星人/超自然）
9. **導航 Bar** — ◀上一日 | 首頁 | 下一日▶
10. **Footer** — Sono每日資訊系統

---

## 🌡️ 天氣數據規則

**數據來源**: OpenMeteo Archive API
- URL: `https://archive-api.open-meteo.com/v1/archive`
- 座標: 緯度 22.28, 經度 114.16（香港）
- 時區: Asia/Hong_Kong

**每日必須更新嘅天氣元素：**
| 元素 | 位置 | 格式 |
|------|------|------|
| 天氣圖示 + 描述 | `.weather-main` | WMO代碼對應 |
| 溫度 | `.temp` / `.temp-range` | 低 X / 高 Y |
| 濕度 | `.weather-detail-item` | X-Y% |
| 風速風向 | `.weather-detail-item` | 方向 + km/h |
| 紫外線 | `.weather-detail-item` | 根據降雨推算 |
| 能見度 | `.weather-detail-item` | 根據降雨推算 |
| 未來5天 | `.forecast-grid` | 5個 forecast-day |
| 天氣洞察 | `.weather-insight` | AI 撰寫 |

**WMO 天氣代碼對應：**
- 0=☀️天晴, 1=🌤️大致天晴, 2=⛅間中有陽光, 3=☁️多雲
- 51=🌦️微雨, 53=🌧️毛毛雨, 55=🌧️持續微雨
- 61=🌧️微雨, 63=🌧️大雨, 65=🌧️大雨, 80=🌦️驟雨, 95=⛈️雷暴

**風向轉換：** 度數 → 北風/東北風/東風/東南風/南風/西南風/西風/西北風

---

## 🖼️ 天氣 Banner 規則

**生成工具**: Pollinations.ai
- 比例: **16:9** (1920×1080)
- URL格式: `https://image.pollinations.ai/prompt/{prompt}?width=1920&height=1080&seed={random}&nologo=true`
- 根據天氣狀況選擇 prompt（維多利亞港 + 天氣描述）
- 加入 User-Agent header 避免403
- 儲存在: `reports/weather_banner_YYYYMMDD.png`

---

## 📰 新聞搜尋規則

**搜尋工具**: SearXNG (`/opt/data/searx_html_search.py`)
- URL: `http://searxng:8080/search`
- 搜尋輔助: `/opt/data/sono-repo/scripts/search_today_news.py`

**四大主題：**
1. **AI科技** — AI/artificial intelligence/ChatGPT/Claude/Gemini/machine learning
2. **太空宇宙** — SpaceX/NASA/astronomy/telescope/Mars/moon
3. **UFO外星人** — UFO/UAP/alien/unidentified/extraterrestrial
4. **超自然** — paranormal/supernatural/ghost/mystery/cryptid

**每個主題要求：**
- 最多5篇新聞
- 每篇必須真實、可驗證
- 如有圖片 → 用 `<img>` + 超連結方式顯示
- 自動去重
- HTML entities 解碼（避免亂碼）
- 標籤自動分類：突破(breakthrough)/趨勢(trend)/警示(alert)

---

## 📝 Sono 專欄規則

**3大標題：**
1. **🌍 世界趨勢** — 根據當日新聞世界大事編寫，簡單直白
2. **📡 蘇蘿預測** — 短期/中期/長期預測
3. **🔮 蘇蘿直覺** — 個人思想感受，加入自己觀察

**寫作風格：**
- 用粵語/繁體中文
- 簡單直白，唔好長篇大論
- 加入自己思想同觀察
- 每日內容必須唔同
- 配合當天天氣作結尾呼應

---

## 🧭 導航系統規則

**底部導航 Bar（上一日 | 首頁 | 下一日）：**
- 自動檢查前後日期頁面是否存在（前後30日範圍）
- 存在 → 顯示彩色連結
- 唔存在 → 顯示灰色文字（唔會link去404）
- 23日：上一日=灰色（最早），下一日=24日
- 最新一日：下一日=灰色（暫無）

**每次生成新日報時：**
- 更新新日報嘅導航（指向前面最近嘅日期）
- 更新前一日报嘅「下一日」連結（指向新日期）

---

## 🏠 首頁更新規則

**日報列表 (`.report-list`)：**
- 新日報卡片插入到列表最頂部
- 自動檢查避免重複
- 卡片格式：日期數字 + 日期中文 + 星期 + 新聞關鍵詞描述
- 描述從新聞標題提取（前15字）

---

## 🔧 Git 工作流程

1. `git config user.name/email` — 設定身份
2. `git pull --rebase origin main` — 確保同步
3. `git add reports/ index.html` — 加入變更
4. `git commit -m "每日自動更新：YYYYMMDD"` — 提交
5. `git push origin main` — 推送

**GitHub Pages 自動部署**，推送後1-2分鐘生效。

---

## ⏰ Cron Job 設定

- **Job ID**: `ea9af07ed35e`
- **名稱**: Sono 每日自動更新
- **排程**: `0 22 * * *`（UTC 22:00 = HKT 06:00）
- **模型**: qwen3.7-max@alibaba
- **通知**: 回報到 Telegram 群組

---

## 🔍 自動除錯功能

每次生成日報後，系統會自動運行除錯檢查，確保所有內容正確無誤。

**除錯腳本**: `/opt/data/sono-repo/scripts/sono_daily_validator.py`

**檢查項目**:
- ✅ 檔案存在性（日報 + Banner）
- ✅ 日期標題正確性
- ✅ 天氣數據完整性（溫度/濕度/風速/紫外線/能見度）
- ✅ Banner 圖片引用
- ✅ Sono 專欄3個部分（世界趨勢/蘇蘿預測/蘇蘿直覺）
- ✅ 新聞 Tabs 4個主題（AI/太空/UFO/超自然）
- ✅ 新聞卡片數量（建議15-25個）
- ✅ 導航系統連結（上一日/下一日是否指向存在嘅日期）
- ✅ Footer 文字
- ✅ HTML 結構完整性（div 標籤匹配）
- ✅ 首頁連結
- ✅ Git 狀態（有無未提交變更）

**輸出示例**:
```
======================================================================
Sono 每日除錯報告 - 20260701
生成時間: 2026-07-01 06:00:00
======================================================================

✅ 通過 23 項檢查:
  ✅ 日報檔案存在: sono_20260701.html (45231 bytes)
  ✅ Banner 圖片存在: weather_banner_20260701.png (123456 bytes)
  ✅ 日期標題正確: 2026年7月1日
  ...

⚠️ 發現 2 個警告:
  ⚠️ 新聞卡片數量偏少: 12（建議20個）
  ⚠️ Git 有 1 個未提交嘅變更

======================================================================
⚠️ 驗證通過（有警告）: 2 個警告
```

**自動執行**:
- 每次 `sono_daily_automation.py` 完成後自動運行
- 如果發現錯誤（❌），會顯示警告訊息
- 警告（⚠️）唔會中斷流程，但建議檢查

---

## ⚠️ 重要守則

1. **23日係骨架參考** — 所有新日報以23日HTML結構為模板
2. **只改內容不改結構** — 天氣/新聞/專欄內容每日更新，但HTML結構保持一致
3. **全繁體中文** — 所有內容用繁體中文/粵語
4. **直接 push** — Sono 網站改動直接 push，唔使確認
5. **圖片用連結方式** — 新聞圖片用 `<img src="URL">` 唔好下載到本地
6. **天氣 banner 16:9** — 嚴格使用 1920×1080 比例
7. **新聞必須真實** — 搜尋真實新聞，唔好虛構
8. **每日內容唔同** — 專欄/新聞每日都要獨特

---

## 📂 重要檔案路徑

| 檔案 | 路徑 |
|------|------|
| 自動化腳本 | `/opt/data/scripts/sono_daily_automation.py` |
| 新聞搜尋腳本 | `/opt/data/sono-repo/scripts/search_today_news.py` |
| 自動除錯腳本 | `/opt/data/sono-repo/scripts/sono_daily_validator.py` |
| SearXNG 搜尋 | `/opt/data/searx_html_search.py` |
| GitHub Token | `/opt/data/.gh_b64` |
| Repo | `/opt/data/sono-repo/` |
| 天氣 Banner | `/opt/data/sono-repo/reports/weather_banner_*.png` |
