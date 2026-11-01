#!/usr/bin/env python3
"""README.md ni yaratadi. Hech bir qator WIDTH dan oshmaydi: oshsa skript xato bilan to'xtaydi.

Ishga tushirish: python3 generate.py
"""
import html
import re

WIDTH = 80
BANNER = r"""███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗
██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝╚██╗██╔╝
███████╗ ╚████╔╝ ██╔██╗ ██║   ██║    ╚███╔╝
╚════██║  ╚██╔╝  ██║╚██╗██║   ██║    ██╔██╗
███████║   ██║   ██║ ╚████║   ██║   ██╔╝ ██╗
╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝""".split("\n")
LINKS = [("kawaii.uz", "https://kawaii.uz"), ("bot", "https://bot.kawaii.uz"), ("id", "https://id.kawaii.uz"), ("radio", "https://radio.kawaii.uz")]
INFO = [
    ("Role", "Founder & developer"),
    ("Location", "Tashkent, Uzbekistan"),
    ("Building", "the Kawaii ecosystem"),
    ("Stack", "Rust · Svelte · Tauri · Next.js"),
    ("Data", "PostgreSQL · Redis · Cloudflare R2"),
]


def link(text, url):
    return f"\x00{url}\x01{text}\x02"


def visible(s):
    return re.sub(r"\x00[^\x01]*\x01([^\x02]*)\x02", r"\1", s)


def center(s, block=None):
    return " " * ((WIDTH - (block or len(visible(s)))) // 2) + s


def render():
    block = max(map(len, BANNER))
    nav = "  ·  ".join(link(*x) for x in LINKS)
    title = "── neofetch "
    lines = ["─" * WIDTH, ""]
    lines += [center(b, block) for b in BANNER]
    lines += ["", center("software developer  ·  perfectionist  ·  founder"), "", center(f"[ {nav} ]"), ""]
    lines += [title + "─" * (WIDTH - len(title)), ""]
    lines += [f"  {k:<10}{v}" for k, v in INFO]
    lines += ["", "─" * WIDTH]
    for line in lines:
        if len(visible(line)) > WIDTH:
            raise SystemExit(f"Qator sig'madi: {visible(line)!r}")
    body = re.sub(r"\x00([^\x01]*)\x01([^\x02]*)\x02", r'<a href="\1">\2</a>', html.escape("\n".join(lines), quote=False))
    return f"<pre>\n{body}\n</pre>\n"


if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(render())
