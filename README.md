# Claude Skills — F:\Claude_Skill

這個目錄存放自訂的 Claude Code Skills，以 Git 做版本控制。

## 📂 目錄結構

```
Claude_Skill/
├── bookmark-checker/        # 書籤掃描工具
│   ├── SKILL.md             # Skill 描述與使用說明
│   └── scripts/
│       └── check_bookmarks.py  # 主程式
├── slot-porting/            # Slot 移植工具
│   └── SKILL.md
└── README.md
```

## 🛠️ Skills 清單

| Skill | 說明 | 觸發詞 |
|-------|------|--------|
| `bookmark-checker` | 掃描 Chrome 書籤，測試 URL 存活狀態，產生 HTML 報告 | 掃描書籤、整理書籤、check bookmarks |
| `slot-porting` | Slot 遊戲移植工具 | — |

## 🚀 如何安裝 Skill

```bash
# 在 Claude Code 中輸入：
/install-skill F:\Claude_Skill\bookmark-checker
```

或直接封裝成 .skill 分享：

```bash
cd <skill-creator目錄>
PYTHONUTF8=1 python -m scripts.package_skill F:\Claude_Skill\bookmark-checker
```

## 📝 版本紀錄

使用 `git log --oneline` 查看所有變更。
