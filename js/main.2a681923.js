// 모바일 메뉴 토글
(function () {
  var btn = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (!btn || !nav) return;
  btn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();

function fmtDate(d) {
  var p = d.split("-");
  return p[0] + "." + p[1] + "." + p[2];
}
function esc(s) {
  return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
  });
}
function seriesLabel(s) {
  return s === "로마서" ? "로마서 강해" : s;
}

// 홈: 이번 주 말씀 (sermons.js의 첫 번째 설교)
(function () {
  var box = document.getElementById("latest-sermon");
  var list = window.SERMONS;
  if (!box || !list || !list.length) return;
  var s = list[0];

  document.getElementById("ls-video").href = "sermons.html";
  document.getElementById("ls-thumb").src = "https://i.ytimg.com/vi/" + s.id + "/hqdefault.jpg";
  document.getElementById("ls-series").textContent = seriesLabel(s.series);
  document.getElementById("ls-title").textContent = s.title;
  document.getElementById("ls-meta").textContent =
    (s.summary && s.summary.passage ? s.summary.passage + " · " : "") + "임승민 목사 · " + fmtDate(s.date);

  var sum = document.getElementById("ls-sum");
  if (s.summary && s.summary.points && s.summary.points.length) {
    var p = s.summary.points[0];
    sum.innerHTML = "<b>1. " + esc(p.h) + "</b><span class=\"t\">" + esc(p.p) + "</span>";
    sum.hidden = false;
  }

  document.getElementById("ls-list").innerHTML = list.slice(1, 3).map(function (x) {
    return '<a href="sermons.html">' + esc(x.title) + "<span>" + fmtDate(x.date).slice(5) + "</span></a>";
  }).join("");
})();

// 설교 페이지: 플레이어 + 목록 + 시리즈 필터
(function () {
  var grid = document.getElementById("sermon-grid");
  var list = window.SERMONS;
  if (!grid || !list || !list.length) return;

  var frame = document.getElementById("player-frame");
  var titleEl = document.getElementById("now-title");
  var metaEl = document.getElementById("now-meta");
  var seriesEl = document.getElementById("now-series");
  var linkEl = document.getElementById("now-link");

  grid.innerHTML = list.map(function (s, i) {
    return (
      '<button class="vcard" type="button" data-i="' + i + '" data-series="' + s.series + '">' +
        '<div class="thumb"><img loading="lazy" alt="" src="https://i.ytimg.com/vi/' + s.id + '/hqdefault.jpg">' +
        '<span class="play"><svg viewBox="0 0 24 24"><path d="M7 4l14 8-14 8z"/></svg></span></div>' +
        '<div class="vt">' + esc(s.title) + '</div>' +
        '<div class="vm"><b>' + seriesLabel(s.series) + '</b> · ' + fmtDate(s.date) + '</div>' +
      '</button>'
    );
  }).join("");

  var cards = grid.querySelectorAll(".vcard");

  function select(i, autoplay) {
    var s = list[i];
    frame.src = "https://www.youtube-nocookie.com/embed/" + s.id + "?rel=0" + (autoplay ? "&autoplay=1" : "");
    titleEl.textContent = s.title;
    var passageEl = document.getElementById("now-passage");
    var passage = s.summary && s.summary.passage;
    passageEl.textContent = passage || "";
    passageEl.hidden = !passage;
    metaEl.textContent = fmtDate(s.date) + " · 설교 임승민 목사";
    seriesEl.textContent = seriesLabel(s.series);
    linkEl.href = "https://www.youtube.com/watch?v=" + s.id;
    cards.forEach(function (c) { c.classList.toggle("playing", +c.dataset.i === i); });

    // 설교 요약: sermons.js에 summary가 있는 설교만 표시
    var box = document.getElementById("summary-box");
    if (box) {
      var sm = s.summary;
      box.hidden = !sm;
      if (sm) {
        document.getElementById("summary-body").innerHTML = sm.points.map(function (p, n) {
          return '<div class="card' + (n % 2 ? "" : " blue") + '"><h3><span class="n">0' + (n + 1) + "</span>" +
            esc(p.h) + "</h3><p>" + esc(p.p) + "</p></div>";
        }).join("");
      }
    }
  }

  grid.addEventListener("click", function (e) {
    var card = e.target.closest(".vcard");
    if (!card) return;
    select(+card.dataset.i, true);
    document.getElementById("now").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  document.querySelectorAll(".filters button").forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.dataset.filter;
      document.querySelectorAll(".filters button").forEach(function (x) {
        x.setAttribute("aria-pressed", x === b ? "true" : "false");
      });
      cards.forEach(function (c) { c.hidden = f !== "all" && c.dataset.series !== f; });
    });
  });

  // sermons.html?v=영상ID 로 들어오면 그 설교를 먼저 보여줌
  var want = new URLSearchParams(location.search).get("v");
  var start = 0;
  list.forEach(function (s, i) { if (s.id === want) start = i; });
  select(start, false);
})();
