---
name: slot-porting
description: |
  AW Slot 遊戲設定移植與上線流程的全方位助手。處理 API 架構老虎機遊戲從下載、錯誤修正、機率設定、打包部署到 DB 設定確認的完整工作流程。

  觸發時機：
  - 提到「移植」、「porting」、「slot 遊戲」、「老虎機」、「新遊戲上線」
  - 提到 PackToReview、Docker 部署、BuildGameImage
  - 提到 AW_Slot 或 AW_Platform 目錄的工作
  - 提到 slotdb、gamedb、platformdb 的設定確認
  - 提到 InitProbTool、機率設定、A/B 機率、ProbSwitchSetting
  - 提到 BuyBonus 設定、FunctionSwitchSetting、SlotMachine
  - 詢問「快測」、「品檢」、「測試機部署」、「DB 上線確認」
  - 任何涉及老虎機遊戲設定移植、快速測試、品質檢測的任務

  使用此 skill 完成所有 slot 遊戲移植相關任務，即使用戶只描述其中一個環節。
---

# Slot 遊戲設定移植 Skill

## 目錄結構

- **AW_Slot/** — 遊戲主程式目錄（API 架構老虎機）
  - `{GameName}/` — 各遊戲資料夾（含 PackToReview.py、Docker/、Game/）
  - `SlotCommon/` — 共用模組
  - `SlotServer/` — 伺服器模組
- **AW_Platform/** — 機率設定與驗證工具
  - `SlotChance/AW/SlotProb/` — AW 遊戲機率設定
  - `InitProbTool.py` — 機率初始化工具

---

## 完整移植流程（4 個階段）

依需求，可執行全流程或單一階段。開始前先確認遊戲名稱（GameName）和版本 Tag。

---

### 階段 1 — 遊戲下載與錯誤修正

**目標**：取得指定版本的遊戲原始碼並確保可正常執行。

1. **使用 Sublime Merge 下載遊戲**（或 git clone）
   - 下載 3 個主要 repository：
     - `{GameName}` — 遊戲主程式
     - `SlotCommon` — 共用邏輯模組
     - `SlotServer` — 伺服器模組
   - 指定對應的 branch/tag

2. **排除錯誤**
   - 執行遊戲確認無 import 錯誤、語法錯誤
   - 常見問題：SlotCommon 版本不含新功能（如 BonusSpin）→ 更新 SlotCommon 版本

3. **更新機率設定**（AW_Platform）
   - 在 `AW_Platform/SlotChance/AW/SlotProb/{GameName}/` 更新對應的機率 py 檔
   - 使用 `InitProbTool.py` 或 `InitProbTool_API` 初始化機率資料

> 詳細機率設定流程請參考 `references/prob-setup.md`

---

### 階段 2 — 打包與快測部署

**目標**：打包遊戲並部署到測試機執行 Docker 服務。

#### Step 1：打包（PackToReview.py）

```bash
# 在 AW_Slot/{GameName}/ 目錄下執行
python PackToReview.py
# 輸入 Tag 名稱（例如：1.0.3）
# 產出：GameSend/{GameName}-{tag}/ 內含 3 個 .tar.gz 檔案
```

PackToReview.py 會自動完成：
- git clone 指定 tag 的 3 個 repo
- 刪除 .git 資料夾與 Docker 資料夾
- 轉換檔案為 CRLF 格式
- 計算 SHA1.csv 校驗檔
- 打包成 `{GameName}.tar.gz`、`SlotCommon.tar.gz`、`SlotServer.tar.gz`

#### Step 2：上傳到跳板機

使用 **WinSCP** 上傳 3 個 `.tar.gz` 到跳板機個人家目錄

#### Step 3：從跳板機複製到測試機

```bash
# 在跳板機執行
scp {GameName}.tar.gz SlotCommon.tar.gz SlotServer.tar.gz macross-slot-01-test:~

# ssh 登入測試機，複製到遊戲目錄
sudo cp ~/*.tar.gz ./
```

#### Step 4：建立 Docker Image

```bash
bash Docker/BuildGameImage.sh \
  {GameName}.tar.gz SlotCommon.tar.gz SlotServer.tar.gz \
  {codename} {version} Dockerfile
```

#### Step 5：啟動服務

```bash
# 確認 image 已建立
sudo docker images

# 啟動服務（TAG 填入版本號）
sudo TAG={version} docker compose -f ./Docker/docker-compose.yml up -d

# 更新服務前需先停止
sudo TAG={version} docker compose -f ./Docker/docker-compose.yml down
```

#### Step 6：測試驗證

- 開啟測試網頁，確認遊戲可正常進入、旋轉
- 確認 Log 無異常：`sudo tail -f /var/log/syslog`
- 查看特定服務 Log：`sudo docker logs docker-{codename}-1`

> 常用 Docker 指令請參考 `references/docker-commands.md`

---

### 階段 3 — DB 設定確認（上線前品檢）

**目標**：確認所有資料庫設定正確，符合上線文件規範。

> 詳細 DB 設定步驟請參考 `references/db-checklist.md`

**快速確認清單**：

#### gamedb（所有遊戲）
- [ ] `Lobby → Stage` — 遊戲已加入大廳
- [ ] `MainGame → FixedTotalBetCategory` — 單一押注段設定
- [ ] `SlotGame → SlotGameInfo` — GameInfo（pixiu 遊戲專用）
- [ ] `SlotGame → SlotGameSetting` — GameSetting（pixiu 遊戲專用）

#### slotdb（API 架構遊戲）
- [ ] `SlotLegi → FunctionSwitchSetting` — EnableGame 加入遊戲名稱
- [ ] `SlotLegi → SlotMachine` — 遊戲資訊（GameName、CodeName、GameUrl）
- [ ] `SlotLegi → ProbSwitchSetting` — A/B 機率基本設定
- [ ] `SlotLegi → ProbSwitchValue` — 確認地區 ID 對應的 ProbId
- [ ] `SlotGame → SlotGameInfo` — 含 ProbId 的遊戲資訊
- [ ] `SlotGame → SlotGameSetting` — 遊戲設定（非必要）

#### platformdb（新遊戲必填）
- [ ] `GameInfo` — 針對活動的遊戲資訊（虎機/魚機參數不同）
- [ ] `KioskBufferSetting` — 新遊戲必須加入，對應 GameName

---

### 階段 4 — BuyBonus 設定（選填）

僅在遊戲需要開放 BuyBonus 功能時執行。

> 詳細設定步驟請參考 `references/buybonus-setup.md`

**快速步驟**：
1. `slotdb → BuyBonus → BonusModel` — 建立 Model（設定起始/結束時間）
2. `slotdb → BuyBonus → BonusInfo` — 設定遊戲對應的 BuyBonus（一種模式一個 Model）
3. 確認售價計算：`售價 = 押注金額 × CostMulti`
4. 注意：`EnableJp` 設定錯誤會造成問題，預設應為 `False`

---

## 常見問題排查

| 問題 | 原因 | 解法 |
|------|------|------|
| 404 Not Found | SlotCommon 版本不含 BonusSpin | 更新 SlotCommon 到含新版的 branch |
| BuyBonus 異常（如魔龍寶藏） | BuyBonusModel 的 EnableJp 設為 True | 將 EnableJp 改為 False |
| Docker image 啟動失敗 | Log 檔或舊設定檔未清除 | 清除 Log 並確認設定檔正確後重建 |
| 機率設定未生效 | ProbId 未對應 | 確認 SlotGameInfo 的 ProbId 與 ProbSwitchValue 一致 |

---

## 使用工具

| 工具 | 用途 |
|------|------|
| Sublime Merge | 下載/管理 git repo |
| WinSCP | 上傳檔案到跳板機 |
| InitProbTool_API | 初始化機率到 slotdb |
| Docker Compose | 管理測試機服務 |
| MongoDB (Robo 3T / Compass) | 設定/確認 DB 資料 |
