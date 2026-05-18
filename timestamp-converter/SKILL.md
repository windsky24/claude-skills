---
name: timestamp-converter
description: >
  時間格式轉換工具。當用戶提到「Unix timestamp」、「時間戳」、「轉換時間」、「UTC 時間」、「台灣時間」、「時區轉換」、「epoch」時觸發。
  支援三種轉換：
  1. Unix timestamp → 台灣時間 (UTC+8) 或任意時區
  2. 台灣時間 (UTC+8) → Unix timestamp
  3. 任意時區時間互轉
  只要用戶給出時間數字或時間字串並要求轉換，就使用此 skill。
---

# Timestamp Converter

幫用戶做時間格式轉換，使用 Python `datetime` 標準庫，不需安裝額外套件。

## 使用腳本

所有轉換透過 `scripts/convert_time.py` 執行，用法：

```bash
python scripts/convert_time.py <mode> <input> [target_offset]
```

**mode 參數：**
- `ts2tw` — Unix timestamp → 台灣時間 (UTC+8)
- `tw2ts` — 台灣時間字串 → Unix timestamp
- `ts2tz` — Unix timestamp → 指定 UTC offset 時間
- `tz2ts` — 指定時區時間字串 → Unix timestamp

**input 格式：**
- timestamp: 純數字，如 `1778678759`
- 時間字串: `"2026-05-16 18:00:00"` (引號包起來避免空格問題)

**target_offset 格式（ts2tz / tz2ts 時使用）：**
- UTC offset 小時數，如 `8`（UTC+8）、`-5`（UTC-5）、`0`（UTC）

## 常見用法範例

使用 Python 3.12 執行（系統預設 python 為 2.7，請指定完整路徑）：

**Unix timestamp → 台灣時間：**
```powershell
C:\Users\billywang\AppData\Local\Programs\Python\Python312\python.exe scripts/convert_time.py ts2tw 1778678759
```

**台灣時間 → Unix timestamp：**
```powershell
C:\Users\billywang\AppData\Local\Programs\Python\Python312\python.exe scripts/convert_time.py tw2ts "2026-05-16 18:00:00"
```

**Unix timestamp → 指定時區（例如 UTC）：**
```powershell
C:\Users\billywang\AppData\Local\Programs\Python\Python312\python.exe scripts/convert_time.py ts2tz 1778678759 0
```

**指定時區時間 → Unix timestamp（例如 UTC+9）：**
```powershell
C:\Users\billywang\AppData\Local\Programs\Python\Python312\python.exe scripts/convert_time.py tz2ts "2026-05-16 19:00:00" 9
```

## 輸出格式

輸出結果直接告訴用戶，格式清楚易讀：

- timestamp 轉時間：`2026-05-13 21:25:59 (UTC+8)`
- 時間轉 timestamp：`1778925600`

## 執行腳本後的回應方式

1. 執行腳本取得結果
2. 用中文清楚回報答案
3. 如果用戶同時問多個轉換，一次列出全部結果
