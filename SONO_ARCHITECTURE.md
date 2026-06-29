# Sono 網站架構紀錄（嚴格保護版）

**建立日期**：2026-06-29  
**目的**：防止日後修改時破壞首頁結構、工具箱排序、遊戲功能及 JavaScript 事件綁定。

---

## 1. 整體結構鐵律

Sono 網站只接受 **三個主要 Tab**：

| Tab | ID | 說明 |
|-----|----|------|
| 每日資訊 | `tab-daily` | 日報列表 + 香港天氣 |
| 遊戲 | `tab-games` | 所有小遊戲 |
| 工具箱 | `tab-toolbox` | 實用工具 + AI 工具 + 娛樂工具 |

**嚴禁**：
- 新增第 4 個 Tab
- 更改三個 Tab 的順序
- 刪除或重命名 Tab ID

---

## 2. 工具箱分類與順序（不可更改）

### 2.1 實用工具（🛠️ 實用工具）

目前順序（**嚴禁更改排序**）：

1. 全球天氣
2. 貨幣匯率
3. Sono 搜尋
4. AI 翻譯
5. ISS 追蹤
6. 世界時鐘
7. QR Code 生成
8. 世界地圖
9. 番茄計時
10. 網絡測速
11. 計算機
12. 農曆轉換

### 2.2 AI 工具（🤖 AI 工具）

1. Sono Chat
2. Sono 創作
3. Sono 分析（Coming Soon）

### 2.3 娛樂工具（🎪 娛樂工具）

1. 靈體探測
2. 命運輪盤
3. 反應挑戰
4. 今日運勢
5. 環境音效
6. 今日金句

**嚴禁**：
- 改變以上任何工具的順序
- 隨意新增工具而破壞 4 欄排版
- 刪除現有工具的 HTML 結構

---

## 3. JavaScript 事件綁定規則

所有工具和遊戲**必須**使用以下模式：

```js
document.getElementById('xxxTrigger').onclick = function() {
  // 建立 modal 的 HTML
  const m = document.createElement('div');
  m.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:99999;';
  m.innerHTML = `...`;
  document.body.appendChild(m);
  m.onclick = e => { if (e.target === m) m.remove(); };
};
```

**嚴禁**：
- 使用全域 `onclick` 屬性
- 刪除整個 `<script>` 區塊
- 覆寫其他 Trigger 的事件

---

## 4. Tab 切換功能（switchTab）

必須保留以下函數：

```js
function switchTab(tab) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
}
```

---

## 5. 日報系統鐵律（已存在，不可違反）

- `sono_20260628.html` 為唯一黃金骨架
- 所有新日報只可替換文字，不可改動 HTML 結構
- 必須保持 tag count = 652
- 上一日 / 下一日 navigation 必須正確連接

---

## 6. 修改守則（重要）

**修改前必須檢查**：
1. 是否有完整備份
2. 是否只新增功能，而非刪除原有 script
3. 是否測試過 Tab 切換正常
4. 是否測試過所有現有工具和遊戲仍可打開

**禁止行為**：
- 使用正則大規模刪除 `<script>` 區塊
- 更改工具箱內 app 的 HTML 順序
- 更改遊戲列表的順序
- 移除任何現有 Trigger 的事件綁定

---

## 7. 目前已確認正常功能（2026-06-29）

- 三個 Tab 切換正常
- 計算機、網絡測速、農曆轉換功能正常
- 其餘工具及遊戲功能正常（還原後狀態）

---

**此文件為 Sono 網站最高保護紀錄，任何修改必須遵守以上規則。**
