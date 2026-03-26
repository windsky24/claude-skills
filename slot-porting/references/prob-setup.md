# 機率設定指南（AW_Platform）

## 目錄結構

```
AW_Platform/
├── SlotChance/
│   └── AW/
│       └── SlotProb/
│           └── {GameName}/
│               ├── {GameName}Info.py      ← 機率詳細資料（含 ProbId）
│               ├── {GameName}InfoB.py     ← B 組機率（若有 A/B）
│               └── {GameName}Setting.py  ← 遊戲設定（押注段等）
├── InitProbTool.py   ← 機率初始化工具（一般架構）
└── pack_igaming_sssapi.py  ← API 架構打包工具
```

---

## A/B 機率架構說明

當遊戲有 2 款以上機率時，可透過 ProbSwitchSetting 設定 A/B 機率切換。

- **A 組**：預設機率（ProbId = 0 或指定值）
- **B 組**：第二組機率（ProbId = 1 或指定值）
- 可依地區、商戶指定使用哪組機率

### ProbId 對應關係

```
SlotGame → SlotGameInfo（含多筆，每筆有不同 ProbId）
     ↕
SlotLegi → ProbSwitchValue（地區/商戶 → ProbId 對應表）
     ↕
SlotLegi → ProbSwitchSetting（A/B 機率群組設定）
```

---

## 使用 InitProbTool_API 初始化機率

`InitProbTool_API` 工具會將 Python 機率設定檔寫入 slotdb。

```bash
# 在 AW_Platform 目錄下執行
python InitProbTool.py
```

或使用互動式工具選擇要初始化的遊戲和動作：
- `SlotGameInfo` — 寫入機率詳細資料
- `SlotGameSetting` — 寫入遊戲設定

---

## 機率檔案範例結構

### {GameName}Info.py
```python
GameInfo = [
    {
        'GameName': 'ChaChaCha',
        'ProbId': 0,
        # ... 機率相關參數
    },
    {
        'GameName': 'ChaChaCha',
        'ProbId': 1,
        # ... B 組機率參數
    }
]
```

### {GameName}Setting.py
```python
Setting = {
    'GameName': 'ChaChaCha',
    'cost': 1,
    # ... 押注設定
}
```

---

## 商戶指定機率（進階）

可為特定商戶指定使用 A 或 B 組機率：
- 路徑：`slotdb → SlotLegi → ProbSwitchValue`
- 使用 `Version` key 指定對應的商戶 ID
- 讓不同地區/商戶可以跑不同機率組合
