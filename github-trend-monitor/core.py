"""
core.py — GitHub Trend Monitor: geteilte Logik
Stdlib-only: urllib, json, datetime, pathlib, os
"""
import json
import os
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path


# ── GitHub API ───────────────────────────────────────────────────────────────

def _gh_request(url: str, token: str | None) -> dict:
    """HTTP GET gegen GitHub API; gibt JSON zurück."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def search_repos(query: str, min_stars: int, extra: str = "",
                 token: str | None = None, max_results: int = 1000) -> list[dict]:
    """
    Paginierte GitHub-Search. Gibt Liste von Repo-Dicts zurück.
    extra: zusätzliche Query-Qualifier, z.B. 'created:>=2026-06-20'
    """
    repos: list[dict] = []
    page = 1
    full_query = f"{query} stars:>={min_stars}"
    if extra:
        full_query += f" {extra}"

    while len(repos) < max_results:
        params = urllib.parse.urlencode({
            "q": full_query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page,
        })
        url = f"https://api.github.com/search/repositories?{params}"
        try:
            data = _gh_request(url, token)
        except Exception as e:
            print(f"[GitHub] Fehler bei Seite {page}: {e}")
            break

        items = data.get("items", [])
        if not items:
            break

        for item in items:
            repos.append({
                "full_name":   item["full_name"],
                "stars":       item["stargazers_count"],
                "created_at":  item["created_at"][:10],  # YYYY-MM-DD
                "html_url":    item["html_url"],
                "description": (item.get("description") or "")[:120],
            })

        total = data.get("total_count", 0)
        if page * 100 >= min(total, 1000):
            break
        page += 1

    return repos


# ── Snapshot-Management ──────────────────────────────────────────────────────

def snapshot_path(state_dir: Path, date: str) -> Path:
    return state_dir / f"{date}.json"


def load_snapshot(state_dir: Path, date: str) -> dict | None:
    p = snapshot_path(state_dir, date)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_snapshot(state_dir: Path, date: str, repos: list[dict]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    snap = {
        "date": date,
        "repos": {r["full_name"]: r for r in repos},
    }
    snapshot_path(state_dir, date).write_text(
        json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def find_nearest_snapshot(state_dir: Path, target_date: str,
                           tolerance_days: int = 3) -> tuple[str | None, dict | None]:
    """
    Sucht nächstgelegenen Snapshot zu target_date (±tolerance_days).
    Gibt (date_str, snapshot) zurück oder (None, None) wenn nichts gefunden.
    """
    target = datetime.strptime(target_date, "%Y-%m-%d").date()
    best: tuple[int, str] | None = None

    for p in state_dir.glob("*.json"):
        try:
            d = datetime.strptime(p.stem, "%Y-%m-%d").date()
            diff = abs((d - target).days)
            if diff <= tolerance_days:
                if best is None or diff < best[0]:
                    best = (diff, p.stem)
        except ValueError:
            continue

    if best is None:
        return None, None
    snap = load_snapshot(state_dir, best[1])
    return best[1], snap


def purge_old_snapshots(state_dir: Path, retention_days: int) -> int:
    """Löscht Snapshots älter als retention_days. Gibt Anzahl gelöschter zurück."""
    cutoff = (datetime.now() - timedelta(days=retention_days)).date()
    removed = 0
    for p in state_dir.glob("*.json"):
        try:
            d = datetime.strptime(p.stem, "%Y-%m-%d").date()
            if d < cutoff:
                p.unlink()
                removed += 1
        except ValueError:
            continue
    return removed


# ── Delta-Berechnung ─────────────────────────────────────────────────────────

def compute_delta(today_repos: list[dict], baseline_snap: dict,
                  top_n: int) -> tuple[list[dict], bool]:
    """
    Berechnet Stern-Delta heute vs. Baseline-Snapshot.
    Gibt (ranked_list, is_complete) zurück.
    is_complete=False wenn Baseline <90% der heutigen Repos abdeckt.
    """
    baseline_stars = {name: r["stars"]
                      for name, r in baseline_snap["repos"].items()}
    deltas = []
    matched = 0

    for repo in today_repos:
        name = repo["full_name"]
        if name in baseline_stars:
            matched += 1
            delta = repo["stars"] - baseline_stars[name]
            if delta > 0:
                deltas.append({**repo, "delta": delta})

    coverage = matched / max(len(today_repos), 1)
    deltas.sort(key=lambda x: x["delta"], reverse=True)
    return deltas[:top_n], coverage >= 0.9


# ── Report-Rendering ─────────────────────────────────────────────────────────

def _table_rows(repos: list[dict], show_delta: bool = False,
                show_created: bool = True) -> str:
    header = "| # | Repo | ⭐ |"
    sep    = "|---|---|---|"
    if show_delta:
        header += " Δ |"
        sep    += "---|"
    if show_created:
        header += " Erstellt |"
        sep    += "---|"
    header += " Beschreibung |"
    sep    += "---|"
    lines = [header, sep]

    for i, r in enumerate(repos, 1):
        desc = (r.get("description") or "")[:80].replace("|", "│")
        link = f"[{r['full_name']}]({r['html_url']})"
        row  = f"| {i} | {link} | {r['stars']:,} |"
        if show_delta:
            row += f" +{r.get('delta', 0):,} |"
        if show_created:
            row += f" {r.get('created_at', '?')} |"
        row += f" {desc} |"
        lines.append(row)

    return "\n".join(lines)


def render_report(
    today: str,
    topic: str,
    search_query: str,
    new_week:    list[dict],
    new_month:   list[dict],
    growing_24h: list[dict],
    growing_30d: list[dict],
    baseline_24h_date: str | None,
    baseline_30d_date: str | None,
    complete_24h: bool,
    complete_30d: bool,
) -> str:
    lines = [
        f"# GitHub Trend Report — {today}",
        "",
        f"**Thema:** `{topic}` | **Query:** `{search_query}` | Stand: {today}",
        "",
        "---",
        "",
        f"## 📅 Neue Repos (7 Tage) — Top {len(new_week)}",
        "",
        _table_rows(new_week) if new_week else "_Keine neuen Repos in diesem Zeitraum._",
        "",
        "---",
        "",
        f"## 📅 Neue Repos (30 Tage) — Top {len(new_month)}",
        "",
        _table_rows(new_month) if new_month else "_Keine neuen Repos in diesem Zeitraum._",
        "",
        "---",
        "",
    ]

    lines.append(f"## 📈 Stärkstes Wachstum (24h) — Top {len(growing_24h)}")
    lines.append("")
    if growing_24h:
        lines.append(_table_rows(growing_24h, show_delta=True))
        if not complete_24h:
            lines.append(f"\n_⚠️ Baseline ({baseline_24h_date}) deckt nicht alle Repos ab — Werte approximativ._")
    else:
        lines.append(f"_⏳ Warmlaufphase — noch kein 24h-Baseline verfügbar (Baseline: {baseline_24h_date or 'fehlt'})._")
    lines += ["", "---", ""]

    lines.append(f"## 📈 Stärkstes Wachstum (30 Tage) — Top {len(growing_30d)}")
    lines.append("")
    if growing_30d:
        lines.append(_table_rows(growing_30d, show_delta=True))
        if not complete_30d:
            lines.append(f"\n_⚠️ Baseline ({baseline_30d_date}) — noch keine 30 Tage Verlauf vorhanden._")
    else:
        lines.append(f"_⏳ Warmlaufphase — noch kein 30d-Baseline verfügbar (Baseline: {baseline_30d_date or 'fehlt'})._")
    lines += ["", "---", ""]

    lines.append(f"_Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')} | github-trend-monitor_")
    return "\n".join(lines)


def extract_section(report_md: str, section_key: str) -> str | None:
    """
    Extrahiert eine Sektion aus dem Report anhand eines Schlüsselworts.
    section_key: 'week' | 'month' | '24h' | '30d'
    """
    mapping = {
        "week":  "Neue Repos (7 Tage)",
        "month": "Neue Repos (30 Tage)",
        "24h":   "Stärkstes Wachstum (24h)",
        "30d":   "Stärkstes Wachstum (30 Tage)",
    }
    header = mapping.get(section_key)
    if not header:
        return None

    lines = report_md.splitlines()
    result: list[str] = []
    in_section = False

    for line in lines:
        if header in line and line.startswith("##"):
            in_section = True
            result.append(line)
            continue
        if in_section:
            if line.startswith("## ") and header not in line:
                break
            result.append(line)

    return "\n".join(result).strip() if result else None


# ── Vollständiger Pipeline-Lauf ───────────────────────────────────────────────

def run(base_dir: Path, config: dict, token: str | None = None) -> Path:
    """
    Führt vollständigen Collector-Lauf durch.
    Gibt Pfad zur erzeugten Report-Datei zurück.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    state_dir   = base_dir / "state" / "snapshots"
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    topic        = config["topic"]
    search_query = config["search_query"]
    min_stars    = config.get("track_min_stars", 50)
    cats         = config.get("categories", {})
    retention    = config.get("snapshot_retention_days", 35)

    print(f"[Collector] {today} | Thema: {topic} | Query: {search_query}")

    print("[Collector] Hole Tracking-Universum ...")
    all_repos = search_repos(search_query, min_stars, token=token, max_results=1000)
    print(f"[Collector] {len(all_repos)} Repos im Universum.")
    save_snapshot(state_dir, today, all_repos)

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    print("[Collector] Hole neue Repos (7 Tage) ...")
    new_week = search_repos(
        search_query, min_stars,
        extra=f"created:>={seven_days_ago}",
        token=token,
        max_results=cats.get("new_week_top", 10) * 10,
    )[:cats.get("new_week_top", 10)]

    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    print("[Collector] Hole neue Repos (30 Tage) ...")
    new_month = search_repos(
        search_query, min_stars,
        extra=f"created:>={thirty_days_ago}",
        token=token,
        max_results=cats.get("new_month_top", 5) * 10,
    )[:cats.get("new_month_top", 5)]

    yesterday   = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    b24h_date, b24h_snap = find_nearest_snapshot(state_dir, yesterday, tolerance_days=2)
    growing_24h: list[dict] = []
    complete_24h = False
    if b24h_snap:
        print(f"[Collector] 24h-Delta vs. {b24h_date} ...")
        growing_24h, complete_24h = compute_delta(
            all_repos, b24h_snap, cats.get("growing_24h_top", 10))
    else:
        print("[Collector] Kein 24h-Baseline — Warmlaufphase.")

    thirty_ago  = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    b30d_date, b30d_snap = find_nearest_snapshot(state_dir, thirty_ago, tolerance_days=5)
    growing_30d: list[dict] = []
    complete_30d = False
    if b30d_snap:
        print(f"[Collector] 30d-Delta vs. {b30d_date} ...")
        growing_30d, complete_30d = compute_delta(
            all_repos, b30d_snap, cats.get("growing_30d_top", 10))
    else:
        print("[Collector] Kein 30d-Baseline — Warmlaufphase.")

    report_md = render_report(
        today=today, topic=topic, search_query=search_query,
        new_week=new_week, new_month=new_month,
        growing_24h=growing_24h, growing_30d=growing_30d,
        baseline_24h_date=b24h_date, baseline_30d_date=b30d_date,
        complete_24h=complete_24h, complete_30d=complete_30d,
    )

    report_file = reports_dir / f"{today}.md"
    report_file.write_text(report_md, encoding="utf-8")
    (reports_dir / "LATEST.md").write_text(report_md, encoding="utf-8")
    print(f"[Collector] Report: {report_file}")

    removed = purge_old_snapshots(state_dir, retention)
    if removed:
        print(f"[Collector] {removed} alte Snapshots gelöscht.")

    return report_file
