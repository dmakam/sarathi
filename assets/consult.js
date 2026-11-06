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

  /* Full-card scenes for who is asking. Flat illustration, 160x190, ground at y=150. */
  var SCENE = {
    student: '<rect width="160" height="190" fill="#26346B"/>' +
      '<rect x="88" y="16" width="58" height="50" rx="3" fill="#141C44"/><path d="M117 16v50M88 41h58" stroke="#26346B" stroke-width="2.5"/>' +
      '<circle cx="131" cy="31" r="8" fill="#F4E6B8"/><circle cx="134.5" cy="28.5" r="7" fill="#141C44"/>' +
      '<circle class="tw" cx="98" cy="25" r="1.1" fill="#fff"/><circle class="tw t2" cx="108" cy="55" r="1" fill="#fff"/><circle class="tw t3" cx="140" cy="57" r="1" fill="#fff"/>' +
      '<path class="glow" d="M33 66 8 116h58z" fill="#F6D77A" opacity=".22"/>' +
      '<path d="M22 112V84l12-18" stroke="#C9A227" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M27 62l15-4 2 10z" fill="#C9A227"/><rect x="14" y="110" width="18" height="4" rx="2" fill="#C9A227"/>' +
      '<circle cx="92" cy="74" r="9.5" fill="#3A2A22"/><path d="M75 116c0-19 7-28 17-28s17 9 17 28z" fill="#E8A65A"/>' +
      '<path d="M84 99c-6 5-12 9-17 11" stroke="#E8A65A" stroke-width="6" stroke-linecap="round" fill="none"/>' +
      '<rect x="116" y="100" width="24" height="5" rx="1" fill="#D07FA8"/><rect x="118" y="95" width="21" height="5" rx="1" fill="#7FC4BA"/><rect x="115" y="90" width="23" height="5" rx="1" fill="#E9D58A"/>' +
      '<path d="M50 112l14-4 14 4v3l-14-3-14 3z" fill="#F4F7F6"/>' +
      '<rect x="6" y="114" width="148" height="7" rx="2" fill="#6B4A2E"/><rect x="14" y="121" width="5" height="30" fill="#55391F"/><rect x="141" y="121" width="5" height="30" fill="#55391F"/>' +
      '<rect y="150" width="160" height="40" fill="#18224A"/>',
    work: '<rect width="160" height="190" fill="#2F6F73"/>' +
      '<rect x="12" y="16" width="74" height="56" rx="3" fill="#A9D8D3"/>' +
      '<path d="M12 72V52h10v-8h9v14h8V40h12v18h7V48h11v24z" fill="#5E9E9C"/><path d="M12 72v-8h16v-6h12v14z" fill="#4A8785"/>' +
      '<path class="cloud" d="M28 30a6 6 0 0 1 11-2 5 5 0 0 1 7 5H24a4 4 0 0 1 4-3z" fill="#fff" opacity=".85"/>' +
      '<rect x="12" y="16" width="74" height="56" rx="3" fill="none" stroke="#24585B" stroke-width="3"/>' +
      '<circle cx="82" cy="70" r="9.5" fill="#2A1E18"/><path d="M63 118c0-21 8-30 19-30s19 9 19 30z" fill="#F4F7F6"/>' +
      '<rect x="60" y="89" width="44" height="28" rx="2.5" fill="#12262A"/><rect x="63" y="92" width="38" height="22" rx="1" fill="#1F4A50"/><path d="M66 98h22M66 103h28M66 108h16" stroke="#7FC4BA" stroke-width="1.6" stroke-linecap="round"/>' +
      '<path d="M54 117h56l-4 4H58z" fill="#9DB6B3"/>' +
      '<rect x="126" y="98" width="16" height="20" rx="2" fill="#C9A227"/><ellipse cx="128" cy="90" rx="5" ry="10" transform="rotate(-25 128 90)" fill="#4C9A6A"/><ellipse cx="140" cy="88" rx="5" ry="11" transform="rotate(20 140 88)" fill="#3F8A5C"/><ellipse cx="134" cy="84" rx="4.5" ry="12" fill="#57A877"/>' +
      '<rect x="24" y="106" width="12" height="12" rx="2" fill="#E9D58A"/><path d="M36 109a3 3 0 0 1 0 6" stroke="#E9D58A" stroke-width="2" fill="none"/>' +
      '<path class="steam" d="M28 102c-2-3 2-5 0-8M32 102c-2-3 2-5 0-8" stroke="#fff" stroke-width="1.4" fill="none" stroke-linecap="round" opacity=".7"/>' +
      '<rect x="6" y="118" width="148" height="7" rx="2" fill="#E9D58A"/><rect x="14" y="125" width="5" height="26" fill="#B89A3E"/><rect x="141" y="125" width="5" height="26" fill="#B89A3E"/>' +
      '<rect y="150" width="160" height="40" fill="#1F5458"/>',
    family: '<rect width="160" height="190" fill="#9E4F3A"/>' +
      '<rect x="102" y="20" width="44" height="50" rx="22" fill="#C97A5C"/><rect x="102" y="20" width="44" height="50" rx="22" fill="none" stroke="#7E3B2B" stroke-width="3"/>' +
      '<path d="M60 0v20" stroke="#5A2E28" stroke-width="2"/><path d="M48 32l12-12 12 12z" fill="#E9D58A"/><path class="glow" d="M48 32h24l18 52H30z" fill="#F6D77A" opacity=".16"/>' +
      '<path d="M10 104q0-8 8-8h124q8 0 8 8v40H10z" fill="#5A2E28"/><rect x="6" y="110" width="16" height="36" rx="6" fill="#4A2520"/><rect x="138" y="110" width="16" height="36" rx="6" fill="#4A2520"/>' +
      '<circle cx="48" cy="72" r="9.5" fill="#3A2A22"/><path d="M32 124c0-22 7-33 16-33s16 11 16 33z" fill="#E9D58A"/>' +
      '<circle cx="108" cy="70" r="10" fill="#2A1E18"/><path d="M91 124c0-23 7-34 17-34s17 11 17 34z" fill="#24306E"/>' +
      '<circle cx="78" cy="92" r="7.5" fill="#3A2A22"/><path d="M66 126c0-15 5-22 12-22s12 7 12 22z" fill="#F07E5A"/>' +
      '<path d="M60 104l10 6M96 102l-10 7" stroke="#E9D58A" stroke-width="5" stroke-linecap="round"/>' +
      '<rect x="10" y="124" width="140" height="18" rx="4" fill="#6E3427"/>' +
      '<rect y="150" width="160" height="40" fill="#6E3427"/><ellipse cx="80" cy="162" rx="58" ry="8" fill="#8A4532"/>',
    love: '<defs><linearGradient id="cx-dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B4A8E"/><stop offset=".6" stop-color="#D98A8A"/><stop offset="1" stop-color="#F4B98A"/></linearGradient></defs>' +
      '<rect width="160" height="190" fill="url(#cx-dusk)"/>' +
      '<circle cx="104" cy="122" r="24" fill="#FFD9A0"/>' +
      '<path d="M0 126q40-14 80-4t80-6v40H0z" fill="#7A5A8E"/>' +
      '<rect x="18" y="74" width="7" height="60" fill="#3B2F55"/><circle cx="22" cy="60" r="22" fill="#4A3B6B"/><circle cx="36" cy="72" r="14" fill="#4A3B6B"/>' +
      '<path class="float" d="M80 44c-3-5-11-4-11 2 0 5 6 9 11 12 5-3 11-7 11-12 0-6-8-7-11-2z" fill="#FF8A98"/>' +
      '<circle cx="68" cy="88" r="8.5" fill="#2A1E2A"/><path d="M54 126c0-19 6-29 14-29s14 10 14 29z" fill="#E9D58A"/>' +
      '<circle cx="93" cy="86" r="9" fill="#1E1620"/><path d="M78 126c0-20 6-30 15-30s15 10 15 30z" fill="#24306E"/>' +
      '<path d="M76 106l6 4 6-4" stroke="#E9D58A" stroke-width="4.5" stroke-linecap="round" fill="none"/>' +
      '<rect x="40" y="124" width="82" height="6" rx="2" fill="#3A2E3A"/><rect x="46" y="130" width="4" height="20" fill="#3A2E3A"/><rect x="112" y="130" width="4" height="20" fill="#3A2E3A"/>' +
      '<rect y="150" width="160" height="40" fill="#3B2F55"/>',
    me: '<defs><linearGradient id="cx-dawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6E9C4"/><stop offset="1" stop-color="#EDB97E"/></linearGradient></defs>' +
      '<rect width="160" height="190" fill="url(#cx-dawn)"/>' +
      '<g class="sun"><circle cx="80" cy="96" r="44" fill="#FFE2A0" opacity=".55"/><circle cx="80" cy="96" r="30" fill="#FFD27A"/></g>' +
      '<path class="bird" d="M30 40q4-4 8 0q4-4 8 0M118 30q3-3 6 0q3-3 6 0" stroke="#7A5A3A" stroke-width="1.4" fill="none" stroke-linecap="round"/>' +
      '<path d="M0 132q40-20 80-14t80 6v66H0z" fill="#8FB09A"/>' +
      '<path d="M0 128q80-28 160 0v62H0z" fill="#4F7F6E"/>' +
      '<circle cx="80" cy="80" r="8" fill="#1E3A3A"/><path d="M69 112c0-15 5-23 11-23s11 8 11 23z" fill="#1E3A3A"/>' +
      '<ellipse cx="80" cy="114" rx="20" ry="6" fill="#1E3A3A"/><path d="M71 99c-4 5-8 9-12 13M89 99c4 5 8 9 12 13" stroke="#1E3A3A" stroke-width="4.5" stroke-linecap="round"/>' +
      '<rect y="150" width="160" height="40" fill="#4F7F6E"/>'
  };
  function scene(id) { return '<svg class="cx-art" viewBox="0 0 160 190" preserveAspectRatio="' + (id === "me" ? "xMidYMid slice" : "xMidYMax slice") + '" aria-hidden="true">' + (SCENE[id] || "") + "</svg>"; }

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
      t += '<button type="button" class="cx-tile art a-' + a[0] + '" style="--i:' + i + '" data-act="aud" data-id="' + a[0] + '">' + scene(a[0]) + "<span>" + esc(a[1]) + "</span></button>";
    });
    return '<p class="cx-kicker">Ask S&#257;rathi</p><h1 class="cx-h">What&rsquo;s on your mind?</h1>' +
      '<p class="cx-q">Who&rsquo;s asking?</p><div class="cx-tiles five">' + t + "</div>" + writeBox("Or tell me in your own words\u2026") + helpLink();
  }
  function vFeel() {
    var t = "";
    D.feel.forEach(function (f, i) {
      t += feelTile(f, i, "");
    });
    return '<p class="cx-kicker">' + esc(byId(D.aud, S.aud)[1]) + '</p><h1 class="cx-h">How does it feel?</h1><div class="cx-tiles six">' + t + "</div>" + helpLink();
  }
  function feelTile(f, i, extra) {
    var hint = (D.hints[S.aud || "me"] || {})[f[0]] || "";
    return '<button type="button" class="cx-tile feel f-' + f[0] + extra + '" style="--i:' + i + '" data-act="feel" data-id="' + f[0] + '">' + face(f[0]) +
      '<span class="ft"><b>' + esc(f[1]) + "</b>" + (hint ? "<small>" + esc(hint) + "</small>" : "") + "</span></button>";
  }
  function forTopic(aud, feel) {
    return D.sit.filter(function (s) { return s.a.indexOf(aud) >= 0 && s.f.indexOf(feel) >= 0; })
      .map(function (s, k) { return { s: s, key: s.f.indexOf(feel) + (s.a[0] === aud ? 0 : 0.5) + k / 1000 }; })
      .sort(function (x, y) { return x.key - y.key; }).map(function (x) { return x.s; }).slice(0, 4);
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
      list = forTopic(S.aud, S.feel);
      head = "Is it one of these?";
    }
    var h = "";
    list.forEach(function (s, i) { h += sitCard(s, i); });
    if (S.matches && !list.length) {
      D.feel.forEach(function (f, i) { h += feelTile(f, i, " slim"); });
      return '<h1 class="cx-h">' + head + "</h1>" + sub + '<div class="cx-tiles six">' + h + "</div>" + writeBox("Try saying it another way\u2026") + helpLink();
    }
    var kick = (!S.matches && S.aud && S.feel) ? '<p class="cx-kicker">' + esc(byId(D.aud, S.aud)[1]) + " &middot; " + esc(byId(D.feel, S.feel)[1]) + "</p>" : "";
    return kick + '<h1 class="cx-h">' + head + '</h1><div class="cx-sits">' + h +
      '<details class="cx-else" style="--i:' + list.length + '"><summary>Something else</summary>' + writeBox("Tell me what happened\u2026") + "</details></div>" + helpLink();
  }
  function vAnswer() {
    var s = byId(D.sit, S.sit), pair = s.v[S.vi], vid = pair[0], v = D.v[vid];
    var saved = store.get("saved", []), isSaved = saved.some(function (x) { return x.id === s.id && x.v === vid; });
    var fb = store.get("fb", {})[s.id + "@" + vid];
    var lines = v.sa.map(function (l, i) { return '<span style="--i:' + i + '">' + esc(l) + "</span>"; }).join("");
    var c = vid.split(".");
    return '<article class="cx-card"><div class="cx-l">' +
      '<p class="cx-for">' + esc(s.t) + "</p>" +
      '<blockquote class="cx-en">\u201c' + esc(v.en) + "\u201d</blockquote>" +
      '<p class="cx-ref"><a href="' + v.url + '">Bhagavad Gita ' + c[0] + "." + c[1] + "</a> &middot; Swami Sivananda</p>" +
      '<details class="cx-sk"><summary>Show the Sanskrit</summary><p class="cx-sa" lang="sa">' + lines + "</p>" +
      '<p class="cx-tl" lang="sa-Latn"><span class="tl-k">Say it</span>' + (v.tl || []).map(esc).join("<br>") + "</p></details></div>" + '<div class="cx-r">' +
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
      "</div></article>" +
      '<nav class="cx-deeper" aria-label="Go deeper"><a href="' + v.pr + '">Learn to recite it</a><a href="' + v.url + '">Read the full verse</a><a href="' + v.url + '#h-map">See what it connects to</a><button type="button" class="cx-link" data-act="restart">Ask about something else</button></nav>';
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
      if (s.a.some(function (a) { return auds[a] || a === S.aud; })) sc += 1;
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

  window.addEventListener("hashchange", function () {
    if (!D) return;
    var mm = (location.hash || "").slice(1).match(/^(.+?)(?:-(\d))?$/);
    if (mm && byId(D.sit, mm[1]) && !(S.step === "answer" && S.sit === mm[1])) { S.sit = mm[1]; S.vi = mm[2] ? (+mm[2] - 1) : 0; go("answer"); }
  });
  fetch(root.getAttribute("data-src")).then(function (r) { return r.json(); }).then(function (d) {
    D = d;
    var qs = (location.search.match(/[?&]q=([^&]*)/) || [])[1];
    var ah = (location.hash.match(/^#a-([a-z]+)$/) || [])[1];
    if (qs) {
      try { history.replaceState(null, "", location.pathname); } catch (e) {}
      S.text = decodeURIComponent(qs.replace(/\+/g, " ")).slice(0, 400);
      var m0 = match(S.text);
      S.hist = [{ step: "who" }];
      if (m0.help) { S.help = m0.help; S.step = "help"; } else { S.matches = m0.list; S.step = "pick"; }
      render("same"); return;
    }
    if (ah && byId(D.aud, ah)) { S.aud = ah; S.step = "feel"; S.hist = [{ step: "who" }]; render("same"); return; }
    var h = (location.hash || "").slice(1), mm = h.match(/^(.+?)(?:-(\d))?$/);
    if (mm && byId(D.sit, mm[1])) { S.sit = mm[1]; S.vi = mm[2] ? (+mm[2] - 1) : 0; S.step = "answer"; S.hist = [{ step: "who" }]; }
    render("same");
  }).catch(function () {
    stage.innerHTML = '<div class="cx-step is-on"><h1 class="cx-h">S&#257;rathi couldn&rsquo;t load.</h1><p class="cx-q">Check your connection and reload the page.</p></div>';
  });
})();
