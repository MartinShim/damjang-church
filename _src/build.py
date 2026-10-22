#!/usr/bin/env python3
"""
담장너머교회 사이트 빌드.

  _src/pages/*.html            페이지 본문(머리/꼬리 제외)
  _src/static/*.css|*.js       스타일·스크립트 원본
  _src/data/church.json        (없음) 잘 안 바뀌는 정보는 템플릿에 직접
  _src/data/bulletins/*.json   주보 한 주 = 파일 하나
  _src/data/sermons.json       유튜브 설교 목록 (최신이 위)

실행:  python3 _src/build.py
결과:  저장소 루트의 *.html, bulletins/*.html, css/, js/
"""
import hashlib
import html
import json
import os
import glob
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src")
YT_CHANNEL = "https://www.youtube.com/@%EB%8B%B4%EC%9E%A5%EB%84%88%EB%A8%B8%EA%B5%90%ED%9A%8C-x2u"

NAV = [
    ("index.html", "홈"),
    ("about.html", "교회 소개"),
    ("worship.html", "예배와 모임"),
    ("news.html", "교회 소식"),
    ("sermons.html", "설교"),
]

e = html.escape


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def ko_date(iso):
    d = date.fromisoformat(iso)
    return "%d년 %d월 %d일" % (d.year, d.month, d.day)


def dot_date(iso):
    d = date.fromisoformat(iso)
    return "%d. %d. %d" % (d.year, d.month, d.day)


# ---------- 정적 파일: 내용 해시를 파일명에 넣어 캐시 문제를 없앰 ----------
def publish_static(name, text, folder, ext):
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    out_dir = os.path.join(ROOT, folder)
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, name + ".*." + ext)) + glob.glob(os.path.join(out_dir, name + "." + ext)):
        os.remove(old)
    fname = "%s.%s.%s" % (name, h, ext)
    write(os.path.join(out_dir, fname), text)
    return "%s/%s" % (folder, fname)


# ---------- 공통 머리/꼬리 ----------
def head(title, desc, current, root):
    nav = "\n".join(
        '      <a href="%s%s"%s>%s</a>' % (root, f, ' aria-current="page"' if f == current else "", label)
        for f, label in NAV
    )
    return """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{root}assets/church-sketch.png">
<link rel="icon" href="{root}assets/cross-mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800&family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}{css}">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html"><img src="{root}assets/cross-mark.png" alt="">담장너머교회</a>
    <nav class="nav">
{nav}
      <a class="nav-cta" href="{root}about.html#newcomer">처음 오셨나요?</a>
    </nav>
    <a class="hbtn" href="{root}about.html#newcomer">처음 오셨나요?</a>
    <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
<main>
""".format(title=e(title), desc=e(desc), root=root, css=ASSETS["css"], nav=nav)


def foot(root, with_sermons):
    scripts = '<script src="%s%s"></script>\n' % (root, ASSETS["sermons"]) if with_sermons else ""
    return """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <div class="footer-brand"><img src="{root}assets/cross-mark.png" alt="">담장너머교회</div>
        <p style="margin-top:10px">대한예수교장로회(합동) 경기노회</p>
      </div>
      <div>
        <h4>WORSHIP</h4>
        <ul>
          <li>주일오전예배 11:00</li>
          <li>오후소모임 · 어린이모임 13:30</li>
          <li>수요성경문답 21:00</li>
          <li>금요리더모임 21:30</li>
        </ul>
      </div>
      <div>
        <h4>VISIT</h4>
        <p>서울 서초구 서초중앙로18길 43<br>율전빌딩 B1</p>
      </div>
      <div>
        <h4>CONTACT</h4>
        <ul>
          <li>담임 임승민 목사</li>
          <li><a href="tel:01034234684">010-3423-4684</a></li>
          <li><a href="{yt}" target="_blank" rel="noopener">유튜브 채널</a></li>
        </ul>
      </div>
    </div>
    <p class="copy">© 담장너머교회</p>
  </div>
</footer>
{scripts}<script src="{root}{main}"></script>
</body>
</html>
""".format(root=root, yt=YT_CHANNEL, scripts=scripts, main=ASSETS["main"])


def page(body, title, desc, current, root="", with_sermons=False):
    return head(title, desc, current, root) + body.strip() + "\n" + foot(root, with_sermons)


# ---------- 주보 조각 ----------
def r_news(b):
    out = ['<ol class="news-list">']
    for i, n in enumerate(b["news"], 1):
        items = "".join("<li>%s</li>" % e(x) for x in n.get("items", []))
        out.append('  <li>\n    <span class="n">%02d</span>\n    <h3>%s</h3>\n    <ul>%s</ul>\n  </li>' % (i, e(n["title"]), items))
    out.append("</ol>")
    return "\n".join(out)


def r_schedule(b):
    today = date.fromisoformat(b["date"])
    rows = []
    for it in b["schedule"]["items"]:
        done = date.fromisoformat(it["end"]) < today
        rows.append('  <li%s><span class="d">%s</span>%s</li>' % (' class="done"' if done else "", e(it["date"]), e(it["text"])))
    return '<ul class="sched sched-wrap">\n%s\n</ul>' % "\n".join(rows)


def r_book(b):
    bk = b.get("book")
    if not bk:
        return ""
    ps = "\n".join("<p>%s</p>" % e(p) for p in bk["paragraphs"])
    return """<div class="book">
  <p class="lbl on-dark">Book of the Month</p>
  <h3>%s의 책 &lt;%s&gt;</h3>
  <p class="by">%s</p>
  %s
</div>""" % (e(bk["month"]), e(bk["title"]), e(bk["author"]), ps)


def r_devotion(b):
    rows = "\n".join(
        '  <li><b><span class="n">%02d</span>%s</b><p>%s</p></li>' % (i, e(d["k"]), e(d["v"]))
        for i, d in enumerate(b.get("devotion", []), 1)
    )
    return '<ul class="rows">\n%s\n</ul>' % rows


def r_order(b, news_href):
    s = b["sermon"]
    rows = []
    for o in b["order"]:
        pos = '<span class="up">▲</span>' if o.get("stand") else ""
        if o.get("sermon"):
            val = "&lt;%s&gt;<br>%s" % (e(s["series"]), e(s["title"]))
            rows.append('<tr class="sermon"><td class="pos">%s</td><td class="item">%s</td><td class="val">%s</td></tr>' % (pos, e(o["item"]), val))
            continue
        if o["item"] == "교회소식":
            val = '<a href="%s">교회 소식 보기</a>' % news_href
        else:
            val = e(o.get("value", ""))
        rows.append('<tr><td class="pos">%s</td><td class="item">%s</td><td class="val">%s</td></tr>' % (pos, e(o["item"]), val))
    return """<table class="order">
  <tbody>
    %s
  </tbody>
</table>
<p class="legend"><span><i class="up">▲</i>일어서서</span></p>""" % "\n    ".join(rows)


def r_sermon_card(b, root):
    s = b["sermon"]
    if s.get("youtube"):
        link = '<a class="btn" href="%ssermons.html?v=%s">설교 영상과 요약 보기</a>' % (root, s["youtube"])
    else:
        link = '<p class="d" style="color:var(--mute)">설교 영상은 준비되는 대로 설교 페이지에 올라옵니다.</p>'
    return """<div class="card blue">
  <span class="pill">%s</span>
  <h3 style="font-size:26px;margin-top:14px">%s</h3>
  <p class="passage-l">%s</p>
  %s
</div>""" % (e(s["series"]), e(s["title"]), e(s["passage"]), link)


def r_archive_rows(bs, root, current=None):
    rows = []
    for b in bs:
        s = b["sermon"]
        cur = ' class="current"' if b["date"] == current else ""
        rows.append(
            '<li%s><a href="%sbulletins/%s.html"><span class="ad">%s</span><span class="at">%s</span><span class="ap">%s</span></a></li>'
            % (cur, root, b["date"], dot_date(b["date"]), e(s["title"]), e(s["passage"]))
        )
    return '<ul class="archive">\n%s\n</ul>' % "\n".join(rows)


def news_body(b, root, title_html, sub_html, extra=""):
    return """<section class="page-title">
  <div class="wrap">
    <div>
      <div class="bars"><i></i><i></i></div>
      <p class="lbl">Church News</p>
      <h1>{title}</h1>
      <div class="pt-sub">{sub}</div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap split">
    <div>
      <div class="sec-head"><div><p class="lbl">News</p><h2 class="title">교회 소식</h2></div></div>
      {news}
    </div>
    <div>
      <div class="sec-head"><div><p class="lbl">Schedule</p><h2 class="title">{sched_title}</h2></div></div>
      {sched}
    </div>
  </div>
</section>
{extra}
<section class="sec soft">
  <div class="wrap split">
    <div id="book" style="scroll-margin-top:100px">
      {book}
    </div>
    <div>
      <div class="sec-head"><div><p class="lbl">Weekly Devotion</p><h2 class="title">이번 주 경건생활 권면</h2></div></div>
      {devotion}
    </div>
  </div>
</section>
""".format(title=title_html, sub=sub_html, news=r_news(b), sched_title=e(b["schedule"]["title"]),
           sched=r_schedule(b), book=r_book(b), devotion=r_devotion(b), extra=extra)


def build():
    global ASSETS
    ASSETS = {}

    bulletins = [json.loads(read(p)) for p in glob.glob(os.path.join(SRC, "data", "bulletins", "*.json"))]
    bulletins.sort(key=lambda b: b["date"], reverse=True)
    latest = bulletins[0]
    sermons = json.loads(read(os.path.join(SRC, "data", "sermons.json")))

    # 설교 목록에 주보의 설교 요약을 영상 ID로 연결
    by_video = {b["sermon"]["youtube"]: b for b in bulletins if b["sermon"].get("youtube")}
    for s in sermons:
        b = by_video.get(s["id"])
        if b:
            s["summary"] = {"passage": b["sermon"]["passage"], "points": b["sermon"]["summary"]}
            s["bulletin"] = b["date"]

    ASSETS["css"] = publish_static("style", read(os.path.join(SRC, "static", "style.css")), "css", "css")
    ASSETS["main"] = publish_static("main", read(os.path.join(SRC, "static", "main.js")), "js", "js")
    sermons_js = "/* 자동 생성 파일입니다. _src/data/sermons.json 과 주보 파일을 고치세요. */\nwindow.SERMONS = " + \
        json.dumps(sermons, ensure_ascii=False, indent=1) + ";\n"
    ASSETS["sermons"] = publish_static("sermons", sermons_js, "js", "js")

    # 일반 페이지 (템플릿)
    for fname, _ in NAV:
        src = read(os.path.join(SRC, "pages", fname))
        meta, body = src.split("\n---\n", 1)
        m = dict(l.split(": ", 1) for l in meta.strip().splitlines())
        if fname == "worship.html":
            body = body.replace("{{ORDER_DATE}}", "%s 주보 기준" % ko_date(latest["date"]))
            body = body.replace("{{ORDER}}", r_order(latest, "news.html"))
        if fname == "news.html":
            others = [b for b in bulletins if b is not latest]
            extra = ""
            if others:
                extra = """<section class="sec">
  <div class="wrap">
    <div class="sec-head"><div><p class="lbl">Archive</p><h2 class="title">지난 주보</h2></div><a class="btn ghost" href="bulletins/index.html">지난 소식 보러가기</a></div>
    %s
  </div>
</section>""" % r_archive_rows(others[:6], "")
            body = news_body(latest, "", "교회 소식",
                             '%s 주보<div class="btns" style="margin-top:18px"><a class="btn" href="bulletins/index.html">지난 소식 보러가기</a></div>' % dot_date(latest["date"])) + extra
        write(os.path.join(ROOT, fname), page(body, m["title"], m["desc"], fname, "", fname in ("index.html", "sermons.html")))

    # 주보별 페이지
    for i, b in enumerate(bulletins):
        newer = bulletins[i - 1] if i > 0 else None
        older = bulletins[i + 1] if i + 1 < len(bulletins) else None
        nav = []
        if older:
            nav.append('<a href="%s.html">← %s 주보</a>' % (older["date"], dot_date(older["date"])))
        nav.append('<a href="index.html">지난 주보 전체</a>')
        if newer:
            nav.append('<a href="%s.html">%s 주보 →</a>' % (newer["date"], dot_date(newer["date"])))
        pager = '<div class="pager">%s</div>' % "".join(nav)
        extra = """<section class="sec soft">
  <div class="wrap split wide">
    <div>
      <div class="sec-head"><div><p class="lbl">Order of Worship</p><h2 class="title">주일오전예배 순서</h2></div></div>
      %s
    </div>
    <div>
      <div class="sec-head"><div><p class="lbl">Sermon</p><h2 class="title">이 주의 설교</h2></div></div>
      %s
    </div>
  </div>
</section>""" % (r_order(b, "#top"), r_sermon_card(b, "../"))
        body = '<div id="top"></div>' + news_body(b, "../", '교회소식 <span style="white-space:nowrap">(%s)</span>' % ko_date(b["date"]), pager, extra) + \
            '<section style="padding:48px 0"><div class="wrap">%s</div></section>' % pager
        write(os.path.join(ROOT, "bulletins", b["date"] + ".html"),
              page(body, "교회소식 (%s) | 담장너머교회" % ko_date(b["date"]),
                   "담장너머교회 교회소식 (%s) — 교회 소식, 일정, 예배 순서, 설교" % ko_date(b["date"]), "news.html", "../"))

    # 지난 주보 목록
    groups = {}
    for b in bulletins:
        groups.setdefault(b["date"][:7], []).append(b)
    blocks = []
    for ym in sorted(groups, reverse=True):
        y, mth = ym.split("-")
        blocks.append('<h3 class="archive-month">%s년 %d월</h3>\n%s' % (y, int(mth), r_archive_rows(groups[ym], "../")))
    body = """<section class="page-title">
  <div class="wrap">
    <div>
      <div class="bars"><i></i><i></i></div>
      <p class="lbl">Archive</p>
      <h1>지난 주보</h1>
      <p>주일마다 나눈 소식과 설교를 날짜별로 모았습니다.</p>
    </div>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    %s
  </div>
</section>""" % "\n".join(blocks)
    write(os.path.join(ROOT, "bulletins", "index.html"),
          page(body, "지난 주보 | 담장너머교회", "담장너머교회 지난 주보 모음", "news.html", "../"))

    print("주보 %d개, 설교 %d개 → 빌드 완료 (최신 주보 %s)" % (len(bulletins), len(sermons), latest["date"]))


if __name__ == "__main__":
    build()
