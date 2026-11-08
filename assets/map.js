/* Sarathi knowledge graph: verse maps, the feeling journey and the path finder. ASCII only. */
(function () {
  "use strict";
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function escH(s) { return String(s || "").replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function vurl(id) { var p = id.split("."); return "/" + p[0] + "/" + p[1] + "/"; }
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SVGNS = "http://www.w3.org/2000/svg";
  var cache = {};
  function dv(u) { var m = document.querySelector('meta[name="sarathi-data"]'); return m && u.indexOf("/data/") === 0 && u.indexOf("?") < 0 ? u + "?v=" + m.getAttribute("content") : u; }
  function getJSON(u) { u = dv(u); if (!cache[u]) cache[u] = fetch(u).then(function (r) { if (!r.ok) throw new Error(u); return r.json(); }); return cache[u]; }

  // ---------- verse map ----------
  function colorOf(n) {
    if (n.classList.contains("st-a")) return "#B4533A";
    if (n.classList.contains("st-h")) return "#1F7A7A";
    if (n.classList.contains("sit") || n.classList.contains("chain")) return "#C9A227";
    if (n.classList.contains("idea")) return "#4B5AA8";
    return "#0F5257";
  }
  function drawMap(vm, animate) {
    var svg = $(".vm-lines", vm), hub = $(".vm-hub", vm);
    var box = vm.getBoundingClientRect(), hb = hub.getBoundingClientRect();
    svg.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);
    svg.setAttribute("width", box.width); svg.setAttribute("height", box.height);
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var hx = hb.left - box.left, hy = hb.top - box.top, hw = hb.width, hh = hb.height;
    var cx = hx + hw / 2, cy = hy + hh / 2;
    $$(".vm-node", vm).forEach(function (n, i) {
      var r = n.getBoundingClientRect();
      var nx = r.left - box.left, ny = r.top - box.top, ncx = nx + r.width / 2, ncy = ny + r.height / 2, d;
      var stacked = ncx > hx - 10 && ncx < hx + hw + 10 || Math.abs(ncx - cx) < Math.abs(ncy - cy) * 0.6;
      if (stacked) {
        var down = ncy > cy, sy = down ? hy + hh : hy, ey = down ? ny : ny + r.height, my = (sy + ey) / 2;
        d = "M" + cx + " " + sy + " C" + cx + " " + my + " " + ncx + " " + my + " " + ncx + " " + ey;
      } else if (ncx < cx) {
        var sx = hx, ex = nx + r.width, mx = (sx + ex) / 2;
        d = "M" + sx + " " + cy + " C" + mx + " " + cy + " " + mx + " " + ncy + " " + ex + " " + ncy;
      } else {
        var sx2 = hx + hw, ex2 = nx, mx2 = (sx2 + ex2) / 2;
        d = "M" + sx2 + " " + cy + " C" + mx2 + " " + cy + " " + mx2 + " " + ncy + " " + ex2 + " " + ncy;
      }
      var p = document.createElementNS(SVGNS, "path");
      p.setAttribute("d", d);
      p.setAttribute("stroke", colorOf(n));
      p.setAttribute("class", "vm-path");
      svg.appendChild(p);
      n._path = p;
      if (animate && !reduced) {
        var L = p.getTotalLength();
        p.style.strokeDasharray = L; p.style.strokeDashoffset = L;
        p.style.transition = "stroke-dashoffset 700ms ease " + (i * 45) + "ms";
        requestAnimationFrame(function () { requestAnimationFrame(function () { p.style.strokeDashoffset = "0"; }); });
        setTimeout(function () { p.style.strokeDasharray = ""; p.style.transition = ""; }, 800 + i * 45);
      }
    });
  }
  $$(".vm").forEach(function (vm) {
    var why = vm.parentNode.querySelector(".vm-why"), drawn = false, hub = $(".vm-hub", vm);
    function show(n, on) {
      if (n._path) n._path.classList.toggle("on", on);
      vm.classList.toggle("focusing", on);
      hub.classList.toggle("lit", on);
      why.textContent = on ? (n.textContent.trim() + ": " + (n.getAttribute("data-why") || "")) : "\u00a0";
    }
    $$(".vm-node", vm).forEach(function (n) {
      n.addEventListener("mouseenter", function () { show(n, true); });
      n.addEventListener("mouseleave", function () { show(n, false); });
      n.addEventListener("focus", function () { show(n, true); });
      n.addEventListener("blur", function () { show(n, false); });
    });
    function go() { if (!drawn) { drawn = true; drawMap(vm, true); } }
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { go(); io.disconnect(); } }); }, { threshold: 0.25 });
      io.observe(vm);
    } else go();
    var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(function () { if (drawn) drawMap(vm, false); }, 120); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (drawn) drawMap(vm, false); });
  });

  // ---------- feeling journey ----------
  var feelings = $$(".feel");
  if (feelings.length) {
    var out = $(".journey");
    getJSON("/data/map.json").then(function (M) {
      function vcard(id) {
        var v = M.verses[id] || ["", ""];
        return '<a class="jv" href="' + vurl(id) + '"><span class="vnum">' + id + '</span><span class="jsa" lang="sa">' + escH(v[1]) +
          '</span><span class="jen">' + escH(v[0]) + '</span><span class="jgo">Read, then practise</span></a>';
      }
      function schip(id) {
        var s = M.states[id];
        return '<a class="jstate st-' + (s[2] === "afflictive" ? "a" : "h") + '" href="/state/' + id + '/"><span lang="sa">' + escH(s[1]) + "</span> " + escH(s[0]) + "</a>";
      }
      function render(id) {
        var j = M.j[id], s = M.states[id];
        feelings.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-s") === id ? "true" : "false"); });
        var cols = [];
        if (j.kind === "afflictive") {
          cols.push('<div class="jcol"><h3><span class="jn">1</span> See how ' + escH(s[0].toLowerCase()) + " works</h3>" +
            (j.understand.length ? j.understand.map(vcard).join("") : '<p class="hint">No core verse names it directly yet.</p>') + "</div>");
          cols.push('<div class="jcol jmid"><h3><span class="jn">2</span> What answers it</h3>' + (j.cures.map(schip).join("") || '<p class="hint">No remedy linked yet.</p>') + "</div>");
          cols.push('<div class="jcol"><h3><span class="jn">3</span> Verses to practise</h3>' + j.practise.map(vcard).join("") + "</div>");
        } else {
          cols.push('<div class="jcol"><h3><span class="jn">1</span> Verses that cultivate ' + escH(s[0].toLowerCase()) + "</h3>" + j.practise.slice(0, 3).map(vcard).join("") + "</div>");
          cols.push('<div class="jcol jmid"><h3><span class="jn">2</span> It answers</h3>' + (j.cures.map(schip).join("") || '<p class="hint">It stands on its own.</p>') + "</div>");
          cols.push('<div class="jcol"><h3><span class="jn">3</span> Go deeper</h3>' + j.practise.slice(3).map(vcard).join("") +
            '<a class="btn ghost" href="/state/' + id + '/">Everything on ' + escH(s[0].toLowerCase()) + "</a></div>");
        }
        out.hidden = false;
        out.className = "journey " + (j.kind === "afflictive" ? "j-a" : "j-h");
        out.innerHTML = '<p class="jtitle"><span lang="sa">' + escH(s[1]) + "</span> " + escH(s[0]) + ": " + escH(s[3]) + '</p><div class="jflow">' + cols.join("") + "</div>";
        if (!reduced) { out.classList.remove("enter"); void out.offsetWidth; out.classList.add("enter"); }
        try { history.replaceState(null, "", "#feel-" + id); } catch (e) {}
      }
      feelings.forEach(function (b) {
        b.setAttribute("aria-pressed", "false");
        b.addEventListener("click", function () { render(b.getAttribute("data-s")); out.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "nearest" }); });
      });
      var m = location.hash.match(/^#feel-([a-z-]+)/);
      if (m && M.j[m[1]]) render(m[1]);
    });
  }

  // ---------- path finder: where you are -> where you want to be, as numbered steps ----------
  var pf = $(".pathform");
  if (pf) {
    getJSON("/data/graph.json").then(function (Gr) {
      var adj = {};
      Object.keys(Gr.nodes).forEach(function (k) { adj[k] = []; });
      Gr.edges.forEach(function (e) {
        var w = Gr.w[e[1]] || 1;
        if (!adj[e[0]] || !adj[e[2]]) return;
        // theme membership makes hops like "Theme 7 includes ..." that mean nothing to a reader
        if (Gr.nodes[e[0]].t === "theme" || Gr.nodes[e[2]].t === "theme") return;
        adj[e[0]].push({ to: e[2], e: e, fwd: true, w: w });
        adj[e[2]].push({ to: e[0], e: e, fwd: false, w: w });
      });
      function find(a, b) {
        var dist = {}, prev = {}, done = {}, q = [a];
        dist[a] = 0;
        while (q.length) {
          q.sort(function (x, y) { return dist[x] - dist[y]; });
          var u = q.shift();
          if (done[u]) continue;
          done[u] = true;
          if (u === b) break;
          adj[u].forEach(function (s) {
            var nd = dist[u] + s.w;
            if (dist[s.to] === undefined || nd < dist[s.to]) { dist[s.to] = nd; prev[s.to] = { from: u, step: s }; q.push(s.to); }
          });
        }
        if (dist[b] === undefined) return null;
        var path = [], cur = b;
        while (cur !== a) { path.unshift(prev[cur]); cur = prev[cur].from; }
        return path;
      }
      var KIND = { verse: "Verse", idea: "Idea", situation: "Situation" };
      function kindOf(n) { return n.t === "state" ? (n.v === "afflictive" ? "st-a" : "st-h") : n.t; }
      function kindLabel(n) { return n.t === "state" ? (n.v === "afflictive" ? "What troubles you" : "What it grows") : (KIND[n.t] || ""); }
      // verse numbers like (16.3) inside a note become links
      function noteHtml(t) {
        return escH(t).replace(/\(?(\d{1,2}\.\d{1,2})\)?/g, function (m, v) { var p = v.split("."); return '<a href="/' + p[0] + "/" + p[1] + '/">verse ' + v + "</a>"; });
      }
      function stop(k, i, how, note) {
        var n = Gr.nodes[k], body = n.t === "verse"
          ? '<a class="pf-card pf-verse" href="' + n.u + '"><span class="pf-vn">Verse ' + escH(n.l) + '</span><span class="pf-vd">' + escH(n.d || "") + "</span></a>"
          : '<a class="pf-card pf-' + kindOf(n) + '" href="' + n.u + '"><span class="pf-k">' + escH(kindLabel(n)) + '</span><span class="pf-l">' + escH(n.l) + "</span></a>";
        return '<li class="pf-stop"><span class="pf-num" aria-hidden="true">' + i + '</span><div class="pf-body">' +
          (how ? '<p class="pf-how">' + how + "</p>" : "") + body + (note ? '<p class="pf-why">' + noteHtml(note) + "</p>" : "") + "</div></li>";
      }
      var from = $(".pf-from"), to = $(".pf-to"), out = $(".pf-out"), pops = $$(".pf-pop [data-p]");
      function run() {
        var a = from.value, b = to.value;
        pops.forEach(function (x) { x.setAttribute("aria-pressed", x.getAttribute("data-p") === a + "|" + b ? "true" : "false"); });
        if (a === b) { out.innerHTML = '<li class="pf-msg">Pick two different points.</li>'; return; }
        var p = find(a, b);
        if (!p) { out.innerHTML = '<li class="pf-msg">No path yet between these two. Try another pair.</li>'; return; }
        var html = stop(a, 1, "", "");
        p.forEach(function (st, i) {
          var e = st.step.e, phr = Gr.rel[e[1]][st.step.fwd ? 0 : 1];
          var how = escH(Gr.nodes[st.from].l) + " <em>" + escH(phr) + "</em> " + escH(Gr.nodes[st.step.to].l);
          html += stop(st.step.to, i + 2, how, e[3]);
        });
        out.innerHTML = html;
        if (!reduced) { out.classList.remove("enter"); void out.offsetWidth; out.classList.add("enter"); }
      }
      from.addEventListener("change", run);
      to.addEventListener("change", run);
      pops.forEach(function (x) {
        x.addEventListener("click", function () { var v = x.getAttribute("data-p").split("|"); from.value = v[0]; to.value = v[1]; run(); });
      });
      run();
    });
  }
})();
