# Sono 網站完整架構保護紀錄（最終版）

**建立日期**：2026-06-29  
**版本**：v2.0（完整版）  
**目的**：萬一網站出問題，可靠呢份文件進行還原同修復

---

## 1. 網站基本資訊

| 項目 | 內容 |
|------|------|
| GitHub Repo | fung2222/sono |
| GitHub Pages | https://fung2222.github.io/sono |
| 主要檔案 | `index.html`（首頁） |
| 日報資料夾 | `reports/` |
| 遊戲資料夾 | `2048/`, `fighter/`, `rps-battle/` 等 |
| 工具箱分類 | 實用工具 / AI 工具 / 娛樂工具 |

---

## 2. 完整架構框架

### 2.1 三個主要 Tab（不可更改）

1. **每日資訊**（`tab-daily`）
   - 香港天氣
   - 日報列表（report-list）

2. **遊戲**（`tab-games`）
   - 所有小遊戲入口

3. **工具箱**（`tab-toolbox`）
   - 實用工具（12個）
   - AI 工具（3個）
   - 娛樂工具（6個）

### 2.2 Tab 切換函數（必須保留）

```js
function switchTab(tab) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
}
```

---

## 3. 工具箱完整列表（順序不可更改）

### 實用工具（🛠️）

| 序號 | 工具名稱 | Trigger ID | 狀態 |
|------|----------|------------|------|
| 1 | 全球天氣 | weatherTrigger | 正常 |
| 2 | 貨幣匯率 | currencyTrigger | 正常 |
| 3 | Sono 搜尋 | searchTrigger | 正常 |
| 4 | AI 翻譯 | translateTrigger | 正常 |
| 5 | ISS 追蹤 | issTrigger | 正常 |
| 6 | 世界時鐘 | worldClockTrigger | 正常 |
| 7 | QR Code 生成 | qrTrigger | 正常 |
| 8 | 世界地圖 | mapTrigger | 正常 |
| 9 | 番茄計時 | timerTrigger | 正常 |
| 10 | 網絡測速 | speedTestTrigger | 正常 |
| 11 | 計算機 | calculatorTrigger | 正常 |
| 12 | 農曆轉換 | lunarTrigger | 正常 |

### AI 工具（🤖）

| 序號 | 工具名稱 | Trigger ID | 狀態 |
|------|----------|------------|------|
| 1 | Sono Chat | sonoChatTrigger | 正常 |
| 2 | Sono 創作 | sonoCreateTrigger | 正常 |
| 3 | Sono 分析 | - | Coming Soon |

### 娛樂工具（🎪）

| 序號 | 工具名稱 | Trigger ID | 狀態 |
|------|----------|------------|------|
| 1 | 靈體探測 | ghostTrigger | 正常 |
| 2 | 命運輪盤 | wheelTrigger | 正常 |
| 3 | 反應挑戰 | reactTrigger | 正常 |
| 4 | 今日運勢 | fortuneTrigger | 正常 |
| 5 | 環境音效 | ambientTrigger | 正常 |
| 6 | 今日金句 | quoteTrigger | 正常 |

---

## 4. 關鍵檔案與路徑

### 4.1 GitHub 端

- **Repo**：`fung2222/sono`
- **首頁**：`index.html`
- **日報**：`reports/sono_YYYYMMDD.html`
- **黃金骨架**：`reports/sono_20260628.html`（**最重要**）

### 4.2 本地備份位置（重要）

| 位置 | 說明 |
|------|------|
| `/opt/data/sono_20260628.html` | 黃金骨架本地備份 |
| `/app/workspace/scripts/project-x-backup/` | Project X 備份 |
| GitHub Actions / Pages | 自動部署 |

### 4.3 還原時可用路徑

- GitHub repo 本身就是主要備份
- 可透過 `git checkout [commit]` 還原
- 可直接下載 `index.html` + `reports/` 資料夾還原

---

## 5. 日報系統鐵律（必須遵守）

- **唯一黃金骨架**：`sono_20260628.html`
- 所有新日報**只可替換文字**，不可改動 HTML 結構
- 必須保持 tag count = 652
- 上一日 / 下一日 navigation 必須正確連接
- 首頁日報列表必須有最新日期

---

## 6. JavaScript 修改守則（最重要）

### 6.1 禁止行為

- 使用正則大規模刪除 `<script>` 區塊
- 覆寫或刪除其他 Trigger 的事件
- 更改工具箱內 app 的 HTML 順序
- 更改遊戲列表順序
- 移除任何現有 Trigger 的事件綁定

### 6.2 正確做法

- 新增功能時，**只新增**，唔好刪除原有 script
- 修改前先備份 `index.html`
- 修改後必須測試所有 Tab 同工具是否正常

---

## 7. 還原步驟（出事時使用）

### 如果網站壞咗：

1. **最快方法**：
   - 去 GitHub repo → 搵之前正常嘅 commit
   - `git checkout [commit] -- index.html`
   - Push 返去

2. **如果 Tab 切換失效**：
   - 檢查 `switchTab` 函數是否存在
   - 重新加入 `switchTab` 函數

3. **如果工具/遊戲打唔開**：
   - 檢查對應 Trigger ID 嘅 `.onclick` 是否存在
   - 重新綁定事件

4. **如果日報列表冇最新日期**：
   - 檢查 `index.html` 入面 `report-list` 是否有最新日期

---

## 8. Cron 相關資訊

- **Sono 日報生成**：每日 6am HKT（cron job: bb303ed10bed）
- 使用模型：grok-4.3 @ xai-oauth
- 推送目標：Telegram Sono蘇蘿 群組 + GitHub Pages

---

## 9. 常見問題與解決方法

| 問題 | 可能原因 | 解決方法 |
|------|----------|----------|
| Tab 切換失效 | switchTab 函數遺失 | 重新加入 switchTab 函數 |
| 工具打唔開 | 事件綁定遺失 | 重新綁定 .onclick |
| 日報列表冇最新日期 | 手動刪除或未更新 | 手動加返最新 report-item |
| 彈窗排版錯位 | modal CSS 問題 | 使用標準 modal 模板 |
| 遊戲打唔開 | 遊戲 Trigger 事件遺失 | 檢查遊戲對應 Trigger |

---

## 10. 保護提示語（以後修改時使用）

**強烈建議**每次修改前先打呢句：

> 「讀取 Sono 架構紀錄」

我會即刻讀取呢份文件，確保唔會破壞現有結構。

---

**此文件為 Sono 網站最高保護紀錄，任何重大修改必須參考本文件。**
