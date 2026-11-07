/* Sarathi front-end. Plain JS, no build step. ASCII only. */
(function () {
  "use strict";

  // ---------- storage (per-browser only, never required) ----------
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("sarathi." + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("sarathi." + k, JSON.stringify(v)); } catch (e) {} }
  };
  function readSet() { return store.get("read", []); }
  function isRead(id) { return readSet().indexOf(id) !== -1; }
  function setRead(id, on) {
    var s = readSet().filter(function (x) { return x !== id; });
    if (on) s.push(id);
    store.set("read", s);
    if (on) store.set("last", id);
  }

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  function escH(s) { return String(s || "").replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function vurl(id) { var p = id.split("."); return "/" + p[0] + "/" + p[1] + "/"; }
  var cache = {};
  var DIYA_ON = '<svg class="diya on" viewBox="0 0 40 46" aria-hidden="true"><circle cx="20" cy="15" r="13" fill="#FFC86B" opacity=".3"/><path d="M20 4C25 11 25 17 20 21 15 17 15 11 20 4Z" fill="#F5A623"/><path d="M20 10C22.5 13.5 22.5 16.5 20 19 17.5 16.5 17.5 13.5 20 10Z" fill="#FFE7A3"/><path d="M4 24C4 34 12 40 20 40S36 34 36 24Z" fill="#B5653E"/><path d="M3 24H37" stroke="#8C4A2B" stroke-width="2.4" stroke-linecap="round"/><path d="M14 40H26L24 44H16Z" fill="#8C4A2B"/></svg>';
  var DIYA_OFF = '<svg class="diya off" viewBox="0 0 40 46" aria-hidden="true"><circle class="fl" cx="20" cy="15" r="13" fill="#FFC86B" opacity=".3"/><path class="fl" d="M20 4C25 11 25 17 20 21 15 17 15 11 20 4Z" fill="#F5A623"/><path class="fl" d="M20 10C22.5 13.5 22.5 16.5 20 19 17.5 16.5 17.5 13.5 20 10Z" fill="#FFE7A3"/><path class="wick" d="M20 19V15" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path class="b" d="M4 24C4 34 12 40 20 40S36 34 36 24Z"/><path class="r" d="M3 24H37" stroke-width="2.4" stroke-linecap="round"/><path class="b2" d="M14 40H26L24 44H16Z"/></svg>';
  function learnedSet() {
    var r = store.get("recite", {}), out = [];
    for (var k in r) if (r[k] && r[k].learned != null) out.push(k);
    return out;
  }
  function themeState(vs, read, learned) {
    var n = 0, l = 0;
    vs.forEach(function (v) { if (learned.indexOf(v) !== -1) l++; if (read.indexOf(v) !== -1 || learned.indexOf(v) !== -1) n++; });
    return { n: n, l: l, of: vs.length, done: l === vs.length, started: n > 0 };
  }
  function lamps(vs, learned) { var k = 0; return vs.map(function (v) { return learned.indexOf(v) !== -1 ? DIYA_ON : DIYA_OFF.replace('class="diya off"', 'class="diya off" style="--k:' + (k++) + '"'); }).join(""); }
  var READ = store.get("read", []), LEARNED = learnedSet();
  (function themeCards() {
    Array.prototype.forEach.call(document.querySelectorAll(".tc3[data-v]"), function (c) {
      var vs = c.getAttribute("data-v").split(","), st = themeState(vs, READ, LEARNED), el = c.querySelector(".tc3-st");
      if (st.done) { c.classList.add("done"); el.innerHTML = DIYA_ON + "Learned by heart"; }
      else if (st.started) { c.classList.add("started"); el.innerHTML = '<span class="lamps">' + lamps(vs, LEARNED) + '</span><span class="vh">' + st.l + " of " + st.of + " learned</span>"; }
      else el.textContent = "Begin";
    });
  })();
  // which theme the learner is on: the first one started and not finished, else the first not finished
  function journey(themes) {
    var states = themes.map(function (t) { return themeState(t[2], READ, LEARNED); }), pick = -1, firstOpen = -1;
    states.forEach(function (x, k) { if (firstOpen < 0 && !x.done) firstOpen = k; if (pick < 0 && x.started && !x.done) pick = k; });
    if (pick < 0) pick = firstOpen < 0 ? 0 : firstOpen;
    var vs = themes[pick][2], nextV = vs.filter(function (x) { return LEARNED.indexOf(x) === -1; })[0] || vs[0];
    return { pick: pick, vs: vs, nextV: nextV, st: states[pick], states: states };
  }
  function lampRow(vs, nextV) {
    var k = 0, marked = false;
    return vs.map(function (x) {
      if (LEARNED.indexOf(x) !== -1) return DIYA_ON;
      var off = DIYA_OFF.replace('class="diya off"', 'class="diya off" style="--k:' + (k++) + '"');
      if (!marked && x === nextV) { marked = true; return '<span class="lamp-next">' + off + "</span>"; }
      return off;
    }).join("");
  }
  (function learnPage() {
    var ln = document.querySelector(".ln[data-themes]"); if (!ln) return;
    var themes = JSON.parse(ln.getAttribute("data-themes")), j = journey(themes);
    var nx = ln.querySelector(".ln-next");
    nx.setAttribute("href", vurl(j.nextV));
    nx.querySelector(".ln-nk").textContent = "Next up \u00b7 verse " + j.nextV;
    nx.querySelector(".ln-nt").textContent = themes[j.pick][1];
    nx.querySelector(".ln-lamps").innerHTML = lampRow(j.vs, j.nextV);
    Array.prototype.forEach.call(ln.querySelectorAll(".ln-row"), function (a, k) {
      var vs = a.getAttribute("data-v").split(","), st = j.states[k], el = a.querySelector(".ln-st");
      var next = vs.filter(function (x) { return LEARNED.indexOf(x) === -1; })[0] || vs[0];
      a.setAttribute("href", vurl(next));
      if (k === j.pick) a.classList.add("on");
      if (st.done) { a.classList.add("done"); el.textContent = "All " + st.of + " lit"; }
      else if (k === j.pick && !st.l) el.textContent = (k === 0 ? "Start here \u00b7 " : "Next \u00b7 ") + st.of + " verses";
      else el.textContent = st.l + " of " + st.of + " lit";
    });
  })();
  (function practiceFocus() {
    var pr = document.querySelector("article.practice"); if (!pr) return;
    var bar = pr.querySelector(".ptop .vtop-lamps");
    if (bar) bar.innerHTML = lampRow(bar.getAttribute("data-v").split(","), bar.getAttribute("data-here"));
    var say = pr.querySelector(".say-toggle");
    if (say) {
      var setSay = function (hide) {
        pr.classList.toggle("no-say", hide);
        say.setAttribute("aria-pressed", hide ? "true" : "false");
        say.textContent = hide ? "Show how to say it" : "Hide how to say it";
      };
      setSay(store.get("hideSay", false));
      say.addEventListener("click", function () { var h = !pr.classList.contains("no-say"); store.set("hideSay", h); setSay(h); });
    }
    var ob = pr.querySelector(".p-opts-btn"), dock = pr.querySelector(".psteps");
    if (ob && dock) ob.addEventListener("click", function () {
      var open = !dock.classList.contains("opts-open");
      dock.classList.toggle("opts-open", open); ob.setAttribute("aria-expanded", open ? "true" : "false");
    });
  })();
  (function versePage() {
    var art = document.querySelector("article.verse"); if (!art) return;
    // lamps: the theme bar at the top and the In Theme card
    var bar = art.querySelector(".vtop-lamps");
    if (bar) bar.innerHTML = lampRow(bar.getAttribute("data-v").split(","), bar.getAttribute("data-here"));
    Array.prototype.forEach.call(art.querySelectorAll(".tl-cell[data-v]"), function (a) {
      var on = LEARNED.indexOf(a.getAttribute("data-v")) !== -1;
      a.querySelector(".tr-lamp").innerHTML = on ? DIYA_ON : DIYA_OFF;
      if (on) a.classList.add("learned");
    });
    // Words / Explained / Connected: on phones one panel at a time; wide screens show them all
    var tabs = Array.prototype.slice.call(art.querySelectorAll(".v-tabs [data-tab]"));
    if (tabs.length) {
      art.classList.add("tabbed");
      var pick = function (id, focus) {
        tabs.forEach(function (b) { var on = b.getAttribute("data-tab") === id; b.setAttribute("aria-selected", on ? "true" : "false"); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); });
        Array.prototype.forEach.call(art.querySelectorAll("[data-tab]:not([role=tab])"), function (p) { p.classList.toggle("tab-off", p.getAttribute("data-tab") !== id); });
        try { sessionStorage.setItem("sarathi.vtab", id); } catch (e) {}
      };
      tabs.forEach(function (b, k) {
        b.addEventListener("click", function () { pick(b.getAttribute("data-tab")); });
        b.addEventListener("keydown", function (e) {
          var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (!d) return;
          e.preventDefault(); var n = tabs[(k + d + tabs.length) % tabs.length]; pick(n.getAttribute("data-tab"), true);
        });
      });
      var start = "words"; try { start = sessionStorage.getItem("sarathi.vtab") || "words"; } catch (e) {}
      if (!tabs.some(function (b) { return b.getAttribute("data-tab") === start; })) start = "words";
      pick(start);
    }
    // verse map: tap a word, its "why" opens under that stop; tap again to close
    Array.prototype.forEach.call(art.querySelectorAll(".vt-chip"), function (c) {
      c.addEventListener("click", function () {
        var stop = c.closest(".vt-stop"), why = stop.querySelector(".vt-why"), open = c.getAttribute("aria-expanded") === "true";
        Array.prototype.forEach.call(art.querySelectorAll(".vt-chip"), function (x) { x.setAttribute("aria-expanded", "false"); });
        Array.prototype.forEach.call(art.querySelectorAll(".vt-why"), function (w) { w.hidden = true; });
        if (open) return;
        c.setAttribute("aria-expanded", "true");
        why.innerHTML = escH(c.getAttribute("data-why")) + ' <a href="' + escH(c.getAttribute("data-href")) + '">' + escH(c.getAttribute("data-go")) + " \u203a</a>";
        why.hidden = false;
      });
    });
  })();
  (function themeRail() {
    Array.prototype.forEach.call(document.querySelectorAll(".tp-list li[data-v], .p-theme li[data-v], .ppath li[data-v]"), function (li) {
      var v = li.getAttribute("data-v"), on = LEARNED.indexOf(v) !== -1;
      li.querySelector(".tr-lamp").innerHTML = on ? DIYA_ON : DIYA_OFF;
      if (on) li.classList.add("learned"); else if (READ.indexOf(v) !== -1) li.classList.add("read");
    });
  })();
  (function themeFocus() {
    var tp = document.querySelector(".tp"); if (!tp) return;
    var cards = Array.prototype.slice.call(tp.querySelectorAll(".tp-main .fcard"));
    var items = Array.prototype.slice.call(tp.querySelectorAll(".tp-list li"));
    if (!cards.length) return;
    tp.classList.add("focus");
    cards.forEach(function (c, k) {
      var pv = cards[k - 1], nx = cards[k + 1], nav = document.createElement("div");
      nav.className = "tp-pager";
      nav.innerHTML = (pv ? '<a class="btn ghost" href="#' + pv.id + '">\u2039 ' + pv.id.slice(2).replace("-", ".") + "</a>" : "<span></span>") +
        (nx ? '<a class="btn" href="#' + nx.id + '">Next verse \u00b7 ' + nx.id.slice(2).replace("-", ".") + " \u203a</a>" : '<a class="btn" href="/themes/">Back to all themes</a>');
      c.appendChild(nav);
    });
    function show(id, scroll) {
      var hit = cards.filter(function (c) { return c.id === id; })[0];
      if (!hit) {
        hit = cards.filter(function (c) { return LEARNED.indexOf(c.id.slice(2).replace("-", ".")) === -1; })[0] || cards[0];
      }
      cards.forEach(function (c) { c.hidden = c !== hit; if (c === hit) { c.classList.remove("in"); void c.offsetWidth; c.classList.add("in"); } });
      items.forEach(function (li) { li.classList.toggle("on", "v-" + li.getAttribute("data-v").replace(".", "-") === hit.id); });
      if (scroll && innerWidth < 1100) hit.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function top() { if (innerWidth >= 1100) requestAnimationFrame(function () { scrollTo(0, 0); }); }
    show((location.hash || "").slice(1), false); top();
    // arriving with a verse in the address (from the home page's journey card): start at the
    // top of the page, on every screen size, rather than wherever the browser jumped to
    if (location.hash) {
      if ("scrollRestoration" in history) history.scrollRestoration = "manual";
      var up = function () { scrollTo(0, 0); };
      requestAnimationFrame(up); addEventListener("load", function () { setTimeout(up, 0); });
    }
    addEventListener("hashchange", function () { show(location.hash.slice(1), true); top(); });
    document.addEventListener("keydown", function (e) {
      if (e.target.closest && e.target.closest("input,textarea,select")) return;
      var cur = cards.filter(function (c) { return !c.hidden; })[0], k = cards.indexOf(cur);
      if (e.key === "ArrowRight" && cards[k + 1]) location.hash = cards[k + 1].id;
      if (e.key === "ArrowLeft" && cards[k - 1]) location.hash = cards[k - 1].id;
    });
  })();
  (function sky() {
    var sk = document.querySelector(".sky"); if (!sk) return;
    var t = document.documentElement.getAttribute("data-sky") || "day";
    var greet = { morning: "Namaste. Good morning.", day: "Namaste. Good afternoon.", evening: "Namaste. Good evening.", night: "Namaste. Can\u2019t sleep? You\u2019re not alone." }[t];
    sk.querySelector(".sky-greet").textContent = greet;
    var tod = JSON.parse(sk.getAttribute("data-tod")), d = Math.floor(Date.now() / 86400000), v = tod[d % tod.length];
    sk.querySelector(".sky-tod .sky-kt").innerHTML = "<span class=\"sky-kl\">Krishna says</span><span class=\"sky-kp\">Today\u2019s verse</span><span class=\"sky-kn\"> \u00b7 " + v[0] + "</span>";
    sk.querySelector(".sky-ref a").textContent = "Read " + v[0] + " in full";
    var qEn = sk.querySelector(".sky-q:not(.sky-qsa)"), qSa = sk.querySelector(".sky-qsa");
    qEn.textContent = "\u201c" + v[1] + "\u201d";
    qSa.innerHTML = (v[3] || []).map(function (l) { return String(l).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }).join("<br>");
    // Sanskrit or English for today's verse; the choice is remembered on this device
    function lang(l) {
      if (!v[3] || !v[3].length) l = "en";
      qEn.hidden = l !== "en"; qSa.hidden = l !== "sa";
      Array.prototype.forEach.call(sk.querySelectorAll(".sky-lang button"), function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-l") === l ? "true" : "false"); });
    }
    lang(store.get("todlang", "en"));
    Array.prototype.forEach.call(sk.querySelectorAll(".sky-lang button"), function (b) {
      b.addEventListener("click", function () { var l = b.getAttribute("data-l"); store.set("todlang", l); lang(l); });
    });
    var p = v[0].split("."); sk.querySelector(".sky-ref a").setAttribute("href", "/" + p[0] + "/" + p[1] + "/");
    var themes = JSON.parse(sk.getAttribute("data-themes")), pick = 0, st, any = false;
    var states = themes.map(function (t) { return themeState(t[2], READ, LEARNED); }), firstOpen = -1;
    states.forEach(function (x, k) { if (x.started) any = true; if (firstOpen < 0 && !x.done) firstOpen = k; });
    pick = -1; states.forEach(function (x, k) { if (pick < 0 && x.started && !x.done) pick = k; });
    if (pick < 0) pick = firstOpen < 0 ? 0 : firstOpen;
    st = themeState(themes[pick][2], READ, LEARNED);
    var card = sk.querySelector(".sky-learn"), vs = themes[pick][2];
    var nextV = vs.filter(function (x) { return LEARNED.indexOf(x) === -1; })[0] || vs[0];
    var ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"];
    var title = "Light your " + (ORD[st.l] || ("next")) + " lamp";
    card.querySelector(".sky-cnt").textContent = st.l + " of " + st.of + " lit";
    card.querySelector(".sky-sub").textContent = "Theme " + (pick + 1) + " \u00b7 " + themes[pick][1] + (st.l ? "" : " \u00b7 " + st.of + " verses");
    // lit lamps for verses learned by heart; the next one glows, ready to be lit
    var k = 0, marked = false;
    card.querySelector(".sky-lamps").innerHTML = vs.map(function (x) {
      if (LEARNED.indexOf(x) !== -1) return DIYA_ON;
      var off = DIYA_OFF.replace('class="diya off"', 'class="diya off" style="--k:' + (k++) + '"');
      if (!marked && x === nextV) { marked = true; return '<span class="lamp-next">' + off + "</span>"; }
      return off;
    }).join("");
    var go = card.querySelector(".sky-hit");
    go.textContent = title;
    go.setAttribute("href", vurl(nextV));
    go.setAttribute("aria-label", title + ": verse " + nextV + ", theme " + (pick + 1) + ", " + themes[pick][1]);
    if (any) sk.classList.add("journey");
  })();
  (function textSize() {
    var b = document.querySelector(".nav-size"); if (!b) return;
    var steps = [1, 1.15, 1.3], names = ["normal", "large", "largest"];
    function apply(z) {
      document.documentElement.style.setProperty("--zoom", z);
      var i = steps.indexOf(z); if (i < 0) i = 0;
      b.setAttribute("aria-label", "Text size: " + names[i] + ". Tap to change.");
      b.classList.toggle("on", i > 0);
    }
    var cur = store.get("textsize", 1); apply(cur);
    b.addEventListener("click", function () {
      var i = steps.indexOf(store.get("textsize", 1)); var z = steps[(i + 1) % steps.length];
      store.set("textsize", z); apply(z);
    });
  })();
  (function themeSwitch() {
    // Dark is the default; Light is remembered per device (read before paint in the page head).
    var b = document.querySelector(".nav-theme"); if (!b) return;
    var root = document.documentElement, meta = document.querySelector('meta[name="theme-color"]');
    function apply(t) {
      root.setAttribute("data-theme", t);
      var other = t === "dark" ? "Light" : "Dark";
      b.setAttribute("aria-label", "Switch to " + other.toLowerCase() + " colours");
      b.querySelector(".nt-l").textContent = other;
      if (meta) meta.setAttribute("content", t === "dark" ? "#071E22" : "#F4F7F6");
    }
    apply(root.getAttribute("data-theme") === "light" ? "light" : "dark");
    b.addEventListener("click", function () {
      var t = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      try { localStorage.setItem("sarathi.theme", t); } catch (e) {}
      apply(t);
    });
  })();
  function getJSON(u) {
    if (!cache[u]) cache[u] = fetch(u).then(function (r) { if (!r.ok) throw new Error(u); return r.json(); });
    return cache[u];
  }
  function dayNumber(d) { d = d || new Date(); return Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000); }
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- audio player with "repeat after me" ----------
  // Two recordings where we have both: "Chant" (Aarsha Vidya Varshini, teacher chants a
  // line and students repeat it) and "Word by word" (slow reading from the dataset).
  function Player(root) {
    var a = new Audio(), slow = root.getAttribute("data-src"), chant = root.getAttribute("data-chant"), src = slow;
    a.preload = "none";
    var btn = $(".play", root), bar = $(".p-bar", root), rep = $(".repeat", root), spd = $(".p-speed", root);
    var rounds = 0, waitT = null;
    function ui() { root.classList.toggle("playing", !a.paused || !!waitT); }
    function stop() { a.pause(); clearTimeout(waitT); waitT = null; root.classList.remove("wait"); rounds = 0; ui(); }
    if (chant) {
      var mode = "chant";
      try { mode = localStorage.getItem("sarathi.listen") || "chant"; } catch (e) {}
      var sw = document.createElement("div");
      sw.className = "p-src"; sw.setAttribute("role", "group"); sw.setAttribute("aria-label", "Recording");
      sw.innerHTML = '<button type="button" data-m="chant">Chant</button><button type="button" data-m="slow">Word by word</button>';
      root.insertBefore(sw, rep ? rep.parentNode : spd);
      var cr = document.createElement("p");
      cr.className = "p-credit";
      cr.innerHTML = 'Chanting by <a href="' + root.getAttribute("data-credit-url") + '" target="_blank" rel="noopener">' + root.getAttribute("data-credit") + "</a>, used with permission.";
      root.parentNode.insertBefore(cr, root.nextSibling);
      var setMode = function (m) {
        mode = m; src = m === "chant" ? chant : slow;
        $$("button", sw).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-m") === m ? "true" : "false"); });
        root.classList.toggle("is-chant", m === "chant");
        cr.hidden = m !== "chant";
        if (rep && m === "chant") rep.checked = false;
        if (a.src) { stop(); a.removeAttribute("src"); a.load(); bar.style.width = "0"; }
      };
      $$("button", sw).forEach(function (b) {
        b.addEventListener("click", function () {
          setMode(b.getAttribute("data-m"));
          try { localStorage.setItem("sarathi.listen", mode); } catch (e) {}
        });
      });
      setMode(mode === "slow" ? "slow" : "chant");
    }
    btn.addEventListener("click", function () {
      if (!a.paused || waitT) { stop(); return; }
      if (!a.getAttribute("src")) a.src = src;
      a.playbackRate = parseFloat(spd.value) || 1;
      rounds = 0;
      a.play();
      ui();
    });
    spd.addEventListener("change", function () { a.playbackRate = parseFloat(spd.value) || 1; });
    a.addEventListener("timeupdate", function () { if (a.duration) bar.style.width = (100 * a.currentTime / a.duration) + "%"; });
    a.addEventListener("pause", ui);
    a.addEventListener("ended", function () {
      bar.style.width = "100%";
      if (rep.checked && rounds < 2) {
        // Leave a gap as long as the verse so the listener can chant it back.
        rounds++;
        root.classList.add("wait");
        var gap = (a.duration || 8) * 1000 / (a.playbackRate || 1);
        waitT = setTimeout(function () { waitT = null; root.classList.remove("wait"); a.currentTime = 0; a.play(); ui(); }, gap);
        ui();
      } else { rounds = 0; ui(); }
    });
  }
  $$(".player").forEach(Player);

  // ---------- home hero: the verse explains itself ----------
  var hero = $(".hero-verse");
  if (hero) {
    var hws = $$(".hw", hero), out = $(".hv-meaning", hero), idx = -1, timer = null, userTook = false;
    function show(i) {
      hws.forEach(function (w, j) { w.classList.toggle("on", j === i); });
      out.textContent = i >= 0 ? hws[i].getAttribute("data-m") : "\u00a0";
    }
    function step() { idx = (idx + 1) % hws.length; show(idx); }
    function auto(ms) { clearInterval(timer); timer = setInterval(step, ms); }
    hws.forEach(function (w, j) {
      function take() { userTook = true; clearInterval(timer); idx = j; show(j); }
      w.addEventListener("mouseenter", take);
      w.addEventListener("focus", take);
      w.addEventListener("click", take);
    });
    if (!reduced) { setTimeout(function () { if (!userTook) { step(); auto(1700); } }, 900); }
    else { show(0); }
    // Listen: play the real recitation and walk the words through it.
    var ha = null, hbtn = $(".hv-play", hero);
    hbtn.addEventListener("click", function () {
      if (!ha) { ha = new Audio(hero.getAttribute("data-src")); ha.addEventListener("ended", function () { hbtn.classList.remove("playing"); clearInterval(timer); show(-1); }); }
      if (!ha.paused) { ha.pause(); hbtn.classList.remove("playing"); clearInterval(timer); return; }
      ha.currentTime = 0; ha.play(); hbtn.classList.add("playing");
      idx = -1; userTook = true;
      var go = function () { auto(Math.max(500, (ha.duration * 1000) / hws.length)); step(); };
      if (ha.duration) go(); else ha.addEventListener("loadedmetadata", go, { once: true });
    });
  }

  // ---------- today's verse ----------
  var vod = $(".vod");
  if (vod) {
    var order = JSON.parse(vod.getAttribute("data-order"));
    var id = order[dayNumber() % order.length];
    getJSON("/data/search.json").then(function (rows) {
      var r = rows.filter(function (x) { return x[0] === id; })[0];
      if (!r) return;
      $(".vod-body", vod).innerHTML = '<p class="vsa" lang="sa">' + escH(r[5]) + '</p><p class="ven">' + escH(r[2]) +
        '</p><a class="btn ghost" href="' + vurl(id) + '">Read ' + id + " in full</a>";
    }).catch(function () {});
  }

  // ---------- chapter progress ----------
  var rows = $$(".crow");
  if (rows.length) {
    var read = readSet();
    rows.forEach(function (row) {
      var ch = row.getAttribute("data-ch");
      var n = read.filter(function (x) { return x.split(".")[0] === ch; }).length;
      if (n) {
        var meta = $(".cmeta", row).textContent, total = parseInt(meta.replace(/.*?(\d+) verses.*/, "$1"), 10) || 1;
        $(".cprog", row).innerHTML = '<i style="width:' + Math.min(100, 100 * n / total) + '%"></i>';
      }
    });
  }
  var resume = $(".resume");
  if (resume) {
    var last = store.get("last", null), ch = resume.getAttribute("data-ch");
    if (last && last.split(".")[0] === ch) {
      var nxt = parseInt(last.split(".")[1], 10) + 1;
      resume.hidden = false;
      resume.textContent = "Resume at verse " + nxt;
      resume.addEventListener("click", function () { location.href = "/" + ch + "/" + nxt + "/"; });
    }
  }

  // ---------- verse page ----------
  var verse = $(".verse");
  if (verse) {
    var vid = verse.getAttribute("data-vid");

    // translation tabs, remembered
    var tabs = $$('.tabs [role="tab"]', verse);
    function selectTab(t) {
      tabs.forEach(function (b) {
        var on = b === t;
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
        document.getElementById(b.getAttribute("aria-controls")).hidden = !on;
      });
    }
    tabs.forEach(function (b, i) {
      b.tabIndex = i === 0 ? 0 : -1;
      b.addEventListener("click", function () { selectTab(b); store.set("tr", b.getAttribute("data-tr")); });
      b.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (d) { var n = tabs[(i + d + tabs.length) % tabs.length]; n.focus(); n.click(); }
      });
    });
    var pref = store.get("tr", null);
    if (pref) { var pt = tabs.filter(function (b) { return b.getAttribute("data-tr") === pref; })[0]; if (pt) selectTab(pt); }

    // word layer: every verse a word appears in
    var pop = $(".word-pop", verse), openBtn = null;
    $$(".word", verse).forEach(function (b) {
      b.setAttribute("aria-expanded", "false");
      b.addEventListener("click", function () {
        if (openBtn === b) { pop.hidden = true; b.setAttribute("aria-expanded", "false"); openBtn = null; return; }
        if (openBtn) openBtn.setAttribute("aria-expanded", "false");
        openBtn = b; b.setAttribute("aria-expanded", "true");
        var keys = (b.getAttribute("data-k") || "").split(" ").filter(Boolean);
        pop.hidden = false; pop.innerHTML = "<p>Looking up...</p>";
        b.parentNode.insertBefore(pop, b.nextSibling);
        Promise.all([getJSON("/data/words.json"), getJSON("/data/wordpages.json")]).then(function (res) {
          var W = res[0], pages = res[1], html = "", tapped = $(".w-sa", b).textContent, here = $(".w-m", b).textContent;
          html += "<h3>" + escH(tapped) + "</h3><p>Here it means: " + escH(here) + ".</p>";
          keys.forEach(function (k) {
            var e = W[k]; if (!e) return;
            var others = e[2].filter(function (x) { return x !== vid; });
            var label = keys.length > 1 ? escH(e[0]) + " appears " : "It appears ";
            html += "<p>" + label + (others.length ? "in " + others.length + " other verse" + (others.length === 1 ? "" : "s") + ", most often meaning: " + escH(e[1]) + "." : "only in this verse.") + "</p>";
            if (others.length) {
              html += "<ul>" + others.slice(0, 24).map(function (x) { return '<li><a href="' + vurl(x) + '">' + x + "</a></li>"; }).join("") + "</ul>";
              if (pages.indexOf(k) !== -1) html += '<a class="more" href="/word/' + k + '/">See every use of ' + escH(e[0]) + "</a>";
            }
          });
          pop.innerHTML = html || "<p>No other uses found.</p>";
        }).catch(function () { pop.innerHTML = "<p>Couldn't load the word index. Check your connection and tap again.</p>"; });
      });
    });

    // commentaries, loaded on demand
    var cmOut = $(".cm-out", verse), cmBtns = $$(".cm-btn", verse);
    cmBtns.forEach(function (b) {
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () {
        var on = b.getAttribute("aria-pressed") === "true";
        cmBtns.forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        if (on) { cmOut.hidden = true; return; }
        b.setAttribute("aria-pressed", "true");
        b.closest(".trad").appendChild(cmOut);
        cmOut.hidden = false; cmOut.textContent = "Loading...";
        getJSON("/data/c/" + vid + ".json").then(function (C) {
          var a = b.getAttribute("data-author");
          cmOut.innerHTML = "<h3>" + escH(a) + "</h3>" + escH(C[a] || "Not available for this verse.");
        }).catch(function () { cmOut.textContent = "Couldn't load this commentary. Check your connection and try again."; });
      });
    });

    // mark as read
    var mark = $(".mark", verse);
    function markUI() { var on = isRead(vid); mark.textContent = on ? "Read" : "Mark as read"; mark.classList.toggle("done", on); mark.setAttribute("aria-pressed", on ? "true" : "false"); }
    mark.addEventListener("click", function () { setRead(vid, !isRead(vid)); markUI(); });
    markUI();
    store.set("last", vid);

    // share card
    var dlg = $(".card-dlg"), canvas = $("canvas", dlg), data = JSON.parse(verse.getAttribute("data-card"));
    $(".share", verse).addEventListener("click", function () {
      (document.fonts && document.fonts.load ? Promise.all([
        document.fonts.load('64px "Tiro Devanagari Sanskrit"'),
        document.fonts.load('italic 40px "Tiro Devanagari Sanskrit"'),
        document.fonts.load('600 30px "Instrument Sans"')]) : Promise.resolve()).then(function () {
        drawCard(canvas, data);
        if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
      });
    });
    $(".close", dlg).addEventListener("click", function () { dlg.close ? dlg.close() : dlg.removeAttribute("open"); });
    $(".dl", dlg).addEventListener("click", function () {
      var a = el("a", { href: canvas.toDataURL("image/png"), download: "bhagavad-gita-" + vid.replace(".", "-") + ".png" });
      document.body.appendChild(a); a.click(); a.remove();
    });
    var sh = $(".sh", dlg);
    if (navigator.canShare && window.File) {
      sh.hidden = false;
      sh.addEventListener("click", function () {
        canvas.toBlob(function (blob) {
          var f = new File([blob], "gita-" + vid + ".png", { type: "image/png" });
          var payload = { files: [f], title: "Bhagavad Gita " + vid, url: location.href };
          if (navigator.canShare(payload)) navigator.share(payload).catch(function () {});
        });
      });
    }
  }

  function wrap(ctx, text, maxW) {
    var words = text.split(/\s+/), lines = [], line = "";
    words.forEach(function (w) {
      var t = line ? line + " " + w : w;
      if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t;
    });
    if (line) lines.push(line);
    return lines;
  }
  function drawCard(c, d) {
    var x = c.getContext("2d"), W = c.width, H = c.height, pad = 96, maxW = W - pad * 2;
    var g = x.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "#145F65"); g.addColorStop(0.6, "#0B3B40"); g.addColorStop(1, "#24306E");
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    var r = x.createRadialGradient(W - 150, 170, 10, W - 150, 170, 260);
    r.addColorStop(0, "rgba(36,48,110,.95)"); r.addColorStop(0.35, "rgba(15,82,87,.6)"); r.addColorStop(0.55, "rgba(201,162,39,.35)"); r.addColorStop(1, "rgba(201,162,39,0)");
    x.fillStyle = r; x.fillRect(0, 0, W, H);
    x.textBaseline = "alphabetic";
    function lines(font, arr) { x.font = font; var o = []; arr.forEach(function (l) { o = o.concat(wrap(x, l, maxW)); }); return o; }
    // Fit the block to the space between the header and the footer link.
    var top = pad + 150, bottom = H - pad - 80, room = bottom - top, L;
    var sizes = [[64, 34, 46], [56, 30, 40], [50, 28, 36], [44, 26, 32]];
    for (var i = 0; i < sizes.length; i++) {
      var s = sizes[i];
      L = {
        s: s,
        sa: lines(s[0] + 'px "Tiro Devanagari Sanskrit", serif', d.sa),
        tl: lines("italic " + s[1] + 'px "Tiro Devanagari Sanskrit", serif', d.tl).slice(0, 4),
        en: lines(s[2] + 'px "Tiro Devanagari Sanskrit", serif', [d.en])
      };
      L.h = L.sa.length * s[0] * 1.5 + 36 + L.tl.length * s[1] * 1.45 + 48 + L.en.length * s[2] * 1.42;
      if (L.h <= room) break;
    }
    var y = top + Math.max(0, (room - L.h) / 2) + L.s[0];
    x.fillStyle = "#C9A227"; x.fillRect(pad, pad, 90, 6);
    x.fillStyle = "#E9D58A"; x.font = '600 30px "Instrument Sans", sans-serif';
    x.fillText("Bhagavad Gita " + d.id, pad, pad + 70);
    x.fillStyle = "#FFFFFF"; x.font = L.s[0] + 'px "Tiro Devanagari Sanskrit", serif';
    L.sa.forEach(function (l) { x.fillText(l, pad, y); y += L.s[0] * 1.5; });
    y += 36 - L.s[0] * 0.5 + L.s[1];
    x.fillStyle = "#9FC2BC"; x.font = "italic " + L.s[1] + 'px "Tiro Devanagari Sanskrit", serif';
    L.tl.forEach(function (l) { x.fillText(l, pad, y); y += L.s[1] * 1.45; });
    y += 48 - L.s[1] * 0.45 + L.s[2] * 0.4;
    x.fillStyle = "#EAF4F1"; x.font = L.s[2] + 'px "Tiro Devanagari Sanskrit", serif';
    var en = L.en, maxLines = Math.floor((bottom - y) / (L.s[2] * 1.42)) + 1;
    if (en.length > maxLines) { en = en.slice(0, maxLines); en[maxLines - 1] = en[maxLines - 1].replace(/\s+\S*$/, "") + "..."; }
    en.forEach(function (l) { x.fillText(l, pad, y); y += L.s[2] * 1.42; });
    x.fillStyle = "#E9D58A"; x.font = '600 28px "Instrument Sans", sans-serif';
    x.fillText(location.host + vurl(d.id), pad, H - pad);
  }

  // ---------- search ----------
  var q = $("#q");
  if (q) {
    var list = $(".s-results"), status = $(".s-status"), data = null;
    var params = new URLSearchParams(location.search);
    function fold(s) { return (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); }
    function run() {
      var raw = q.value.trim();
      history.replaceState(null, "", raw ? "?q=" + encodeURIComponent(raw) : location.pathname);
      if (!raw) { list.innerHTML = ""; status.textContent = "Searches the transliteration, word meanings and five English translations."; return; }
      var m = raw.match(/^(\d{1,2})[.:\s](\d{1,2})$/);
      if (m) { location.href = "/" + m[1] + "/" + m[2] + "/"; return; }
      var terms = fold(raw).split(/\s+/).filter(function (t) { return t.length > 1; });
      var hits = [];
      data.forEach(function (r) {
        var tl = fold(r[1]), en = fold(r[2] + " " + r[3]), wm = fold(r[4]), s = 0;
        terms.forEach(function (t) {
          if (en.indexOf(t) !== -1) s += 3;
          if (wm.indexOf(t) !== -1) s += 2;
          if (tl.indexOf(t) !== -1) s += 2;
        });
        if (fold(r[2] + " " + r[3] + " " + r[4]).indexOf(fold(raw)) !== -1) s += 6;
        var all = terms.every(function (t) { return (tl + en + wm).indexOf(t) !== -1; });
        if (s && all) hits.push([s, r]);
      });
      hits.sort(function (a, b) { return b[0] - a[0]; });
      status.textContent = hits.length ? hits.length + " verse" + (hits.length === 1 ? "" : "s") + " found." : "No verses matched. Try a simpler word, like \"mind\" or \"duty\".";
      var re = new RegExp("(" + terms.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + ")", "gi");
      list.innerHTML = hits.slice(0, 60).map(function (h) {
        var r = h[1];
        return '<li class="vrow"><a href="' + vurl(r[0]) + '"><span class="vnum">' + r[0] + '</span><span class="vsa" lang="sa">' + escH(r[5]) +
          '</span><span class="ven">' + escH(r[2]).replace(re, "<mark>$1</mark>") + "</span></a></li>";
      }).join("");
    }
    getJSON("/data/search.json").then(function (d) {
      data = d;
      if (params.get("q")) q.value = params.get("q");
      run();
      var t; q.addEventListener("input", function () { clearTimeout(t); t = setTimeout(run, 120); });
    });
  }

  // ---------- plans ----------
  var plansEl = $(".plans");
  if (plansEl) {
    getJSON("/data/plans.json").then(function (P) {
      function render() {
        var cur = store.get("plan", null), read = readSet();
        $$(".plan", plansEl).forEach(function (card) {
          var k = card.getAttribute("data-plan"), active = cur && cur.id === k, p = P[k];
          card.classList.toggle("active", !!active);
          var btn = $(".start", card);
          if (active) {
            var done = p.days.filter(function (d) { return d.every(function (x) { return read.indexOf(x) !== -1; }); }).length;
            $(".plan-state", card).textContent = "In progress: " + done + " of " + p.days.length + " " + (p.unit || "day") + "s done.";
            btn.textContent = "Stop this plan";
          } else { $(".plan-state", card).textContent = ""; btn.textContent = "Start this plan"; }
        });
        var today = $(".today");
        if (cur && P[cur.id]) {
          var p = P[cur.id], unitDays = p.unit === "week" ? 7 : 1;
          var i = Math.min(p.days.length - 1, Math.floor((dayNumber() - cur.start) / unitDays));
          var day = p.days[i];
          today.hidden = false;
          today.innerHTML = '<div class="today-in"><h2>' + escH(p.name) + ", " + (p.unit || "day") + " " + (i + 1) + (p.labels ? ": " + escH(p.labels[i]) : "") + "</h2>" +
            '<div class="chips">' + day.map(function (x) { return '<a class="chip' + (read.indexOf(x) !== -1 ? " read" : "") + '" href="' + vurl(x) + '">' + x + "</a>"; }).join("") + "</div></div>";
        } else today.hidden = true;
      }
      $$(".plan .start", plansEl).forEach(function (b) {
        b.addEventListener("click", function () {
          var k = b.closest(".plan").getAttribute("data-plan"), cur = store.get("plan", null);
          store.set("plan", cur && cur.id === k ? null : { id: k, start: dayNumber() });
          render();
        });
      });
      render();
    });
  }
})();
