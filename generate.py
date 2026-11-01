#!/usr/bin/env python3
"""README.md ni yaratadi: butun sahifa bitta ASCII oyna, faollik GitHub'dan olinadi.

Hamma qator aynan WIDTH belgi: kenglik mos kelmasa skript xato bilan to'xtaydi va eski README qoladi.
Ishga tushirish: python3 generate.py
"""
import datetime as dt
import html
import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

USER = "syntxme"
WIDTH = 80
INNER = WIDTH - 4
TZ = ZoneInfo("Asia/Tashkent")
LEVELS = "·░▒▓█"
DAYS = ["   ", "Mon", "   ", "Wed", "   ", "Fri", "   "]
SERVICES = [
    ("kawaii.uz", "https://kawaii.uz/", "the front door"),
    ("bot.kawaii.uz", "https://bot.kawaii.uz/", "anime in Telegram"),
    ("id.kawaii.uz", "https://id.kawaii.uz/", "one account for everything"),
    ("radio.kawaii.uz", "https://radio.kawaii.uz/", "music, all day"),
    ("api.kawaii.uz", "https://api.kawaii.uz/health", "anime data for the ecosystem"),
]


def fetch(url, token=False):
    headers = {"User-Agent": f"{USER}-profile"}
    if "contributions" in url:
        headers["X-Requested-With"] = "XMLHttpRequest"
    if token and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return r.read().decode("utf-8")


def is_up(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile"}), timeout=15) as r:
            return r.status < 500
    except urllib.error.HTTPError as e:
        return e.code < 500
    except OSError:
        return False


def contributions():
    """{sana: (daraja, soni)} oxirgi bir yil uchun."""
    page = fetch(f"https://github.com/users/{USER}/contributions")
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)', page))
    days = {}
    for date, cell, level in re.findall(r'data-date="([\d-]+)"[^>]*?id="([^"]+)"[^>]*?data-level="(\d)"', page):
        m = re.match(r"(\d[\d,]*) contribution", tips.get(cell, ""))
        days[dt.date.fromisoformat(date)] = (int(level), int(m.group(1).replace(",", "")) if m else 0)
    if len(days) < 300:
        raise SystemExit(f"Faollik o'qilmadi: {len(days)} kun")
    return days


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 0 if unicodedata.combining(c) else 1 for c in s)


# Havola: ko'rinadigan matn kenglikka kiradi, manzil kirmaydi.
def link(text, url):
    return f"\x00{url}\x01{text}\x02"


def visible(s):
    return re.sub(r"\x00[^\x01]*\x01([^\x02]*)\x02", r"\1", s)


def row(s=""):
    gap = INNER - width(visible(s))
    if gap < 0:
        raise SystemExit(f"Qator sig'madi: {visible(s)!r}")
    return f"│ {s}{' ' * gap} │"


def heading(title):
    return row(f"── {title} " + "─" * (INNER - width(title) - 4))


def center(s):
    return " " * ((INNER - width(visible(s))) // 2) + s


def graph(days):
    first = min(days)
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    weeks = (max(days) - start).days // 7 + 1
    months, last = [" "] * weeks, None
    for w in range(weeks):
        day = start + dt.timedelta(weeks=w)
        if day.month != last and w + 3 <= weeks:
            months[w:w + 3] = day.strftime("%b")
            last = day.month
    lines = ["    " + "".join(months)]
    for d in range(7):
        cells = ""
        for w in range(weeks):
            day = start + dt.timedelta(days=w * 7 + d)
            cells += LEVELS[days[day][0]] if day in days else " "
        lines.append(f"{DAYS[d]} {cells}")
    return lines


def stats(days, today):
    counts = {d: c for d, (_, c) in days.items()}
    active = sorted(d for d, c in counts.items() if c)
    longest = run = 0
    prev = None
    for d in active:
        run = run + 1 if prev and (d - prev).days == 1 else 1
        longest = max(longest, run)
        prev = d
    streak, d = 0, today if counts.get(today) else today - dt.timedelta(days=1)
    while counts.get(d):
        streak += 1
        d -= dt.timedelta(days=1)
    best = max(counts, key=counts.get)
    return {
        "total": sum(counts.values()),
        "active": len(active),
        "streak": streak,
        "longest": longest,
        "best": f"{counts[best]} on {best:%d %b %Y}" if counts[best] else "—",
        "last": f"{active[-1]:%d %b %Y}" if active else "—",
    }


def recent():
    events = json.loads(fetch(f"https://api.github.com/users/{USER}/events/public?per_page=100", token=True))
    out = []
    for e in events:
        repo = e["repo"]["name"]
        if repo == f"{USER}/{USER}":
            continue
        kind = {"PushEvent": "pushed to", "CreateEvent": "created", "PullRequestEvent": "pull request on", "IssuesEvent": "issue on", "ReleaseEvent": "released", "WatchEvent": "starred", "ForkEvent": "forked"}.get(e["type"])
        if not kind:
            continue
        item = (dt.datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).astimezone(TZ).date(), kind, repo)
        if item not in out:
            out.append(item)
    return sorted(out, key=lambda x: x[0], reverse=True)[:5]


def render():
    now = dt.datetime.now(TZ)
    days = contributions()
    s = stats(days, now.date())
    banner = r"""███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗
██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝╚██╗██╔╝
███████╗ ╚████╔╝ ██╔██╗ ██║   ██║    ╚███╔╝
╚════██║  ╚██╔╝  ██║╚██╗██║   ██║    ██╔██╗
███████║   ██║   ██║ ╚████║   ██║   ██╔╝ ██╗
╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝""".split("\n")
    pad = (INNER - max(map(width, banner))) // 2
    title = f" {USER}@github: ~ "
    L = ["╭─" + title + "─" * (WIDTH - width(title) - 3) + "╮", row()]
    L += [row(" " * pad + b) for b in banner]
    L += [row(), row(center("software developer  ·  perfectionist  ·  founder")), row()]
    nav = "  ·  ".join(link(n, u) for n, u in [("kawaii.uz", "https://kawaii.uz"), ("bot", "https://bot.kawaii.uz"), ("id", "https://id.kawaii.uz"), ("radio", "https://radio.kawaii.uz")])
    L += [row(center(f"[ {nav} ]")), row()]

    L += [heading("neofetch"), row()]
    logo = ["  ███████  ", "  ██       ", "  ███████  ", "       ██  ", "  ███████  "]
    info = ["Role      Founder & developer", "Location  Tashkent, Uzbekistan", "Building  the Kawaii ecosystem", "Stack     Rust · Svelte · Tauri · Next.js", "Data      PostgreSQL · Redis · Cloudflare R2"]
    L += [row(f"{c}     {i}") for c, i in zip(logo, info)] + [row()]

    L += [heading("systemctl status kawaii-*"), row()]
    for name, url, about in SERVICES:
        state = "● online " if is_up(url) else "○ offline"
        L.append(row(f"  {state}   {link(name, url.replace('/health', ''))}{' ' * (20 - width(name))}{about}"))
    L += [row()]

    L += [heading(f"git log --since=1.year  ({s['total']:,} contributions)"), row()]
    L += [row(g) for g in graph(days)]
    L += [row(), row(" " * 4 + "less " + " ".join(LEVELS) + " more"), row()]
    pairs = [("Active days", s["active"], "Current streak", f"{s['streak']} d"), ("Longest streak", f"{s['longest']} d", "Best day", s["best"]), ("Last active", s["last"], "", "")]
    for a, b, c, d in pairs:
        L.append(row(f"  {a:<15}{str(b):<15}{c:<16}{d}".rstrip()))
    L += [row()]

    events = recent()
    L += [heading("recent activity  (public)"), row()]
    for date, kind, repo in events:
        L.append(row(f"  {date:%d %b %Y}   {kind:<16}{link(repo, 'https://github.com/' + repo)}"))
    if not events:
        L.append(row("  nothing public lately. the good stuff is in private repos."))
    L += [row()]

    L += [heading("cat ~/.principles"), row()]
    L += [row("  # one standard for every service: systemd, CI, automatic rollback"), row("  # tests pass, or nothing ships"), row(f"  # every line on this page is exactly {WIDTH} columns. a script checks."), row()]
    L += [row(f"syntx@tashkent:~$ █{' ' * (INNER - 37)}updated {now:%Y-%m-%d}"), "╰" + "─" * (WIDTH - 2) + "╯"]

    for line in L:
        if width(visible(line)) != WIDTH:
            raise SystemExit(f"Kenglik {width(visible(line))}: {visible(line)!r}")
    body = "\n".join(L)
    body = html.escape(body, quote=False)
    body = re.sub(r"\x00([^\x01]*)\x01([^\x02]*)\x02", r'<a href="\1">\2</a>', body)
    return f"<pre>\n{body}\n</pre>\n"


if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(render())
