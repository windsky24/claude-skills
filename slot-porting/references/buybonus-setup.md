# BuyBonus 設定指南

BuyBonus 功能讓玩家可以直接購買 Bonus Round，目前僅開放給 API 架構遊戲。

---

## Step 1：建立 BonusModel

路徑：`slotdb → BuyBonus → BonusModel`

新增一筆 Model，設定：
- 起始時間（StartTime）
- 結束時間（EndTime）
- 其他 Model 相關參數

---

## Step 2：設定 BonusInfo

路徑：`slotdb → BuyBonus → BonusInfo`

- 將遊戲的 BuyBonus 模式對應到 Step 1 建立的 Model
- **一種 BuyBonus 模式 → 對應一個 BonusModel**
- 若遊戲有多種購買模式，需分別建立對應

---

## Step 3：確認售價計算

確認幣值換算與總金額是否正確：

```
售價 = 押注金額 × CostMulti
```

---

## ⚠️ 常見錯誤

### 錯誤 1：404 Not Found
**原因**：SlotCommon 版本過舊，不含 BonusSpin 的新版實作
**解法**：更新 SlotCommon 到包含 BonusSpin 的版本

### 錯誤 2：BuyBonus 異常行為（如魔龍寶藏案例）
**原因**：`BuyBonusModel` 內的 `EnableJp` 設為 `True`
**解法**：將 `EnableJp` 改為 `False`

> 💡 如果遊戲有客製化 BonusSpin（如 SlotCommon 有特殊版本），需確認版本相容性

---

## 確認遊戲正確

設定完成後，在遊戲內確認：
1. BuyBonus 按鈕顯示正常
2. 各模式的價格計算正確
3. 購買後可正確進入 Bonus Round
4. Bonus 結果正常結算
