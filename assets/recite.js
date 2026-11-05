/* Sarathi recitation coach: listen, recite, score, check marks, spaced review.
   Needs score.js. Uses the browser's speech recogniser (Chrome, Edge) in
   Hindi mode, which writes Devanagari. ASCII only. */
(function () {
  "use strict";
  var S = window.SarathiScore;
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
  function addTry(vid, good, pct) {
    var rec = getRec(vid), d = today();
    rec.tries.push({ d: d, good: good, pct: pct });
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
    var words = JSON.parse(page.getAttribute("data-words"));
    var spans = $$(".pw", page);
    var micBtn = $(".mic", page), micLbl = $(".mic-label", page), live = $(".live", page), result = $(".result", page);
    var consentDlg = $(".consent"), SR = window.SpeechRecognition || window.webkitSpeechRecognition;

    function renderProgress() {
      var rec = getRec(vid), st = status(rec);
      var ticks = rec.tries.slice(-10).map(function (t) {
        return '<span class="tick ' + (t.good ? "ok" : "no") + '" title="' + dayLabel(t.d) + ": " + (t.good ? "Good" : "Needs work") + " (" + t.pct + '%)">' + (t.good ? CHECK : "\u00b7") + "</span>";
      }).join("");
      $(".progress", page).innerHTML = '<p class="st ' + st.cls + '">' + st.label + "</p><p class=\"st-text\">" + st.text + "</p>" +
        (ticks ? '<div class="ticks" aria-label="Recent takes">' + ticks + "</div>" : "");
    }
    renderProgress();

    if (!SR) {
      micBtn.disabled = true;
      micLbl.textContent = "Recording needs Chrome or Edge";
      live.textContent = "This browser has no speech recogniser. Open this page in Chrome or Edge on a computer or Android phone.";
      return;
    }

    var rec = null, listening = false, finals = [], lastAlts = [], silenceT = null, maxT = null;
    var media = null, chunks = [], takeUrl = null;

    function setState(on) {
      listening = on;
      micBtn.classList.toggle("on", on);
      micBtn.setAttribute("aria-pressed", on ? "true" : "false");
      micLbl.textContent = on ? "Listening. Tap to finish." : "Tap and recite";
    }
    function stopAll() {
      clearTimeout(silenceT); clearTimeout(maxT);
      try { rec && rec.stop(); } catch (e) {}
      try { if (media && media.state !== "inactive") media.stop(); } catch (e) {}
    }
    function startRecording(stream) {
      chunks = [];
      try {
        media = new MediaRecorder(stream);
        media.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
        media.onstop = function () {
          if (takeUrl) URL.revokeObjectURL(takeUrl);
          takeUrl = chunks.length ? URL.createObjectURL(new Blob(chunks, { type: media.mimeType || "audio/webm" })) : null;
          stream.getTracks().forEach(function (t) { t.stop(); });
          var b = $(".play-take", page); if (b) b.hidden = !takeUrl;
        };
        media.start();
      } catch (e) { media = null; stream.getTracks().forEach(function (t) { t.stop(); }); }
    }

    function begin() {
      result.hidden = true;
      spans.forEach(function (s) { s.className = "pw"; });
      finals = []; lastAlts = [];
      live.textContent = "";
      rec = new SR();
      rec.lang = "hi-IN";
      rec.continuous = true;
      rec.interimResults = true;
      rec.maxAlternatives = 5;
      rec.onresult = function (e) {
        var interim = "";
        for (var i = e.resultIndex; i < e.results.length; i++) {
          var r = e.results[i];
          if (r.isFinal) {
            finals.push(r[0].transcript);
            lastAlts = []; for (var a = 0; a < r.length; a++) lastAlts.push(r[a].transcript);
          } else interim += r[0].transcript;
        }
        live.textContent = (finals.join(" ") + " " + interim).trim();
        clearTimeout(silenceT);
        silenceT = setTimeout(stopAll, 3500);
      };
      rec.onerror = function (e) {
        var msg = { "not-allowed": "Microphone access is blocked. Allow the microphone for this site in the address bar, then try again.",
          "service-not-allowed": "Microphone access is blocked. Allow the microphone for this site in the address bar, then try again.",
          "no-speech": "Didn't hear anything. Move closer to the microphone and try again.",
          "network": "The speech service couldn't be reached. Check your connection and try again.",
          "audio-capture": "No microphone found. Plug one in or pick another in your system settings." }[e.error];
        if (msg) live.textContent = msg;
      };
      rec.onend = function () {
        setState(false);
        try { if (media && media.state !== "inactive") media.stop(); } catch (err) {}
        if (finals.length) finish(); else if (!live.textContent) live.textContent = "Didn't hear anything. Tap and try again.";
      };
      navigator.mediaDevices && navigator.mediaDevices.getUserMedia
        ? navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) { startRecording(stream); go(); }, function () { go(); })
        : go();
      function go() {
        try { rec.start(); setState(true); maxT = setTimeout(stopAll, 60000); }
        catch (e) { live.textContent = "Couldn't start listening. Reload the page and try again."; }
      }
    }

    function finish() {
      var joined = finals.join(" ");
      var options = [joined];
      if (finals.length === 1) options = lastAlts.length ? lastAlts : options;
      else lastAlts.slice(1).forEach(function (alt) { options.push(finals.slice(0, -1).join(" ") + " " + alt); });
      var r = S.score(words, options);
      var pct = Math.round(r.clearShare * 100);
      r.words.forEach(function (w, i) { if (spans[i]) spans[i].className = "pw " + w.mark; });
      var recd = addTry(vid, r.good, pct);
      var st = status(recd);
      var close = r.words.filter(function (w) { return w.mark === "close"; }).length, missed = r.missed;
      var detail = r.good
        ? (close ? close + " word" + (close === 1 ? " was" : "s were") + " close; say " + (close === 1 ? "it" : "them") + " more slowly next time." : "Every word came through clearly.")
        : missed ? missed + " word" + (missed === 1 ? " was" : "s were") + " missed or unclear. They are marked in the verse above." : "Some words were close but not clear. Try again a little more slowly.";
      result.hidden = false;
      result.className = "result " + (r.good ? "good" : "work");
      result.innerHTML = '<p class="verdict">' + (r.good ? '<span class="big-check" aria-hidden="true">' + CHECK + "</span> Good" : "Needs work") + "</p>" +
        '<p class="detail">' + escH(detail) + " " + pct + "% of words clear.</p>" +
        (r.good && st.label !== "Almost learned" && st.label !== "Practising" ? '<p class="detail strong">' + escH(st.label) + ". " + escH(st.text) + "</p>" : r.good ? '<p class="detail strong">' + escH(st.text) + "</p>" : "") +
        '<div class="v-actions"><button type="button" class="btn again">Try again</button><button type="button" class="btn ghost play-take"' + (takeUrl ? "" : " hidden") + ">Play your take</button></div>" +
        '<details class="heard"><summary>What the recogniser heard</summary><p lang="hi">' + escH(r.heard) + "</p></details>";
      $(".again", result).addEventListener("click", function () { micBtn.focus(); start(); });
      $(".play-take", result).addEventListener("click", function () { if (takeUrl) new Audio(takeUrl).play(); });
      renderProgress();
      result.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function start() {
      if (listening) { stopAll(); return; }
      if (!store.get("reciteConsent", false)) {
        if (consentDlg.showModal) consentDlg.showModal(); else consentDlg.setAttribute("open", "");
        return;
      }
      begin();
    }
    micBtn.addEventListener("click", start);
    $(".consent .ok", consentDlg).addEventListener("click", function () {
      store.set("reciteConsent", true);
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
      html += "<h2>" + (ids.length ? "More to learn" : "Start with these") + "</h2><ol class=\"vlist\">" + ess.filter(function (id) { return ids.indexOf(id) === -1; }).map(row).join("") + "</ol>";
      board.innerHTML = html;
    });
  }
})();
