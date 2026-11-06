/* Sarathi recitation coach: listen, recite, score, check marks, spaced review.
   Records the take in the browser and sends it to the Sarathi coach, which
   force-aligns it against the known verse and marks each word. ASCII only. */
(function () {
  "use strict";
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function escH(s) { return String(s || "").replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("sarathi." + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("sarathi." + k, JSON.stringify(v)); } catch (e) {} }
  };
  function today() { var d = new Date(); return Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000); }
  function dayLabel(n) { var d = new Date(n * 86400000); return d.toLocaleDateString(undefined, { month: "short", day: "numeric", timeZone: "UTC" }); }
  function vurl(id) { var p = id.split("."); return "/" + p[0] + "/" + p[1] + "/"; }
  var CHECK = "\u2713";
  var REVIEWS = [1, 3, 7, 21];

  // ---------- progress model ----------
  // record = {tries:[{d, good, pct}], learned: day|null, stage: 0..4}
  function getRec(vid) { var all = store.get("recite", {}); return all[vid] || { tries: [], learned: null, stage: 0 }; }
  function saveRec(vid, rec) { var all = store.get("recite", {}); all[vid] = rec; store.set("recite", all); }
  function goodDays(rec) { var s = {}; rec.tries.forEach(function (t) { if (t.good) s[t.d] = 1; }); return Object.keys(s).map(Number).sort(function (a, b) { return a - b; }); }
  function nextDue(rec) { return rec.learned == null || rec.stage >= REVIEWS.length ? null : rec.learned + REVIEWS[rec.stage]; }
  function addTry(vid, good, pct, self) {
    var rec = getRec(vid), d = today();
    rec.tries.push(self ? { d: d, good: good, pct: null, self: 1 } : { d: d, good: good, pct: pct });
    if (rec.tries.length > 40) rec.tries = rec.tries.slice(-40);
    if (good) {
      var days = goodDays(rec);
      if (rec.learned == null && days.length >= 2) { rec.learned = d; rec.stage = 0; }
      else if (rec.learned != null) { var due = nextDue(rec); if (due != null && d >= due) rec.stage++; }
    }
    saveRec(vid, rec);
    return rec;
  }
  function status(rec) {
    var due = nextDue(rec);
    if (rec.learned != null && rec.stage >= REVIEWS.length) return { label: "Mastered", cls: "mastered", text: "All four reviews passed." };
    if (rec.learned != null) return due <= today() ? { label: "Review due", cls: "due", text: "A review is due today." } : { label: "Learned", cls: "learned", text: "Next review " + dayLabel(due) + "." };
    var gd = goodDays(rec).length;
    if (gd === 1) return { label: "Almost learned", cls: "half", text: "One more Good on another day marks it learned." };
    if (rec.tries.length) return { label: "Practising", cls: "trying", text: "Two Goods on different days mark it learned." };
    return { label: "Not started", cls: "new", text: "Two Goods on different days mark it learned." };
  }
  window.SarathiRecite = { getRec: getRec, status: status, nextDue: nextDue, today: today };

  // ---------- practice page ----------
  var page = $(".practice");
  if (page) initPractice(page);

  function initPractice(page) {
    var vid = page.getAttribute("data-vid");
    var api = page.getAttribute("data-api") || "/api/score";
    var spans = $$(".pw", page);
    var micBtn = $(".mic", page), micLbl = $(".mic-label", page), live = $(".live", page), result = $(".result", page);
    var consentDlg = $(".consent");

    function renderProgress() {
      var rec = getRec(vid), st = status(rec);
      var ticks = rec.tries.slice(-10).map(function (t) {
        return '<span class="tick ' + (t.good ? "ok" : "no") + '" title="' + dayLabel(t.d) + ": " + (t.self ? "You marked it recited" : (t.good ? "Good" : "Needs work") + " (" + t.pct + "%)") + '">' + (t.good ? CHECK : "\u00b7") + "</span>";
      }).join("");
      $(".progress", page).innerHTML = '<p class="st ' + st.cls + '">' + st.label + "</p><p class=\"st-text\">" + st.text + "</p>" +
        (ticks ? '<div class="ticks" aria-label="Recent takes">' + ticks + "</div>" : "") +
        '<p class="self-mark"><button type="button" class="btn ghost sm self">I recited it from memory</button>' +
        '<span class="hint">No microphone needed. Use this when you practise aloud elsewhere, or can&rsquo;t record.</span></p>';
      var sb = $(".self", page);
      var doneToday = rec.tries.some(function (t) { return t.self && t.d === today(); });
      if (doneToday) { sb.disabled = true; sb.textContent = "Marked for today"; }
      sb.addEventListener("click", function () { addTry(vid, true, null, true); renderProgress(); var live2 = $(".live", page); if (live2) live2.textContent = "Marked as recited today."; });
    }
    renderProgress();

    if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder)) {
      micBtn.disabled = true;
      micLbl.textContent = "Recording isn't available in this browser";
      live.textContent = "Open this page in a current version of Chrome, Edge, Safari or Firefox.";
      return;
    }

    var stream = null, media = null, chunks = [], ctx = null, raf = 0, maxT = null, state = "idle";
    var takeUrl = null, takeAudio = null, lastWords = [];

    function setState(s, label) {
      state = s;
      micBtn.classList.toggle("on", s === "recording");
      micBtn.classList.toggle("busy", s === "checking");
      micBtn.disabled = s === "checking";
      micBtn.setAttribute("aria-pressed", s === "recording" ? "true" : "false");
      micLbl.textContent = label || (s === "recording" ? "Listening. Tap when you finish." : s === "checking" ? "Checking your recitation..." : "Tap and recite");
    }
    function cleanup() {
      cancelAnimationFrame(raf); clearTimeout(maxT);
      if (ctx) { try { ctx.close(); } catch (e) {} ctx = null; }
      if (stream) { stream.getTracks().forEach(function (t) { t.stop(); }); stream = null; }
    }
    function stop() { if (media && media.state === "recording") media.stop(); }

    // Stop by itself: once voice has been heard, 2.5 s of quiet ends the take.
    function watchSilence() {
      try {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
        var src = ctx.createMediaStreamSource(stream), an = ctx.createAnalyser();
        an.fftSize = 2048; src.connect(an);
        var buf = new Float32Array(an.fftSize), heard = false, quietSince = 0, floor = 0.01;
        (function tick() {
          an.getFloatTimeDomainData(buf);
          var sum = 0; for (var i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
          var rms = Math.sqrt(sum / buf.length), now = performance.now();
          if (rms > floor * 3) { heard = true; quietSince = 0; live.textContent = "Hearing you..."; }
          else if (heard) { if (!quietSince) quietSince = now; else if (now - quietSince > 2500) { stop(); return; } }
          raf = requestAnimationFrame(tick);
        })();
      } catch (e) {}
    }

    function begin() {
      result.hidden = true;
      spans.forEach(function (s) { s.className = "pw"; });
      live.textContent = "";
      navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } }).then(function (s) {
        stream = s; chunks = [];
        media = new MediaRecorder(stream);
        media.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
        media.onstop = function () { cleanup(); upload(new Blob(chunks, { type: media.mimeType || "audio/webm" })); };
        media.start();
        setState("recording");
        watchSilence();
        maxT = setTimeout(stop, 70000);
      }, function (err) {
        setState("idle");
        live.textContent = err && err.name === "NotFoundError" ? "No microphone found. Plug one in or pick another in your system settings."
          : "Microphone access is blocked. Allow the microphone for this site in the address bar, then try again.";
      });
    }

    function upload(blob) {
      if (takeUrl) URL.revokeObjectURL(takeUrl);
      takeUrl = URL.createObjectURL(blob);
      takeAudio = new Audio(takeUrl);
      if (blob.size < 2000) { setState("idle"); live.textContent = "Didn't hear anything. Tap and try again."; return; }
      setState("checking");
      live.textContent = "";
      fetch(api + "?v=" + encodeURIComponent(vid), { method: "POST", body: blob, headers: { "Content-Type": blob.type || "application/octet-stream" } })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          setState("idle");
          if (!res.ok) { live.textContent = res.j.message || "The coach couldn't score that take. Try again."; return; }
          show(res.j);
        })
        .catch(function () { setState("idle"); live.textContent = "Couldn't reach the coach. Check your connection and try again."; });
    }

    function playSpan(a, b) {
      if (!takeAudio || a == null) return;
      takeAudio.pause(); takeAudio.currentTime = Math.max(0, a - 0.15); takeAudio.play();
      var stopAt = (b || a) + 0.2;
      var h = function () { if (takeAudio.currentTime >= stopAt) { takeAudio.pause(); takeAudio.removeEventListener("timeupdate", h); } };
      takeAudio.addEventListener("timeupdate", h);
    }

    function show(r) {
      lastWords = r.words;
      var pct = Math.round(r.clearShare * 100);
      r.words.forEach(function (w, i) {
        var sp = spans[i]; if (!sp) return;
        sp.className = "pw " + w.mark + (w.start != null ? " tap" : "");
        sp.title = w.mark === "clear" ? "Clear. Tap to hear your take." : w.mark === "close" ? "Close. Tap to hear your take." : "Missed or unclear.";
      });
      var recd = addTry(vid, r.good, pct), st = status(recd);
      var close = r.words.filter(function (w) { return w.mark === "close"; }).length;
      var detail = r.good
        ? (close ? close + " word" + (close === 1 ? " was" : "s were") + " close. Say " + (close === 1 ? "it" : "them") + " a little more clearly next time." : "Every word came through clearly.")
        : r.missed ? r.missed + " word" + (r.missed === 1 ? " was" : "s were") + " missed or unclear. They are marked in red in the verse above."
        : "Some words were close but not clear. Try again a little more slowly.";
      result.hidden = false;
      result.className = "result " + (r.good ? "good" : "work");
      result.innerHTML = '<p class="verdict">' + (r.good ? '<span class="big-check" aria-hidden="true">' + CHECK + "</span> Good" : "Needs work") + "</p>" +
        '<p class="detail">' + escH(detail) + " " + pct + "% of words clear. Tap any word in the verse to hear how you said it.</p>" +
        (r.good ? '<p class="detail strong">' + escH(st.label === "Almost learned" ? st.text : st.label + ". " + st.text) + "</p>" : "") +
        '<div class="v-actions"><button type="button" class="btn again">Try again</button><button type="button" class="btn ghost play-take">Play your take</button></div>';
      $(".again", result).addEventListener("click", function () { start(); });
      $(".play-take", result).addEventListener("click", function () { if (takeAudio) { takeAudio.currentTime = 0; takeAudio.play(); } });
      renderProgress();
      result.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    spans.forEach(function (sp, i) {
      sp.addEventListener("click", function () { var w = lastWords[i]; if (w) playSpan(w.start, w.end); });
    });

    function start() {
      if (state === "recording") { stop(); return; }
      if (state === "checking") return;
      if (!store.get("reciteConsent2", false)) { if (consentDlg.showModal) consentDlg.showModal(); else consentDlg.setAttribute("open", ""); return; }
      begin();
    }
    micBtn.addEventListener("click", start);
    $(".consent .ok", consentDlg).addEventListener("click", function () {
      store.set("reciteConsent2", true);
      consentDlg.close ? consentDlg.close() : consentDlg.removeAttribute("open");
      begin();
    });
    $(".consent .cancel", consentDlg).addEventListener("click", function () { consentDlg.close ? consentDlg.close() : consentDlg.removeAttribute("open"); });
  }

  // ---------- practice index ----------
  var board = $(".practice-board");
  if (board) {
    var all = store.get("recite", {}), ids = Object.keys(all);
    var ess = JSON.parse(board.getAttribute("data-essentials"));
    var themes = JSON.parse(board.getAttribute("data-themes") || "[]");
    fetch("/data/search.json").then(function (r) { return r.json(); }).then(function (rows) {
      var sa = {}; rows.forEach(function (r) { sa[r[0]] = r[5]; });
      function row(id) {
        var st = status(getRec(id));
        return '<li class="vrow"><a href="/practice' + vurl(id) + '"><span class="vnum">' + id + '</span><span class="vsa" lang="sa">' + escH(sa[id] || "") +
          '</span><span class="ven"><span class="pill ' + st.cls + '">' + st.label + "</span> " + escH(st.text) + "</span></a></li>";
      }
      var due = ids.filter(function (id) { var d = nextDue(all[id]); return d != null && d <= today(); });
      var going = ids.filter(function (id) { return due.indexOf(id) === -1; });
      var html = "";
      if (due.length) html += "<h2>Due for review</h2><ol class=\"vlist\">" + due.map(row).join("") + "</ol>";
      if (going.length) html += "<h2>Your verses</h2><ol class=\"vlist\">" + going.map(row).join("") + "</ol>";
      themes.forEach(function (t, i) {
        var left = t[1].filter(function (id) { return ids.indexOf(id) === -1; });
        if (!left.length) return;
        html += "<h2>Theme " + (i + 1) + ": " + escH(t[0]) + "</h2><ol class=\"vlist\">" + left.map(row).join("") + "</ol>";
      });
      board.innerHTML = html;
    });
  }
})();
