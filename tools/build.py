#!/usr/bin/env python3
"""Build one edition of Ron's Melbourne Outings.

Usage:  python3 tools/build.py data/YYYY-MM-DD.json

* renders editions/YYYY-MM-DD.html from the data file
* adds/updates the edition in editions.json (newest first)
* refreshes the no-JS fallback list baked into index.html
"""
import datetime as dt, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SECTIONS = [  # (key in data, heading, id)
    ("Hikes", "Hikes", "hikes"),
    ("Bike", "Bike trails", "bikes"),
    ("Music", "Music", "music"),
    ("Tours", "New tours on sale", "tours"),
    ("Comedy", "Stand-up comedy", "comedy"),
    ("Sport", "Sports", "sports"),
    ("Basketball", "Basketball", "basketball"),
    ("Theatre", "Musicals & theatre", "theatre"),
    ("Exhibitions+Markets", "Exhibitions & markets", "exhibitions"),
]
e = lambda s: html.escape(str(s), quote=True)


def nice_date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d:%a} {d.day} {d:%b %Y}"


def card(it, star=False):
    end = f' data-end="{e(it["end"])}"' if it.get("end") else ""
    tag = ' <span class="tag">Top pick</span>' if it.get("top") and star else ""
    return (f'<li class="item"{end}>'
            f'<a class="name" href="{e(it["url"])}" target="_blank" rel="noopener"><strong>{e(it["name"])}</strong></a>{tag}'
            f'<div class="meta"><span class="when">{e(it["when"])}</span>'
            f'<span class="venue">{e(it["venue"])}</span>'
            f'<span class="price">{e(it.get("price") or "See site")}</span></div>'
            f'<p class="note">{e(it.get("note", ""))}</p></li>')


def render(d):
    items = d["items"]
    tops = [i for i in items if i.get("top")]
    toc, body = [], []
    toc.append('<a href="#top-picks">Top picks</a>')
    body.append('<section id="top-picks" class="top"><h2>⭐ Top picks</h2><ul class="items">'
                + "".join(card(i) for i in tops) + "</ul></section>")
    for key, title, sid in SECTIONS:
        keys = key.split("+")
        sel = [i for i in items if i["section"] in keys]
        if not sel:
            continue
        toc.append(f'<a href="#{sid}">{e(title)}</a>')
        body.append(f'<section id="{sid}"><h2>{e(title)}</h2><ul class="items">'
                    + "".join(card(i, star=True) for i in sel) + "</ul></section>")
    date = d["date"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ron's Melbourne Outings: {e(nice_date(date))}</title>
<link rel="stylesheet" href="../outings.css">
</head>
<body>
<div class="wrap">
<p class="back"><a href="../">← All editions</a></p>
<header><h1>Ron's Melbourne Outings</h1>
<p class="sub">Edition {e(d.get("edition", ""))} · {e(nice_date(date))}</p></header>
<nav class="toc">{"".join(toc)}</nav>
{chr(10).join(body)}
<footer><p>Events whose last date has passed are greyed out automatically. Prices and dates as published at the time of the edition; check the linked page before booking.</p></footer>
</div>
<script>
(function () {{
  var today = new Intl.DateTimeFormat("en-CA", {{ timeZone: "Australia/Melbourne" }}).format(new Date());
  document.querySelectorAll(".item[data-end]").forEach(function (el) {{
    if (el.dataset.end < today) {{ el.classList.add("past"); el.title = "This event has finished"; }}
  }});
}})();
</script>
</body>
</html>
"""


def main(path):
    d = json.loads(pathlib.Path(path).read_text())
    date = d["date"]
    out = ROOT / "editions" / f"{date}.html"
    out.write_text(render(d))
    ej = ROOT / "editions.json"
    eds = json.loads(ej.read_text()) if ej.exists() else {"editions": []}
    entry = {
        "date": date,
        "edition": d.get("edition"),
        "file": f"editions/{date}.html",
        "title": d.get("title", nice_date(date)),
        "top_picks": [{"name": i["name"], "when": i["when"], "venue": i["venue"]} for i in d["items"] if i.get("top")],
        "item_count": len(d["items"]),
    }
    eds["editions"] = sorted([x for x in eds["editions"] if x["date"] != date] + [entry],
                             key=lambda x: x["date"], reverse=True)
    ej.write_text(json.dumps(eds, indent=2, ensure_ascii=False) + "\n")
    # static fallback in index.html
    idx = ROOT / "index.html"
    lis = "".join(
        f'<li><a href="{e(x["file"])}"><strong>{e(nice_date(x["date"]))}</strong></a> – '
        + e("; ".join(t["name"] for t in x["top_picks"])) + "</li>" for x in eds["editions"])
    txt = re.sub(r"(<!-- EDITIONS -->).*?(<!-- /EDITIONS -->)",
                 lambda m: m.group(1) + lis + m.group(2), idx.read_text(), flags=re.S)
    idx.write_text(txt)
    print("built", out.relative_to(ROOT), "and updated editions.json + index.html")


if __name__ == "__main__":
    main(sys.argv[1])
