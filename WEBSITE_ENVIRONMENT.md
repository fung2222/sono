# Sono 網站環境記錄

## 📁 倉庫結構

```
fung2822/sono/
├── index.html                    # 首頁（2918行）
├── games/
│   ├── all.html                  # 遊戲庫主頁面（128行）
│   └── improved/
│       └── preview.html
├── reports/
│   ├── index.html                # 歷史日報列表（75行）
│   ├── sono_20260623.html        # 6月23日日報（已鎖定）
│   ├── sono_20260624.html        # 6月24日日報（已鎖定）
│   ├── sono_20260625.html        # 6月25日日報（已鎖定）
│   ├── sono_20260626.html        # 6月26日日報（已鎖定）
│   ├── sono_20260627.html        # 6月27日日報（已鎖定）
│   ├── sono_20260628.html        # 6月28日日報（已鎖定）
│   ├── sono_20260629.html        # 6月29日日報（已鎖定）
│   ├── sono_20260630.html        # 6月30日日報（已鎖定）
│   └── sono_20260701.html        # 7月1日日報（已鎖定）
├── 2048/                         # 2048 遊戲
├── ai-fighter/                   # AI 格鬥遊戲
├── fighter/                      # 火柴人格鬥
├── memory/                       # 記憶配對遊戲
├── rps-battle/                   # 剪刀石頭佈
├── snake/                        # 貪食蛇
├── stickman-fighter-v1/          # Stickman Fighter v1
├── tictactoe/                    # 井字遊戲
├── tools/
│   └── currency-converter.html   # 貨幣轉換工具
├── images/                       # 圖片資源
├── scripts/                      # 腳本檔案
└── backups/                      # 備份
```

## 🎯 核心功能

### 1. 每日日報系統
- **執行時間**：每日 HKT 06:00
- **自動化腳本**：`/opt/data/sono-repo/scripts/sono_daily_automation.py`
- **搜尋工具**：`/opt/data/searx_html_search.py`
- **驗證腳本**：`/opt/data/sono_daily_validator.py`

### 2. 日報內容結構
每個日報包含：
- 🌡️ **天氣數據**：OpenMeteo API（真實歷史/當日數據）
- 🖼️ **天氣 Banner**：Pollinations.ai 生成（16:9, 1920x1080）
- 📰 **新聞搜尋**：4大主題（AI科技、太空宇宙、UFO/外星人、超自然）
- 📝 **專欄**：粵語寫作（世界趨勢、蘇蘿預測、蘇蘿直覺）
- 🧭 **底部導航**：上一日 / 首頁 / 下一日

### 3. 導航樣式規則
**底部導航按鈕**：
- **上一日/下一日**：透明背景 + 紫色邊框 + 紫色文字（outline style）
  ```css
  style="color:#a29bfe;text-decoration:none;font-size:0.78em;padding:4px 12px;border:1px solid #333;border-radius:16px;display:inline-flex;align-items:center;gap:2px;transition:all 0.3s"
  ```
- **首頁**：漸變背景（粉紅→紫）+ 白字（主按鈕突出）
  ```css
  style="background:linear-gradient(135deg,#ff6b9d,#a29bfe);color:#fff;text-decoration:none;font-size:1.1em;padding:5px 28px;border-radius:22px;font-weight:700;letter-spacing:2px;line-height:1.2"
  ```

## 🎮 遊戲庫管理

### 遊戲列表（games/all.html）
**經典遊戲**：
- 貪食蛇（snake/）
- 2048（2048/）

**對戰遊戲**：
- 火柴人格鬥（fighter/）
- Stickman Fighter（stickman-fighter-v1/）
- 剪刀石頭佈（rps-battle/）
- 井字遊戲（tictactoe/）

**益智遊戲**：
- 記憶配對（memory/）

**其他**：
- AI 格鬥（ai-fighter/）

### 添加新遊戲流程
1. 在倉庫根目錄創建遊戲資料夾（如 `new-game/`）
2. 放置 `index.html` 在遊戲資料夾內
3. 創建 SVG logo（如 `new-game.svg`）放在 `games/` 目錄
4. 在 `games/all.html` 添加卡片：
   ```html
   <a href="../new-game/" class="game-card">
     <img src="new-game.svg" class="game-logo" alt="遊戲名稱">
     <div class="game-name">遊戲名稱</div>
     <div class="game-tag">分類標籤</div>
   </a>
   ```
5. 分類：經典 / 對戰 / 益智 / AI

## 🛠️ 工具箱管理

### 工具列表（tools/）
- **貨幣轉換器**：`tools/currency-converter.html`

### 添加工具流程
1. 在 `tools/` 目錄創建 HTML 檔案
2. 在首頁 `index.html` 的「工具箱」區域添加入口
3. 保持深色主題風格（#0a0a1a 背景）

## 📊 首頁結構（index.html）

### 主要區域
1. **Header**：Logo + 日期
2. **天氣預覽**：當日天氣摘要
3. **日報卡片**：最新日報入口（自動更新）
4. **遊戲庫**：遊戲入口網格
5. **工具箱**：實用工具列表
6. **Footer**：版權資訊

### 日報卡片自動更新
每日自動化腳本會：
1. 生成新日報 HTML
2. 在首頁插入新卡片（最頂部）
3. 更新 `reports/index.html` 歷史列表
4. 調整前一日的「下一日」導航連結

## 🔒 已鎖定內容（23日-7月1日）

以下日報**不再改動**：
- ✅ 新聞內容（全部中文翻譯）
- ✅ 天氣數據
- ✅ 專欄內容
- ✅ 底部導航樣式
- ✅ 首頁卡片排序
- ✅ 歷史頁面列表

## 📝 未來擴展指引

### 添加遊戲
```
1. 創建遊戲資料夾：new-game/index.html
2. 創建 logo：games/new-game.svg
3. 在 games/all.html 添加卡片（按分類）
4. Git commit + push
```

### 添加工具
```
1. 創建工具頁面：tools/new-tool.html
2. 在 index.html 工具箱區域添加入口
3. 保持深色主題一致性
4. Git commit + push
```

### 維護守則
- 每日日報自動生成（HKT 06:00）
- 新聞必須是中文（SearXNG 搜尋）
- 導航樣式統一（outline 風格）
- 驗證腳本自動檢查（28項）
- 所有變更必須 Git push

---

**最後更新**：2026年7月1日  
**維護者**：Hermes AI Agent  
**版本**：v1.0（23日-7月1日鎖定版）
