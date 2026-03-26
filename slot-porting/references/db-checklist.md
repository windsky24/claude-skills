# DB 上線確認 — 詳細步驟

## 1. gamedb 設定

### 1.1 確認遊戲加入大廳
路徑：`gamedb → Lobby → Stage`
- 確認遊戲名稱（GameName）已存在於 Stage collection
- 若無則新增，可參考同類遊戲格式複製後修改 GameName

### 1.2 確認單一押注段設定
路徑：`gamedb → MainGame → FixedTotalBetCategory`
- 確認遊戲是否有加入單一押注段
- 有需要固定押注金額的遊戲才需設定

### 1.3 SlotGameInfo（pixiu 遊戲專用）
路徑：`gamedb → SlotGame → SlotGameInfo`
- 僅 pixiu 架構遊戲需要設定
- 可複製同類遊戲的設定後修改 GameName

### 1.4 SlotGameSetting（pixiu 遊戲專用）
路徑：`gamedb → SlotGame → SlotGameSetting`
- 僅 pixiu 架構遊戲需要設定

---

## 2. slotdb 設定（API 架構遊戲）

> ⚠️ 舊版 slotdb 的 SlotGameInfo/SlotGameSetting 已棄用，改用 A/B 機率架構

### 2.1 EnableGame — 開啟遊戲功能
路徑：`slotdb → SlotLegi → FunctionSwitchSetting`
- 找到 `EnableGame` 欄位，將遊戲名稱加入 array
- 沒有此設定遊戲無法被呼叫

### 2.2 SlotMachine — 遊戲基本資訊
路徑：`slotdb → SlotLegi → SlotMachine`
新增一筆資料，包含：
- `GameName` — 遊戲名稱（大小寫需一致）
- `CodeName` — 遊戲代碼（通常小寫）
- `GameUrl` — 遊戲進入點 URL

### 2.3 ProbSwitchSetting — A/B 機率基本設定
路徑：`slotdb → SlotLegi → ProbSwitchSetting`
- 設定遊戲的 A/B 機率群組
- 每個機率組對應一個 ProbId

### 2.4 ProbSwitchValue — 地區對應機率
路徑：`slotdb → SlotLegi → ProbSwitchValue`（或同 collection 內）
- 確認各地區 ID 所對應的 ProbId 正確
- 可指定商戶的 A/B 機率，使用 Version key 指定

### 2.5 SlotGameInfo — 遊戲機率詳細資訊
路徑：`slotdb → SlotGame → SlotGameInfo`
- 含 ProbId 的遊戲機率詳細設定
- 每個 ProbId 對應一筆機率資料
- 由 InitProbTool_API 工具初始化

### 2.6 SlotGameSetting（非必要）
路徑：`slotdb → SlotGame → SlotGameSetting`
- 非每款遊戲都需要，視遊戲需求設定

---

## 3. platformdb 設定（新遊戲必填）

### 3.1 GameInfo — 活動相關遊戲資訊
路徑：`platformdb → GameInfo`（PlatformDB）
- 新遊戲必須加入
- 虎機（Slot）與魚機（Fish）參數格式不同
- 建議複製同類遊戲設定後修改 GameName

### 3.2 KioskBufferSetting — Kiosk 快取設定
路徑：`platformdb → KioskBufferSetting`（PlatDB）
- **新遊戲必填**，沒有此設定 Kiosk 端會異常
- 對應欄位：`GameName`

---

## 快速確認 Checklist（複製使用）

```
API 遊戲上線 DB 確認清單
遊戲名稱：_______________
版本 Tag：_______________
日期：_______________

[ ] gamedb → Lobby → Stage
[ ] gamedb → MainGame → FixedTotalBetCategory
[ ] slotdb → SlotLegi → FunctionSwitchSetting (EnableGame)
[ ] slotdb → SlotLegi → SlotMachine
[ ] slotdb → SlotLegi → ProbSwitchSetting
[ ] slotdb → SlotLegi → ProbSwitchValue
[ ] slotdb → SlotGame → SlotGameInfo (由 InitProbTool 處理)
[ ] platformdb → GameInfo
[ ] platformdb → KioskBufferSetting
[ ] BuyBonus (若需要)
```
