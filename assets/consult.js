/* Ask Sarathi: guided consultation. Runs entirely in the browser. */
(function () {
  "use strict";
  var root = document.querySelector(".cx");
  if (!root) return;
  var stage = root.querySelector(".cx-stage");
  var D = null;
  var S = { step: "who", aud: null, feel: null, sit: null, vi: 0, matches: null, text: "", help: null, hist: [] };
  var audio = null;

  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("sarathi.consult." + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("sarathi.consult." + k, JSON.stringify(v)); } catch (e) {} }
  };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function byId(list, id) { for (var i = 0; i < list.length; i++) if ((list[i].id || list[i][0]) === id) return list[i]; return null; }

  var ICON = {
    student: '<path d="M4 6.5C6.5 5 9.5 5 12 6.5 14.5 5 17.5 5 20 6.5V18c-2.5-1.5-5.5-1.5-8 0-2.5-1.5-5.5-1.5-8 0z"/><path d="M12 6.5V18"/>',
    work: '<rect x="3.5" y="7.5" width="17" height="11" rx="2"/><path d="M9 7.5V6a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 6v1.5M3.5 12.5h17"/>',
    family: '<path d="M4 11.5 12 5l8 6.5"/><path d="M6 10v8.5h12V10"/><path d="M10 18.5v-4h4v4"/>',
    me: '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 19.5c1.2-3.6 4-5.5 7-5.5s5.8 1.9 7 5.5"/>'
  };
  function icon(id) { return '<svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' + (ICON[id] || "") + "</svg>"; }

  function dots() {
    var order = ["who", "feel", "pick", "answer"], at = order.indexOf(S.step);
    if (at < 0) return "";
    var h = '<ol class="cx-dots" aria-label="Step ' + (at + 1) + ' of 4">';
    for (var i = 0; i < 4; i++) h += '<li class="' + (i < at ? "done" : i === at ? "on" : "") + '"></li>';
    return h + "</ol>";
  }
  function topbar() {
    return '<div class="cx-top">' + (S.hist.length ? '<button type="button" class="cx-back" data-act="back"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>Back</button>' : "<span></span>") + dots() + "</div>";
  }
  function writeBox(ph) {
    return '<form class="cx-write" data-act="write"><label class="sr" for="cx-text">Tell me in your own words</label>' +
      '<input id="cx-text" name="t" autocomplete="off" maxlength="400" placeholder="' + esc(ph) + '" value="' + esc(S.text) + '">' +
      '<button type="submit" aria-label="Find guidance"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button></form>';
  }
  function helpLink() { return '<p class="cx-helpline"><button type="button" class="cx-link" data-act="help" data-kind="crisis">Need to talk to someone right now?</button></p>'; }

  /* ---------------- steps ---------------- */
  function vWho() {
    var t = "";
    D.aud.forEach(function (a, i) {
      t += '<button type="button" class="cx-tile big" style="--i:' + i + '" data-act="aud" data-id="' + a[0] + '">' + icon(a[0]) + "<span>" + esc(a[1]) + "</span></button>";
    });
    return '<p class="cx-kicker">Ask S&#257;rathi</p><h1 class="cx-h">What&rsquo;s on your mind?</h1>' +
      '<p class="cx-q">Who&rsquo;s asking?</p><div class="cx-tiles four">' + t + "</div>" + writeBox("Or tell me in your own words\u2026") + helpLink();
  }
  function vFeel() {
    var t = "";
    D.feel.forEach(function (f, i) {
      t += '<button type="button" class="cx-tile feel f-' + f[0] + '" style="--i:' + i + '" data-act="feel" data-id="' + f[0] + '"><i aria-hidden="true"></i><span>' + esc(f[1]) + "</span></button>";
    });
    return '<p class="cx-kicker">' + esc(byId(D.aud, S.aud)[1]) + '</p><h1 class="cx-h">How does it feel?</h1><div class="cx-tiles six">' + t + "</div>" + helpLink();
  }
  function sitCard(s, i) {
    return '<button type="button" class="cx-sit" style="--i:' + i + '" data-act="sit" data-id="' + s.id + '"><span>' + esc(s.t) + '</span><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>';
  }
  function vPick() {
    var list, head, sub = "";
    if (S.matches) {
      list = S.matches;
      head = list.length ? "Is it one of these?" : "I couldn&rsquo;t place that yet.";
      if (!list.length) sub = '<p class="cx-q">Pick the feeling that&rsquo;s closest, and I&rsquo;ll take it from there.</p>';
    } else {
      list = D.sit.filter(function (s) { return s.a === S.aud && s.f.indexOf(S.feel) >= 0; });
      var more = D.sit.filter(function (s) { return s.a !== S.aud && s.f.indexOf(S.feel) >= 0; });
      list = list.concat(more).slice(0, 4);
      head = "Is it one of these?";
    }
    var h = "";
    list.forEach(function (s, i) { h += sitCard(s, i); });
    if (S.matches && !list.length) {
      D.feel.forEach(function (f, i) { h += '<button type="button" class="cx-tile feel slim f-' + f[0] + '" style="--i:' + i + '" data-act="feel" data-id="' + f[0] + '"><i aria-hidden="true"></i><span>' + esc(f[1]) + "</span></button>"; });
      return '<h1 class="cx-h">' + head + "</h1>" + sub + '<div class="cx-tiles six">' + h + "</div>" + writeBox("Try saying it another way\u2026") + helpLink();
    }
    return '<h1 class="cx-h">' + head + '</h1><div class="cx-sits">' + h +
      '<details class="cx-else" style="--i:' + list.length + '"><summary>Something else</summary>' + writeBox("Tell me what happened\u2026") + "</details></div>" + helpLink();
  }
  function vAnswer() {
    var s = byId(D.sit, S.sit), pair = s.v[S.vi], vid = pair[0], v = D.v[vid];
    var saved = store.get("saved", []), isSaved = saved.some(function (x) { return x.id === s.id && x.v === vid; });
    var fb = store.get("fb", {})[s.id + "@" + vid];
    var lines = v.sa.map(function (l, i) { return '<span style="--i:' + i + '">' + esc(l) + "</span>"; }).join("");
    var c = vid.split(".");
    return '<article class="cx-card">' +
      '<p class="cx-for">' + esc(s.t) + "</p>" +
      '<p class="cx-sa" lang="sa">' + lines + "</p>" +
      '<p class="cx-ref"><a href="' + v.url + '">Bhagavad Gita ' + c[0] + "." + c[1] + "</a></p>" +
      '<blockquote class="cx-en">' + esc(v.en) + "<cite>Swami Sivananda</cite></blockquote>" +
      '<dl class="cx-notes"><div style="--i:0"><dt>For you</dt><dd>' + esc(pair[1]) + "</dd></div>" +
      '<div style="--i:1"><dt>Try today</dt><dd>' + esc(s.do) + "</dd></div>" +
      '<div style="--i:2"><dt>Sit with</dt><dd>' + esc(s.ask) + "</dd></div></dl>" +
      '<div class="cx-acts">' +
      (v.audio ? '<button type="button" class="cx-btn" data-act="listen" title="A slow, word-by-word reading"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path class="i-play" d="M8 5v14l11-7z" fill="currentColor"/><path class="i-pause" d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/></svg><span>Listen</span></button>' : "") +
      (s.v.length > 1 ? '<button type="button" class="cx-btn" data-act="next"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 12a8 8 0 0 1 14-5.3M20 12a8 8 0 0 1-14 5.3M18 3v4h-4M6 21v-4h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Another verse <small>' + (S.vi + 1) + "/" + s.v.length + "</small></span></button>" : "") +
      '<button type="button" class="cx-btn' + (isSaved ? " on" : "") + '" data-act="save" aria-pressed="' + isSaved + '"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 4h12v16l-6-4-6 4z" fill="' + (isSaved ? "currentColor" : "none") + '" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg><span>' + (isSaved ? "Saved" : "Save") + "</span></button>" +
      "</div>" +
      '<div class="cx-fb">' + (fb ? '<p class="cx-thanks">' + (fb === "yes" ? "Glad it helped. It&rsquo;s here whenever you need it." : "Thanks for telling me. Try another verse, or tell me more:") + "</p>" + (fb === "no" ? writeBox("What\u2019s really going on?") : "") :
        '<span>Did this help?</span><button type="button" class="cx-pill" data-act="fb" data-v="yes">Yes</button><button type="button" class="cx-pill" data-act="fb" data-v="no">Not quite</button>') + "</div>" +
      '<p class="cx-note">The shloka and translation are from the Gita text. The three notes are S&#257;rathi&rsquo;s, written to help you apply it.</p>' +
      "</article>" +
      '<nav class="cx-deeper" aria-label="Go deeper"><a href="' + v.pr + '">Learn to recite it</a><a href="' + v.url + '">Read the commentaries</a><a href="' + v.url + '#h-map">See what it connects to</a><button type="button" class="cx-link" data-act="restart">Ask about something else</button></nav>';
  }
  function vHelp() {
    if (S.help === "unsafe") {
      return '<div class="cx-help"><h1 class="cx-h">Your safety comes first.</h1>' +
        '<p class="cx-q">If someone is hurting you, you deserve help. These lines are free and confidential.</p>' +
        '<ul class="cx-lines"><li><strong>In danger right now</strong><span>Call 911</span></li>' +
        '<li><strong>National Domestic Violence Hotline</strong><span>1-800-799-7233, or text START to 88788</span></li>' +
        '<li><strong>Under 18? Childhelp</strong><span>1-800-422-4453</span></li></ul>' +
        '<p class="cx-small">Outside the US, <a href="https://findahelpline.com" rel="noopener">findahelpline.com</a> lists free lines in your country.</p>' +
        '<button type="button" class="cx-link" data-act="restart">Back to S&#257;rathi</button></div>';
    }
    return '<div class="cx-help"><h1 class="cx-h">Please talk to someone now.</h1>' +
      '<p class="cx-q">You don&rsquo;t have to carry this alone. A trained person will listen, any hour, for free.</p>' +
      '<ul class="cx-lines"><li><strong>Call or text 988</strong><span>Suicide and Crisis Lifeline, US</span></li>' +
      '<li><strong>In danger right now</strong><span>Call 911</span></li>' +
      '<li><strong>Outside the US</strong><span><a href="https://findahelpline.com" rel="noopener">findahelpline.com</a></span></li></ul>' +
      '<p class="cx-small">If you can, tell one person near you how you&rsquo;re feeling.</p>' +
      '<button type="button" class="cx-link" data-act="restart">Back to S&#257;rathi</button></div>';
  }

  var VIEWS = { who: vWho, feel: vFeel, pick: vPick, answer: vAnswer, help: vHelp };
  function render(dir) {
    stopAudio();
    var el = document.createElement("div");
    el.className = "cx-step s-" + S.step + (dir === "back" ? " from-left" : "");
    el.innerHTML = (S.step === "help" ? "" : topbar()) + VIEWS[S.step]();
    var old = stage.querySelector(".cx-step");
    stage.innerHTML = "";
    stage.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("is-on"); });
    if (old && dir !== "same") {
      var h = el.querySelector(".cx-h, .cx-card");
      if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
      var top = root.getBoundingClientRect().top;
      if (top < 0) root.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    try { history.replaceState(null, "", S.step === "answer" ? "#" + S.sit + (S.vi ? "-" + (S.vi + 1) : "") : location.pathname); } catch (e) {}
    renderSaved();
  }
  function go(step) { S.hist.push({ step: S.step, matches: S.matches, vi: S.vi }); S.step = step; render(); }

  /* ---------------- matching ---------------- */
  function hits(text, words) {
    var n = 0;
    words.forEach(function (w) { if (text.indexOf(" " + w.toLowerCase()) >= 0) n += w.indexOf(" ") > 0 ? 2 : 1; });
    return n;
  }
  function match(raw) {
    var t = " " + raw.toLowerCase().replace(/[\u2018\u2019]/g, "'").replace(/[^a-z0-9' -]+/g, " ").replace(/\s+/g, " ") + " ";
    if (hits(t, D.crisis)) return { help: "crisis" };
    if (hits(t, D.unsafe)) return { help: "unsafe" };
    var feels = {}, auds = {};
    D.feel.forEach(function (f) { if (hits(t, f[2])) feels[f[0]] = 1; });
    D.aud.forEach(function (a) { if (hits(t, a[2])) auds[a[0]] = 1; });
    var scored = D.sit.map(function (s) {
      var sc = hits(t, s.w) * 2;
      s.f.forEach(function (f) { if (feels[f]) sc += 1.5; });
      if (auds[s.a] || s.a === S.aud) sc += 1;
      return { s: s, sc: sc };
    }).filter(function (x) { return x.sc >= 2; });
    scored.sort(function (a, b) { return b.sc - a.sc; });
    return { list: scored.slice(0, 3).map(function (x) { return x.s; }) };
  }

  /* ---------------- audio, saved ---------------- */
  function stopAudio() { if (audio) { audio.pause(); audio = null; } }
  function renderSaved() {
    var box = document.querySelector(".cx-saved"), ul = box && box.querySelector(".cx-savelist");
    if (!ul) return;
    var saved = store.get("saved", []);
    box.hidden = !saved.length;
    ul.innerHTML = saved.slice().reverse().map(function (x) {
      var s = byId(D.sit, x.id);
      if (!s) return "";
      var i = 0; s.v.forEach(function (p, k) { if (p[0] === x.v) i = k; });
      return '<li><button type="button" class="cx-sit slim" data-act="open" data-id="' + s.id + '" data-vi="' + i + '"><span>' + esc(s.t) + "<small>Gita " + esc(x.v) + "</small></span></button></li>";
    }).join("");
  }

  /* ---------------- events ---------------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-act]");
    if (!b || !root.parentNode.contains(b) || b.tagName === "FORM") return;
    var act = b.getAttribute("data-act"), id = b.getAttribute("data-id");
    if (act === "aud") { S.aud = id; S.matches = null; go("feel"); }
    else if (act === "feel") { S.feel = id; S.matches = null; if (!S.aud) S.aud = "me"; go("pick"); }
    else if (act === "sit" || act === "open") { S.sit = id; S.vi = +(b.getAttribute("data-vi") || 0); go("answer"); if (act === "open") root.scrollIntoView({ behavior: "smooth" }); }
    else if (act === "back") { var p = S.hist.pop(); if (p) { S.step = p.step; S.matches = p.matches; S.vi = p.vi; render("back"); } }
    else if (act === "next") { var s = byId(D.sit, S.sit); S.vi = (S.vi + 1) % s.v.length; render("same"); }
    else if (act === "restart") { S = { step: "who", aud: null, feel: null, sit: null, vi: 0, matches: null, text: "", help: null, hist: [] }; render(); }
    else if (act === "help") { S.help = b.getAttribute("data-kind"); go("help"); }
    else if (act === "save") {
      var s2 = byId(D.sit, S.sit), vid = s2.v[S.vi][0], saved = store.get("saved", []);
      var at = -1; saved.forEach(function (x, k) { if (x.id === s2.id && x.v === vid) at = k; });
      if (at >= 0) saved.splice(at, 1); else saved.push({ id: s2.id, v: vid, t: Date.now() });
      store.set("saved", saved); render("same");
    }
    else if (act === "fb") {
      var s3 = byId(D.sit, S.sit), fb = store.get("fb", {});
      fb[s3.id + "@" + s3.v[S.vi][0]] = b.getAttribute("data-v"); store.set("fb", fb); render("same");
    }
    else if (act === "listen") {
      var v = D.v[byId(D.sit, S.sit).v[S.vi][0]];
      if (audio) { stopAudio(); b.classList.remove("playing"); return; }
      audio = new Audio(v.audio); b.classList.add("playing");
      audio.addEventListener("ended", function () { b.classList.remove("playing"); audio = null; });
      audio.play().catch(function () { b.classList.remove("playing"); audio = null; });
    }
  });
  document.addEventListener("submit", function (e) {
    var f = e.target.closest(".cx-write");
    if (!f) return;
    e.preventDefault();
    var t = (f.querySelector("input").value || "").trim();
    if (!t) { f.querySelector("input").focus(); return; }
    S.text = t;
    var m = match(t);
    if (m.help) { S.help = m.help; go("help"); return; }
    S.matches = m.list; go("pick");
  });

  fetch(root.getAttribute("data-src")).then(function (r) { return r.json(); }).then(function (d) {
    D = d;
    var h = (location.hash || "").slice(1), mm = h.match(/^(.+?)(?:-(\d))?$/);
    if (mm && byId(D.sit, mm[1])) { S.sit = mm[1]; S.vi = mm[2] ? (+mm[2] - 1) : 0; S.step = "answer"; S.hist = [{ step: "who" }]; }
    render("same");
  }).catch(function () {
    stage.innerHTML = '<div class="cx-step is-on"><h1 class="cx-h">S&#257;rathi couldn&rsquo;t load.</h1><p class="cx-q">Check your connection and reload the page.</p></div>';
  });
})();
