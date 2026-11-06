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

  /* Scenes for who is asking. Line art, gold stroke; "k" shapes are filled to sit in front. */
  var SCENE = {
    student: '<path d="M18 54c2-9 7-14 14-14s12 5 14 14"/><circle cx="32" cy="28" r="7"/><path class="k" d="M19 17l13-6 13 6-13 6z"/><path d="M41 19v6"/><path class="k" d="M16 50l16 4 16-4v9l-16 4-16-4z"/><path d="M32 54v9"/>',
    work: '<circle cx="32" cy="19" r="7"/><path d="M18 44c2-9 7-14 14-14s12 5 14 14"/><rect class="k" x="16" y="34" width="32" height="19" rx="2"/><path d="M9 56h46"/><circle cx="32" cy="43.5" r="1.4" class="dot"/>',
    family: '<circle cx="20" cy="18" r="6"/><path d="M8 44c2-8 6-12 12-12s10 4 12 12"/><circle cx="44" cy="18" r="6"/><path d="M32 44c2-8 6-12 12-12s10 4 12 12"/><circle class="k" cx="32" cy="35" r="5"/><path class="k" d="M22 58c1.6-7 5-10.5 10-10.5S40.4 51 42 58z"/>',
    love: '<path class="heart" d="M32 18c-2.6-4.4-9-3.4-9 1.8 0 4 5.3 7.4 9 10 3.7-2.6 9-6 9-10 0-5.2-6.4-6.2-9-1.8z"/><circle cx="20" cy="34" r="6.5"/><path d="M7 60c2-9 7-13.5 13-13.5S31 51 33 60"/><circle class="k" cx="44" cy="34" r="6.5"/><path class="k" d="M31 60c2-9 7-13.5 13-13.5S55 51 57 60z"/>',
    me: '<circle cx="32" cy="13" r="6"/><path d="M32 20v14"/><path d="M32 25c-6 1-10 6-11 13M32 25c6 1 10 6 11 13"/><path class="k" d="M13 46c6-5 13-6 19-2 6-4 13-3 19 2-6 6-13 7-19 3-6 4-13 3-19-3z"/>'
  };
  function scene(id) { return '<svg class="cx-scene" viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">' + (SCENE[id] || "") + "</svg>"; }

  /* Faces drawn from the facial actions Ekman's FACS links to each emotion:
     anger = brows lowered and pulled together, narrowed eyes, pressed lips;
     fear = brows raised and drawn together, widened eyes, lips stretched open;
     sadness = inner brows raised, lids drooping, lip corners pulled down. */
  var FACE = {
    angry: '<path class="br" d="M17 21l10 4M47 21l-10 4"/><g class="ey"><circle cx="24" cy="31" r="2.3"/><circle cx="40" cy="31" r="2.3"/></g><path d="M24 45q8-3.5 16 0"/>',
    anxious: '<path class="br" d="M17 23q5-4 10-2.5M47 23q-5-4-10-2.5"/><g class="ey"><circle cx="24" cy="30" r="2.4"/><circle cx="40" cy="30" r="2.4"/></g><path d="M22 44q2.5-3 5 0t5 0 5 0 5 0"/><path class="sweat" d="M50 18q3 4.5 0 6.5-3-2 0-6.5z"/>',
    low: '<path class="br" d="M17 22q5-3.6 10-1M47 22q-5-3.6-10-1"/><path class="ey" d="M21 31q3 2.4 6 0M37 31q3 2.4 6 0"/><path d="M24 46q8-6 16 0"/>',
    hurt: '<path class="br" d="M18 23q4.5-4 9-2M46 23q-4.5-4-9-2"/><path class="ey" d="M21 30q3 2 6 0M37 30q3 2 6 0"/><path class="tear" d="M41 34q2.6 3.8 0 5.6-2.6-1.8 0-5.6z"/><path d="M26 45q3-2 6 0t6 0"/>',
    stuck: '<path class="br" d="M18 23h9M37 23h9"/><g class="ey"><path d="M20 29.5h8M36 29.5h8"/><path d="M21 29.5q3 3.4 6 0M37 29.5q3 3.4 6 0" class="lid"/></g><path d="M25 44.5h14"/><path class="loop" d="M50 13c3 0 4 3 1.8 4.4S49 20 52 21"/>',
    afraid: '<path class="br" d="M17 21q5-5.5 10-2.5M47 21q-5-5.5-10-2.5"/><g class="ey"><circle cx="24" cy="29.5" r="3.6"/><circle cx="40" cy="29.5" r="3.6"/><circle class="pu" cx="24" cy="29.5" r="1.1"/><circle class="pu" cx="40" cy="29.5" r="1.1"/></g><ellipse cx="32" cy="44.5" rx="6.5" ry="3.8"/>'
  };
  function face(id) { return '<svg class="cx-face" viewBox="0 0 64 64" width="64" height="64" aria-hidden="true"><circle class="disc" cx="32" cy="32" r="27"/>' + (FACE[id] || "") + "</svg>"; }

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
      t += '<button type="button" class="cx-tile big" style="--i:' + i + '" data-act="aud" data-id="' + a[0] + '">' + scene(a[0]) + "<span>" + esc(a[1]) + "</span></button>";
    });
    return '<p class="cx-kicker">Ask S&#257;rathi</p><h1 class="cx-h">What&rsquo;s on your mind?</h1>' +
      '<p class="cx-q">Who&rsquo;s asking?</p><div class="cx-tiles five">' + t + "</div>" + writeBox("Or tell me in your own words\u2026") + helpLink();
  }
  function vFeel() {
    var t = "";
    D.feel.forEach(function (f, i) {
      t += '<button type="button" class="cx-tile feel f-' + f[0] + '" style="--i:' + i + '" data-act="feel" data-id="' + f[0] + '">' + face(f[0]) + '<span>' + esc(f[1]) + "</span></button>";
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
      D.feel.forEach(function (f, i) { h += '<button type="button" class="cx-tile feel slim f-' + f[0] + '" style="--i:' + i + '" data-act="feel" data-id="' + f[0] + '">' + face(f[0]) + '<span>' + esc(f[1]) + "</span></button>"; });
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
