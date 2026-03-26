#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Bookmark Checker
Scans all Chrome bookmarks, tests each URL, and generates an HTML report.

Usage:
    python check_bookmarks.py --bookmarks <path> --output <report.html>
    python check_bookmarks.py --bookmarks <path> --output <report.html> --threads 20 --timeout 10

Windows tip: run with PYTHONUTF8=1 to avoid encoding errors on Chinese Windows.
"""

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urlparse
import urllib.request
import urllib.error
import ssl

# Fix Windows console encoding for Unicode / emoji output
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# ── Helpers ────────────────────────────────────────────────────────────────────

def is_private_ip(url: str) -> bool:
    """Return True if URL points to a private/internal address."""
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return False
    private_patterns = [
        r"^192\.168\.", r"^10\.", r"^172\.(1[6-9]|2\d|3[01])\.",
        r"^127\.", r"^localhost$", r"^0\.0\.0\.0$",
    ]
    return any(re.match(p, host) for p in private_patterns)


def extract_bookmarks(node: dict, folder_path: str = "") -> list:
    """Recursively extract all bookmarks from the Chrome bookmarks JSON tree."""
    results = []
    name = node.get("name", "")
    node_type = node.get("type", "")

    if node_type == "url":
        url = node.get("url", "")
        if url and url.startswith("http"):
            results.append({
                "name": name,
                "url": url,
                "folder": folder_path or "書籤列",
            })
    elif node_type == "folder" or "children" in node:
        new_path = f"{folder_path} / {name}".strip(" /") if name else folder_path
        for child in node.get("children", []):
            results.extend(extract_bookmarks(child, new_path))
    return results


def load_bookmarks(bookmarks_path: str) -> list:
    """Load and parse the Chrome Bookmarks JSON file."""
    with open(bookmarks_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    roots = data.get("roots", {})
    all_bookmarks = []
    for root_name, root_node in roots.items():
        if isinstance(root_node, dict):
            all_bookmarks.extend(extract_bookmarks(root_node, ""))
    return all_bookmarks


# ── URL Testing ────────────────────────────────────────────────────────────────

def check_url(bookmark: dict, timeout: int = 10) -> dict:
    """Test a single URL and return status info."""
    url = bookmark["url"]
    result = bookmark.copy()

    # Private IPs — skip live check
    if is_private_ip(url):
        result.update({"status": "warn", "code": "內網", "elapsed": 0,
                        "reason": "Private / internal address"})
        return result

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    start = time.time()
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; BookmarkChecker/1.0)"},
                method=method,
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                code = resp.status
                elapsed = round((time.time() - start) * 1000)
                if 200 <= code < 400:
                    result.update({"status": "ok", "code": str(code), "elapsed": elapsed, "reason": ""})
                else:
                    result.update({"status": "warn", "code": str(code), "elapsed": elapsed,
                                    "reason": f"HTTP {code}"})
                return result
        except urllib.error.HTTPError as e:
            code = e.code
            elapsed = round((time.time() - start) * 1000)
            if code == 405 and method == "HEAD":
                continue  # retry with GET
            if 400 <= code < 500:
                result.update({"status": "warn", "code": str(code), "elapsed": elapsed,
                                "reason": f"HTTP {code}"})
            else:
                result.update({"status": "dead", "code": str(code), "elapsed": elapsed,
                                "reason": f"HTTP {code}"})
            return result
        except Exception as e:
            if method == "HEAD":
                continue
            elapsed = round((time.time() - start) * 1000)
            msg = str(e)[:80]
            result.update({"status": "dead", "code": "ERR", "elapsed": elapsed, "reason": msg})
            return result

    result.update({"status": "dead", "code": "ERR", "elapsed": 0, "reason": "All methods failed"})
    return result


def check_all(bookmarks: list, threads: int = 20, timeout: int = 10) -> list:
    """Check all bookmarks concurrently with a progress indicator."""
    total = len(bookmarks)
    results = []
    done = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_url, bm, timeout): bm for bm in bookmarks}
        for future in as_completed(futures):
            done += 1
            pct = int(done / total * 50)
            bar = "█" * pct + "░" * (50 - pct)
            print(f"\r[{bar}] {done}/{total}", end="", flush=True)
            results.append(future.result())

    print()  # newline after progress bar
    return results


# ── HTML Report ────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>書籤健康報告 · Bookmark Health Report</title>
<style>
  :root {
    --ok: #16a34a; --ok-bg: #dcfce7;
    --dead: #dc2626; --dead-bg: #fee2e2;
    --warn: #d97706; --warn-bg: #fef3c7;
    --bg: #f8fafc; --card: #ffffff;
    --border: #e2e8f0; --text: #1e293b;
    --muted: #64748b;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); padding: 24px; }
  h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 4px; }
  .subtitle { color: var(--muted); font-size: 0.9rem; margin-bottom: 24px; }

  .stats { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px;
          padding: 16px 24px; flex: 1; min-width: 120px; text-align: center; }
  .card .num { font-size: 2rem; font-weight: 700; }
  .card .lbl { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
  .card.ok   .num { color: var(--ok); }
  .card.dead .num { color: var(--dead); }
  .card.warn .num { color: var(--warn); }

  .controls { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
  .btn { padding: 8px 18px; border-radius: 8px; border: 1px solid var(--border);
         cursor: pointer; font-size: 0.85rem; background: var(--card);
         transition: all .15s; font-weight: 500; }
  .btn:hover { background: var(--border); }
  .btn.active { background: var(--text); color: #fff; border-color: var(--text); }
  #search { flex: 1; min-width: 200px; padding: 8px 14px; border-radius: 8px;
            border: 1px solid var(--border); font-size: 0.9rem; }

  .folder { margin-bottom: 24px; }
  .folder-title { font-size: 0.95rem; font-weight: 600; color: var(--muted);
                  text-transform: uppercase; letter-spacing: .05em;
                  margin-bottom: 8px; }
  table { width: 100%; border-collapse: collapse; background: var(--card);
          border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }
  thead { background: var(--bg); }
  th { padding: 10px 14px; text-align: left; font-size: 0.8rem; color: var(--muted);
       font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
  td { padding: 10px 14px; font-size: 0.87rem; border-top: 1px solid var(--border);
       vertical-align: middle; }
  tr.ok   td:first-child { border-left: 3px solid var(--ok); }
  tr.dead td:first-child { border-left: 3px solid var(--dead); }
  tr.warn td:first-child { border-left: 3px solid var(--warn); }
  .badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px;
           border-radius: 99px; font-size: 0.78rem; font-weight: 600; }
  .badge.ok   { background: var(--ok-bg);   color: var(--ok); }
  .badge.dead { background: var(--dead-bg); color: var(--dead); }
  .badge.warn { background: var(--warn-bg); color: var(--warn); }
  .url-cell a { color: var(--muted); text-decoration: none; font-size: 0.8rem; }
  .url-cell a:hover { color: var(--text); text-decoration: underline; }
  .elapsed { color: var(--muted); font-size: 0.8rem; white-space: nowrap; }
  tr.hidden { display: none; }
</style>
</head>
<body>
<h1>📚 書籤健康報告</h1>
<p class="subtitle">Bookmark Health Report &nbsp;·&nbsp; 掃描時間 __SCAN_TIME__</p>

<div class="stats">
  <div class="card"><div class="num">__TOTAL__</div><div class="lbl">📊 總計 Total</div></div>
  <div class="card ok"><div class="num">__OK__</div><div class="lbl">✅ 存活 Alive</div></div>
  <div class="card dead"><div class="num">__DEAD__</div><div class="lbl">❌ 失效 Dead</div></div>
  <div class="card warn"><div class="num">__WARN__</div><div class="lbl">⚠️ 需確認 Check</div></div>
</div>

<div class="controls">
  <button class="btn active" onclick="doFilter('all',this)">全部 All</button>
  <button class="btn" onclick="doFilter('ok',this)">✅ 存活</button>
  <button class="btn" onclick="doFilter('dead',this)">❌ 失效</button>
  <button class="btn" onclick="doFilter('warn',this)">⚠️ 需確認</button>
  <input id="search" type="text" placeholder="搜尋書籤名稱或網址… Search…" oninput="doSearch(this.value)">
</div>

__FOLDERS__

<script>
let currentFilter = 'all';
let currentSearch = '';

function doFilter(f, btn) {
  currentFilter = f;
  document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function doSearch(q) {
  currentSearch = q.toLowerCase();
  applyFilters();
}

function applyFilters() {
  document.querySelectorAll('tr[data-status]').forEach(row => {
    const matchStatus = currentFilter === 'all' || row.dataset.status === currentFilter;
    const matchSearch = !currentSearch ||
      row.dataset.name.includes(currentSearch) ||
      row.dataset.url.includes(currentSearch);
    row.classList.toggle('hidden', !(matchStatus && matchSearch));
  });
  document.querySelectorAll('.folder').forEach(sec => {
    const visible = [...sec.querySelectorAll('tr[data-status]')].some(r => !r.classList.contains('hidden'));
    sec.style.display = visible ? '' : 'none';
  });
}
</script>
</body>
</html>
"""


def badge(status: str, code: str) -> str:
    icons = {"ok": "✅", "dead": "❌", "warn": "⚠️"}
    return f'<span class="badge {status}">{icons.get(status, "?")} {code}</span>'


def build_html(results: list, scan_time: str) -> str:
    ok   = sum(1 for r in results if r["status"] == "ok")
    dead = sum(1 for r in results if r["status"] == "dead")
    warn = sum(1 for r in results if r["status"] == "warn")

    # Group by folder
    folders: dict = {}
    for r in results:
        folders.setdefault(r["folder"], []).append(r)

    folder_html_parts = []
    for folder, items in sorted(folders.items()):
        rows = []
        for item in items:
            name = item["name"].replace("<", "&lt;").replace(">", "&gt;")
            url  = item["url"]
            url_display = (url[:80] + "…") if len(url) > 80 else url
            elapsed = f'{item["elapsed"]} ms' if item.get("elapsed") else "—"
            reason  = item.get("reason", "")
            rows.append(
                f'<tr class="{item["status"]}" '
                f'data-status="{item["status"]}" '
                f'data-name="{name.lower()}" '
                f'data-url="{url.lower()}">'
                f'<td>{name}</td>'
                f'<td class="url-cell"><a href="{url}" target="_blank">{url_display}</a></td>'
                f'<td>{badge(item["status"], item["code"])}</td>'
                f'<td class="elapsed">{elapsed}</td>'
                f'<td style="font-size:.78rem;color:#64748b">{reason}</td>'
                f'</tr>'
            )

        folder_html_parts.append(
            f'<div class="folder">'
            f'<div class="folder-title">📁 {folder or "書籤列"}</div>'
            f'<table>'
            f'<thead><tr>'
            f'<th>名稱 Name</th><th>網址 URL</th>'
            f'<th>狀態 Status</th><th>回應時間</th><th>備註</th>'
            f'</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody>'
            f'</table></div>'
        )

    html = HTML_TEMPLATE
    html = html.replace("__SCAN_TIME__", scan_time)
    html = html.replace("__TOTAL__", str(len(results)))
    html = html.replace("__OK__",   str(ok))
    html = html.replace("__DEAD__", str(dead))
    html = html.replace("__WARN__", str(warn))
    html = html.replace("__FOLDERS__", "\n".join(folder_html_parts))
    return html


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Chrome Bookmark Checker")
    parser.add_argument("--bookmarks", required=True, help="Path to Chrome Bookmarks file")
    parser.add_argument("--output",    required=True, help="Output HTML report path")
    parser.add_argument("--threads",   type=int, default=20, help="Concurrent threads (default 20)")
    parser.add_argument("--timeout",   type=int, default=10, help="URL timeout in seconds (default 10)")
    args = parser.parse_args()

    if not os.path.isfile(args.bookmarks):
        print(f"❌ 找不到書籤檔案: {args.bookmarks}", file=sys.stderr)
        sys.exit(1)

    print(f"📖 讀取書籤檔案…")
    bookmarks = load_bookmarks(args.bookmarks)
    print(f"📚 找到 {len(bookmarks)} 個書籤，開始測試網址…")
    print(f"   (執行緒: {args.threads}, 逾時: {args.timeout}s)\n")

    results = check_all(bookmarks, threads=args.threads, timeout=args.timeout)

    ok   = sum(1 for r in results if r["status"] == "ok")
    dead = sum(1 for r in results if r["status"] == "dead")
    warn = sum(1 for r in results if r["status"] == "warn")

    print(f"\n{'='*50}")
    print(f"✅ 存活 (Alive):   {ok}")
    print(f"❌ 失效 (Dead):    {dead}")
    print(f"⚠️  需確認 (Check): {warn}")
    print(f"📊 Total:          {len(results)}")

    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = build_html(results, scan_time)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"📄 報告已儲存: {args.output}")
    print(f"{'='*50}")
    print("💡 請用 Chrome 開啟報告檔案，使用篩選按鈕和搜尋框整理書籤。")


if __name__ == "__main__":
    main()
