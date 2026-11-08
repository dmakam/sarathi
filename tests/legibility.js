() => {
  const out = [];
  const vis = (el) => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none" && parseFloat(cs.opacity) > 0.05 && !el.closest('[hidden],.vh,.skip,.sr,[aria-hidden="true"]'); };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const t = walker.currentNode, txt = t.nodeValue.trim(); if (!txt || txt.length < 2) continue;
    const el = t.parentElement; if (!el || seen.has(el) || !vis(el) || el.matches(".sky-hit")) continue; seen.add(el);
    const fs = parseFloat(getComputedStyle(el).fontSize), words = el.textContent.trim().split(/\s+/).length;
    const reading = words >= 6 && getComputedStyle(el).textTransform !== "uppercase";
    const min = reading ? 16 : 13;
    if (fs < min - 0.01) out.push({ kind: reading ? "reading<16" : "text<13", fs, sel: el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : ""), txt: txt.slice(0, 40) });
  }
  document.querySelectorAll("a,button,select,input,[role=tab]").forEach((el) => {
    if (!vis(el) || el.matches(".bar,.sky-hit")) return;
    const cs = getComputedStyle(el); if (cs.display === "inline" && el.closest("p,li,span.vt-why")) return;
    const r = el.getBoundingClientRect();
    if (r.height < 43.5 || r.width < 43.5) out.push({ kind: "tap<44", fs: Math.round(r.width) + "x" + Math.round(r.height), sel: el.tagName.toLowerCase() + (typeof el.className === "string" && el.className ? "." + el.className.split(" ")[0] : ""), txt: (el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 30) });
  });
  return out;
}
