#!/usr/bin/env python3
"""Generate a visual duplicate manager for guide media (images/videos)."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

GUIDES_ROOT = Path("guides/ru")
OUTPUT_HTML = Path("media_manager_visual.html")

URL_RE = re.compile(r"https?://[^\s<>)\]\"']+")

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".avif"}
VIDEO_EXTS = {".mp4", ".webm", ".mov", ".m4v"}


def clean_url(raw: str) -> str:
    url = raw.strip().rstrip(".,;!?")
    return url


def canonicalize_url(raw_url: str) -> str:
    parts = urlsplit(raw_url)
    # Drop query/fragment to collapse size/proxy variants into one canonical media URL.
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def media_kind(raw_url: str) -> str | None:
    path = urlsplit(raw_url).path.lower()
    ext = Path(path).suffix.lower()
    if ext in VIDEO_EXTS:
        return "video"
    if ext in IMAGE_EXTS:
        return "image"
    return None


def collect_occurrences() -> list[dict]:
    occurrences: list[dict] = []
    occ_id = 1

    for md_file in sorted(GUIDES_ROOT.rglob("*.md")):
        rel = md_file.as_posix()
        lines = md_file.read_text(encoding="utf-8").splitlines()

        for line_no, line in enumerate(lines, start=1):
            urls = URL_RE.findall(line)
            if not urls:
                continue

            seen_on_line = set()
            for raw in urls:
                url = clean_url(raw)
                if url in seen_on_line:
                    continue
                seen_on_line.add(url)

                kind = media_kind(url)
                if not kind:
                    continue

                occurrences.append(
                    {
                        "id": occ_id,
                        "file": rel,
                        "line": line_no,
                        "kind": kind,
                        "url": url,
                        "canonical_url": canonicalize_url(url),
                        "snippet": line.strip()[:220],
                    }
                )
                occ_id += 1

    return occurrences


def build_groups(occurrences: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for occ in occurrences:
        grouped[occ["canonical_url"]].append(occ)

    groups: list[dict] = []
    for canonical, items in grouped.items():
        if len(items) < 2:
            continue

        ordered = sorted(items, key=lambda x: (x["file"], x["line"], x["id"]))
        kinds = {x["kind"] for x in ordered}
        group_kind = "mixed" if len(kinds) > 1 else next(iter(kinds))

        groups.append(
            {
                "canonical_url": canonical,
                "kind": group_kind,
                "count": len(ordered),
                "items": ordered,
            }
        )

    groups.sort(key=lambda g: (-g["count"], g["canonical_url"]))
    return groups


def render_html(payload: dict) -> str:
    data_json = json.dumps(payload, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang=\"ru\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Media Manager: фото и видео дубликаты</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #f0f2f5;
      color: #222;
      padding: 20px;
    }}
    .container {{ max-width: 100%; margin: 0 auto; }}
    .header {{
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 18px;
      box-shadow: 0 2px 8px rgba(0,0,0,.1);
      position: sticky;
      top: 20px;
      z-index: 40;
    }}
    h1 {{ font-size: 28px; margin-bottom: 10px; }}
    .sub {{ color: #555; }}
    .stats {{
      margin-top: 16px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }}
    .stat {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 8px;
      text-align: center;
      padding: 12px;
    }}
    .stat .v {{ font-size: 24px; font-weight: 700; }}
    .stat .l {{ font-size: 12px; opacity: .9; }}
    .toolbar {{
      background: #fff;
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,.1);
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    input, select, button {{
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 14px;
    }}
    input {{ flex: 1; min-width: 220px; }}
    button {{ cursor: pointer; background: #ececec; }}
    button:hover {{ background: #dfdfdf; }}
    .layout {{ margin-right: 320px; }}
    .sidebar {{
      position: fixed;
      right: 0;
      top: 0;
      width: 300px;
      height: 100vh;
      background: #fff;
      border-left: 3px solid #667eea;
      box-shadow: -2px 0 8px rgba(0,0,0,.08);
      padding: 16px;
      overflow-y: auto;
      z-index: 100;
    }}
    .sidebar h3 {{ margin-bottom: 10px; }}
    .pick {{
      background: #ffebee;
      border-left: 3px solid #f44336;
      border-radius: 4px;
      margin: 6px 0;
      padding: 8px;
      font-size: 12px;
    }}
    .group {{
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,.1);
      padding: 16px;
      margin-bottom: 14px;
    }}
    .group-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      border-bottom: 2px solid #f2f2f2;
      padding-bottom: 8px;
      margin-bottom: 10px;
    }}
    .badge {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .url {{
      background: #f6f6f6;
      border-left: 4px solid #667eea;
      border-radius: 6px;
      padding: 10px;
      font-family: Consolas, Monaco, 'Courier New', monospace;
      font-size: 11px;
      color: #555;
      margin-bottom: 12px;
      word-break: break-all;
      max-height: 44px;
      overflow: hidden;
    }}
    .row {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-start; }}
    .item {{
      width: 180px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      background: #fafafa;
      padding: 10px;
      transition: .2s ease;
    }}
    .item.keep {{ border-color: #6f9; background: #f5fff7; }}
    .item.delete {{ border-color: #f44336; background: #fff5f5; }}
    .item .media {{
      width: 100%;
      height: 100px;
      border: 1px solid #ddd;
      border-radius: 6px;
      background: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}
    .item img, .item video {{ width: 100%; height: 100%; object-fit: contain; }}
    .meta {{ margin-top: 8px; font-size: 11px; color: #555; }}
    .meta .file {{ display: block; font-weight: 700; color: #333; margin-bottom: 2px; }}
    .actions {{ margin-top: 8px; display: flex; gap: 6px; }}
    .actions button {{ flex: 1; font-size: 11px; padding: 6px; }}
    .sep {{ align-self: center; color: #999; font-weight: 700; }}
    .empty {{ text-align: center; color: #888; padding: 28px; }}

    @media (max-width: 900px) {{
      .layout {{ margin-right: 0; }}
      .sidebar {{ position: static; width: 100%; height: auto; margin-bottom: 16px; }}
    }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"header\">
      <h1>Media manager: фото и видео дубликаты</h1>
      <p class=\"sub\">Аналог менеджера иконок для media в гайдах RU. В каждой группе один и тот же URL встречается несколько раз.</p>
      <div class=\"stats\">
        <div class=\"stat\"><div class=\"v\" id=\"s-all\">0</div><div class=\"l\">Всего media ссылок</div></div>
        <div class=\"stat\"><div class=\"v\" id=\"s-uniq\">0</div><div class=\"l\">Уникальных media URL</div></div>
        <div class=\"stat\"><div class=\"v\" id=\"s-groups\">0</div><div class=\"l\">Групп дубликатов</div></div>
        <div class=\"stat\"><div class=\"v\" id=\"s-picked\">0</div><div class=\"l\">Отмечено к удалению</div></div>
      </div>
    </div>

    <div class=\"sidebar\">
      <h3>Отмечено удалением</h3>
      <div id=\"picked\"></div>
    </div>

    <main class=\"layout\">
      <div class=\"toolbar\">
        <input id=\"search\" type=\"text\" placeholder=\"Поиск по пути гайда, URL или фрагменту строки\" />
        <select id=\"kind\">
          <option value=\"all\">Все типы</option>
          <option value=\"image\">Только фото</option>
          <option value=\"video\">Только видео</option>
          <option value=\"mixed\">Смешанные</option>
        </select>
        <button id=\"clear\">Очистить выбор</button>
        <button id=\"mark\">Отметить все дубликаты</button>
        <button id=\"export-plan\">Экспорт delete-плана</button>
        <button id=\"export-map\">Экспорт migration-map</button>
      </div>

      <div id=\"groups\"></div>
    </main>
  </div>

  <script>
    const DATA = {data_json};
    const groups = DATA.groups || [];
    const occurrencesById = new Map();
    for (const g of groups) {{
      for (const it of g.items) {{
        occurrencesById.set(it.id, it);
      }}
    }}

    const selections = {{}}; // occurrence id -> true (delete)

    const searchEl = document.getElementById('search');
    const kindEl = document.getElementById('kind');
    const groupsEl = document.getElementById('groups');
    const pickedEl = document.getElementById('picked');

    function updateStats() {{
      document.getElementById('s-all').textContent = DATA.total_occurrences;
      document.getElementById('s-uniq').textContent = DATA.unique_urls;
      document.getElementById('s-groups').textContent = groups.length;
      document.getElementById('s-picked').textContent = Object.keys(selections).length;
    }}

    function groupMatches(g) {{
      const q = searchEl.value.trim().toLowerCase();
      const kind = kindEl.value;
      if (kind !== 'all' && g.kind !== kind) return false;
      if (!q) return true;

      if (g.canonical_url.toLowerCase().includes(q)) return true;
      return g.items.some(it =>
        it.file.toLowerCase().includes(q) ||
        (it.snippet || '').toLowerCase().includes(q) ||
        it.url.toLowerCase().includes(q)
      );
    }}

    function renderPicked() {{
      pickedEl.innerHTML = '';
      const ids = Object.keys(selections).map(x => Number(x)).sort((a,b) => a-b);
      if (!ids.length) {{
        pickedEl.innerHTML = '<div class="empty">Пока ничего не отмечено</div>';
        return;
      }}

      for (const id of ids) {{
        const it = occurrencesById.get(id);
        if (!it) continue;
        const div = document.createElement('div');
        div.className = 'pick';
        div.innerHTML = `<div><strong>${{it.file}}:${{it.line}}</strong></div><div>${{it.kind}} | id=${{id}}</div>`;
        pickedEl.appendChild(div);
      }}
    }}

    function toggleDelete(id) {{
      if (selections[id]) delete selections[id];
      else selections[id] = true;
      render();
    }}

    function render() {{
      updateStats();
      renderPicked();

      groupsEl.innerHTML = '';
      const filtered = groups.filter(groupMatches);

      if (!filtered.length) {{
        groupsEl.innerHTML = '<div class="empty">Ничего не найдено</div>';
        return;
      }}

      for (const g of filtered) {{
        const wrap = document.createElement('section');
        wrap.className = 'group';

        const head = document.createElement('div');
        head.className = 'group-head';
        head.innerHTML = `<div><strong>${{g.kind}}</strong> · ${{g.count}} вхождений</div><div class="badge">dup x${{g.count}}</div>`;

        const url = document.createElement('div');
        url.className = 'url';
        url.title = g.canonical_url;
        url.textContent = g.canonical_url;

        const row = document.createElement('div');
        row.className = 'row';

        g.items.forEach((it, idx) => {{
          const card = document.createElement('article');
          const isDelete = !!selections[it.id];
          card.className = 'item ' + (isDelete ? 'delete' : idx === 0 ? 'keep' : '');

          const mediaHtml = it.kind === 'video'
            ? `<video src="${{it.url}}" controls muted preload="metadata"></video>`
            : `<img src="${{it.url}}" loading="lazy" alt="media" />`;

          card.innerHTML = `
            <div class="media">${{mediaHtml}}</div>
            <div class="meta">
              <span class="file">${{it.file}}</span>
              <span>line: ${{it.line}} · id: ${{it.id}}</span>
            </div>
            <div class="actions">
              <button onclick="toggleDelete(${{it.id}})">${{isDelete ? 'Снять' : 'Удалить'}} </button>
            </div>
          `;

          row.appendChild(card);
          if (idx < g.items.length - 1) {{
            const sep = document.createElement('div');
            sep.className = 'sep';
            sep.textContent = '=';
            row.appendChild(sep);
          }}
        }});

        wrap.appendChild(head);
        wrap.appendChild(url);
        wrap.appendChild(row);
        groupsEl.appendChild(wrap);
      }}
    }}

    function markDuplicates() {{
      for (const g of groups) {{
        g.items.forEach((it, idx) => {{
          if (idx > 0) selections[it.id] = true;
        }});
      }}
      render();
    }}

    function clearSelections() {{
      for (const key of Object.keys(selections)) delete selections[key];
      render();
    }}

    function exportJson(filename, payload) {{
      const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
      const href = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = href;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(href);
    }}

    function exportDeletePlan() {{
      const selected = Object.keys(selections).map(x => Number(x));
      const rows = selected
        .map(id => occurrencesById.get(id))
        .filter(Boolean)
        .map(it => ({{ id: it.id, file: it.file, line: it.line, kind: it.kind, url: it.url, canonical_url: it.canonical_url }}));

      exportJson('media_to_delete.json', {{
        timestamp: new Date().toISOString(),
        total: rows.length,
        rows,
      }});
    }}

    function exportMigrationMap() {{
      const selectedSet = new Set(Object.keys(selections).map(x => Number(x)));
      const migration = [];

      for (const g of groups) {{
        const keep = g.items.find(it => !selectedSet.has(it.id)) || g.items[0];
        for (const it of g.items) {{
          if (!selectedSet.has(it.id)) continue;
          migration.push({{
            from_id: it.id,
            from_file: it.file,
            from_line: it.line,
            from_url: it.url,
            to_id: keep.id,
            to_file: keep.file,
            to_line: keep.line,
            to_url: keep.url,
            canonical_url: g.canonical_url,
          }});
        }}
      }}

      exportJson('media_migration_map.json', {{
        timestamp: new Date().toISOString(),
        total: migration.length,
        migration,
      }});
    }}

    window.toggleDelete = toggleDelete;

    document.getElementById('mark').addEventListener('click', markDuplicates);
    document.getElementById('clear').addEventListener('click', clearSelections);
    document.getElementById('export-plan').addEventListener('click', exportDeletePlan);
    document.getElementById('export-map').addEventListener('click', exportMigrationMap);
    searchEl.addEventListener('input', render);
    kindEl.addEventListener('change', render);

    render();
  </script>
</body>
</html>
"""


def main() -> None:
    occurrences = collect_occurrences()
    groups = build_groups(occurrences)

    payload = {
        "total_occurrences": len(occurrences),
        "unique_urls": len({o["canonical_url"] for o in occurrences}),
        "groups": groups,
    }

    OUTPUT_HTML.write_text(render_html(payload), encoding="utf-8")
    print(f"Generated {OUTPUT_HTML} with {len(groups)} duplicate groups")


if __name__ == "__main__":
    main()
