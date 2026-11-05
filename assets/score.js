/* Sarathi recitation scorer. Compares what the recogniser heard (Devanagari)
   with the expected verse, letter by letter, and scores each expected word.
   ASCII only: every Devanagari character below is written as a \\u escape. */
(function (root) {
  "use strict";

  var VIRAMA = "\u094d", NUKTA = "\u093c", ANUSVARA = "\u0902", CANDRA = "\u0901", VISARGA = "\u0903";
  var NASALS = "\u0919\u091e\u0923\u0928\u092e";            // nga nya nna na ma
  // Independent vowels become their vowel signs, so a recogniser that splits
  // a word before a vowel is treated the same as one that joins it.
  var VOWEL_TO_SIGN = {
    "\u0906": "\u093e", "\u0907": "\u093f", "\u0908": "\u0940", "\u0909": "\u0941", "\u090a": "\u0942",
    "\u090b": "\u0943", "\u090f": "\u0947", "\u0910": "\u0948", "\u0913": "\u094b", "\u0914": "\u094c",
    "\u0905": ""   // a: inherent, carries no sign
  };
  // Pairs that sound close or that Hindi recognisers routinely swap: half cost.
  var GROUPS = [
    "\u093f\u0940",          // i / ii signs
    "\u0941\u0942",          // u / uu signs
    "\u0947\u0948",          // e / ai signs
    "\u094b\u094c",          // o / au signs
    "\u0923\u0928",          // nna / na
    "\u0936\u0937\u0938",    // sha / ssa / sa
    "\u0935\u092c",          // va / ba
    "\u0943\u093f",          // vocalic r / i sign
    "\u091c\u092f",          // ja / ya
    "\u0915\u0916", "\u0917\u0918", "\u091a\u091b", "\u091f\u0920", "\u0921\u0922",
    "\u0924\u0925", "\u0926\u0927", "\u092a\u092b", "\u092c\u092d"   // aspirated pairs
  ];
  var GROUP_OF = {};
  GROUPS.forEach(function (g, i) { g.split("").forEach(function (c) { GROUP_OF[c] = GROUP_OF[c] ? GROUP_OF[c] + "," + i : String(i); }); });
  // Marks a recogniser often drops or adds: cheap to insert or delete.
  var LIGHT = VIRAMA + "M" + VISARGA;

  function isDeva(c) { var n = c.charCodeAt(0); return n >= 0x0900 && n <= 0x097f; }
  function isConsonant(c) { var n = c.charCodeAt(0); return (n >= 0x0915 && n <= 0x0939) || (n >= 0x0958 && n <= 0x095f); }

  // Reduce Devanagari to a sound key: letters only, nasals before consonants
  // and anusvara merged into "M", nukta dropped, vowels as signs.
  function key(s) {
    s = (s || "").normalize("NFC").replace(/[\u0958-\u095f]/g, function (c) { return c.normalize("NFD").charAt(0); });
    var chars = [];
    for (var i = 0; i < s.length; i++) {
      var c = s.charAt(i);
      if (!isDeva(c) || c === NUKTA || c === "\u093d" || c === "\u0964" || c === "\u0965" || (c >= "\u0966" && c <= "\u096f")) continue;
      if (c === ANUSVARA || c === CANDRA) { chars.push("M"); continue; }
      if (VOWEL_TO_SIGN.hasOwnProperty(c)) { if (VOWEL_TO_SIGN[c]) chars.push(VOWEL_TO_SIGN[c]); continue; }
      // nasal + virama + consonant -> M
      if (NASALS.indexOf(c) !== -1 && s.charAt(i + 1) === VIRAMA && isConsonant(s.charAt(i + 2) || "")) { chars.push("M"); i++; continue; }
      chars.push(c);
    }
    return chars;
  }

  function sub(a, b) {
    if (a === b) return 0;
    var ga = GROUP_OF[a], gb = GROUP_OF[b];
    if (ga && gb && ga.split(",").some(function (g) { return gb.split(",").indexOf(g) !== -1; })) return 0.5;
    return 1;
  }
  function indel(c) { return LIGHT.indexOf(c) !== -1 ? 0.3 : 1; }

  // Weighted edit distance with a backtrace that charges every edit to an
  // expected letter, so each word knows what it lost.
  function align(exp, heard) {
    var n = exp.length, m = heard.length, D = [], B = [];
    for (var i = 0; i <= n; i++) { D.push(new Float64Array(m + 1)); B.push(new Uint8Array(m + 1)); }
    for (i = 1; i <= n; i++) { D[i][0] = D[i - 1][0] + indel(exp[i - 1]); B[i][0] = 1; }
    for (var j = 1; j <= m; j++) { D[0][j] = D[0][j - 1] + indel(heard[j - 1]); B[0][j] = 2; }
    for (i = 1; i <= n; i++) {
      for (j = 1; j <= m; j++) {
        var s = D[i - 1][j - 1] + sub(exp[i - 1], heard[j - 1]), d = D[i - 1][j] + indel(exp[i - 1]), ins = D[i][j - 1] + indel(heard[j - 1]);
        if (s <= d && s <= ins) { D[i][j] = s; B[i][j] = 0; } else if (d <= ins) { D[i][j] = d; B[i][j] = 1; } else { D[i][j] = ins; B[i][j] = 2; }
      }
    }
    var cost = new Float64Array(n);
    i = n; j = m;
    while (i > 0 || j > 0) {
      var b = B[i][j];
      if (i > 0 && j > 0 && b === 0) { cost[i - 1] += sub(exp[i - 1], heard[j - 1]); i--; j--; }
      else if (i > 0 && (j === 0 || b === 1)) { cost[i - 1] += indel(exp[i - 1]); i--; }
      else { cost[Math.min(Math.max(i - 1, 0), n - 1)] += indel(heard[j - 1]); j--; }
    }
    return { cost: cost, total: n ? D[n][m] : m };
  }

  var CLEAR = 0.75, CLOSE = 0.45, PASS_SHARE = 0.85;

  // words: the expected Devanagari words; heard: one or more transcripts.
  function score(words, heard) {
    var list = Array.isArray(heard) ? heard : [heard];
    var best = null;
    list.forEach(function (h) {
      var exp = [], owner = [];
      words.forEach(function (w, wi) { key(w).forEach(function (c) { exp.push(c); owner.push(wi); }); });
      var hk = key(h), a = align(exp, hk);
      var per = words.map(function () { return { len: 0, cost: 0 }; });
      owner.forEach(function (wi, k) { per[wi].len++; per[wi].cost += a.cost[k]; });
      var res = words.map(function (w, wi) {
        var p = per[wi], s = p.len ? Math.max(0, 1 - p.cost / p.len) : 1;
        return { word: w, score: Math.round(s * 100) / 100, mark: s >= CLEAR ? "clear" : s >= CLOSE ? "close" : "missed" };
      });
      var clear = res.filter(function (r) { return r.mark === "clear"; }).length;
      var overall = exp.length ? Math.max(0, 1 - a.total / Math.max(exp.length, hk.length)) : 0;
      var out = { words: res, clearShare: words.length ? clear / words.length : 0, overall: Math.round(overall * 100) / 100, heard: h };
      out.missed = res.filter(function (r) { return r.mark === "missed"; }).length;
      // A skipped or wrong word always fails: learning a shloka means every word.
      out.good = out.clearShare >= PASS_SHARE && out.missed === 0;
      if (!best || out.clearShare > best.clearShare || (out.clearShare === best.clearShare && out.overall > best.overall)) best = out;
    });
    return best;
  }

  var api = { key: key, align: align, score: score, thresholds: { CLEAR: CLEAR, CLOSE: CLOSE, PASS_SHARE: PASS_SHARE } };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.SarathiScore = api;
})(typeof window !== "undefined" ? window : this);
