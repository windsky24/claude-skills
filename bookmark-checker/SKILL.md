---
name: bookmark-checker
description: >
  Scan and audit Chrome bookmarks to check which URLs are still alive or broken,
  then generate a beautiful HTML report. Use this skill whenever the user wants to:
  - Check / scan / test their Chrome bookmarks
  - Find broken, dead, or invalid bookmark links
  - Organize or audit browser bookmarks
  - Generate a bookmark health report
  - Clean up their bookmarks list
  Trigger on phrases like: "整理書籤", "掃描書籤", "檢查書籤", "書籤失效", "check bookmarks",
  "scan bookmarks", "audit bookmarks", "find broken links", "bookmark report",
  "which bookmarks are dead", "clean up bookmarks".
  Always use this skill when Chrome bookmarks and URL-checking are mentioned together.
---

# Bookmark Checker Skill

Scan the user's Chrome bookmarks, test each URL for availability, and produce a
polished HTML report (saved to the Desktop) with filterable results.

## Step-by-step workflow

### 1. Locate the Chrome Bookmarks file

Auto-detect based on OS:

| OS | Path |
|----|------|
| Windows | `C:\Users\<USERNAME>\AppData\Local\Google\Chrome\User Data\Default\Bookmarks` |
| macOS | `~/Library/Application Support/Google/Chrome/Default/Bookmarks` |
| Linux | `~/.config/google-chrome/Default/Bookmarks` |

Use `Bash` to find the username and verify the file exists:

```bash
# Windows — find Python home dir
python -c "import os; print(os.path.expanduser('~'))"
```

**Windows Python path** (check common locations):
- `C:\Users\<USER>\AppData\Local\Programs\Python\Python3xx\python.exe`
- `py` launcher if available

### 2. Run the checker script

The script lives next to this SKILL.md at `scripts/check_bookmarks.py`.
Find its absolute path, then run:

```bash
PYTHON="<path_to_python3>"
SKILL_DIR="<directory_containing_this_SKILL.md>"
BOOKMARKS="<path_to_Chrome_Bookmarks_file>"
OUTPUT="<Desktop_path>/bookmark_report.html"

PYTHONUTF8=1 "$PYTHON" "$SKILL_DIR/scripts/check_bookmarks.py" \
  --bookmarks "$BOOKMARKS" \
  --output "$OUTPUT" \
  --threads 20 \
  --timeout 10
```

**Desktop paths:**
- Windows: `C:\Users\<USERNAME>\Desktop`
- macOS/Linux: `~/Desktop`

> `PYTHONUTF8=1` is important on Windows to prevent emoji encoding errors.

### 3. Report the results to the user

After the script finishes it prints a summary like:

```
✅ 存活 (Alive):   312
❌ 失效 (Dead):     87
⚠️  需確認 (Check): 14
📊 Total:           413
📄 報告已儲存: C:\Users\...\Desktop\bookmark_report.html
```

Tell the user:
- Total bookmarks scanned
- How many are alive / dead / need checking
- Where the HTML report was saved
- Suggest they open the report in Chrome to use the filter + search features

### 4. Error handling

| Problem | Action |
|---------|--------|
| Bookmarks file not found | Ask which Chrome profile they use (Default / Profile 1 / etc.) |
| Python not found | Ask user to install Python 3; check `py --version` on Windows |
| UnicodeEncodeError | Add `PYTHONUTF8=1` before the command |
| Script not found | Confirm the skill's directory path is correct |

## Output format

The HTML report includes:
- **Stats cards** — total / alive / dead / needs-checking counts
- **Filter buttons** — All / ✅ Alive / ❌ Dead / ⚠️ Check
- **Search box** — filter by bookmark name or URL in real time
- **Folder grouping** — bookmarks grouped by Chrome folder hierarchy
- **Color-coded rows** — green / red / yellow per status
- Each row shows: name, clickable URL, HTTP status code, response time, error reason

## Technical notes

- HEAD request first (fast), falls back to GET if HEAD returns 405
- 20 concurrent threads — typically finishes 400+ bookmarks in 1–3 minutes
- Per-URL timeout: 10 seconds (configurable via `--timeout`)
- HTTP 3xx redirects → counted as ✅ alive (content still reachable)
- Private/internal IPs (192.168.x, 10.x, 172.16-31.x, localhost, 127.x) → auto ⚠️
- Report is self-contained HTML (no external CDN) — works fully offline
