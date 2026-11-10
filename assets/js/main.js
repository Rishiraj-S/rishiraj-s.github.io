// Menu behaviour: hash tabs, Q/E to switch tabs, arrow keys move focus between tiles, Esc goes back.
// Without JS every panel simply renders stacked, so nothing depends on this file.
document.documentElement.classList.add("js");

const tabs = [...document.querySelectorAll(".tabs a")];
const panels = [...document.querySelectorAll(".panel")];
const backLink = document.querySelector("[data-back]");
// Items that stagger in when their tab opens (the menu-load effect)
const CASCADE = ".tile, .about, .history > li, .academy > li, .certs > li, .gallery > li, .contact-lines > div, .form > label, .form > .btn";

function show(id) {
  const panel = panels.find(p => p.id === id) || panels[0];
  if (!panel) return;
  panels.forEach(p => p.classList.toggle("is-active", p === panel));
  tabs.forEach(t => t.hash === "#" + panel.id ? t.setAttribute("aria-current", "page") : t.removeAttribute("aria-current"));
  panel.querySelectorAll(CASCADE).forEach((el, i) => { el.classList.add("cascade"); el.style.setProperty("--i", i); });
  window.scrollTo(0, 0);
}

function stepTab(dir) {
  const i = tabs.findIndex(t => t.getAttribute("aria-current") === "page");
  location.hash = tabs[(i + dir + tabs.length) % tabs.length].hash;
}

// ponytail: nearest-tile-in-direction by centre distance; fine for a dozen tiles.
function moveFocus(key) {
  const panel = document.querySelector(".panel.is-active");
  if (!panel) return false;
  const tiles = [...panel.querySelectorAll(".tile:not([hidden])")];
  const from = tiles.includes(document.activeElement) ? document.activeElement : null;
  if (!from) { tiles[0]?.focus(); return !!tiles[0]; }
  const a = from.getBoundingClientRect();
  const [dx, dy] = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[key];
  let best = null, bestScore = Infinity;
  for (const t of tiles) {
    if (t === from) continue;
    const b = t.getBoundingClientRect();
    const ox = (b.left + b.width / 2) - (a.left + a.width / 2);
    const oy = (b.top + b.height / 2) - (a.top + a.height / 2);
    const along = ox * dx + oy * dy;
    if (along <= 1) continue;
    const score = along + Math.abs(ox * dy + oy * dx) * 2;
    if (score < bestScore) { best = t; bestScore = score; }
  }
  best?.focus();
  return true;
}

document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || e.target.closest("input, textarea, select")) return;
  if (e.key === "Escape" && backLink) { location.href = backLink.href; return; }
  if (!panels.length) return;
  if (e.key === "q" || e.key === "Q") stepTab(-1);
  else if (e.key === "e" || e.key === "E") stepTab(1);
  else if (e.key === "Escape") location.hash = tabs[0].hash;
  else if (e.key.startsWith("Arrow") && moveFocus(e.key)) e.preventDefault();
});

if (panels.length) {
  window.addEventListener("hashchange", () => show(location.hash.slice(1)));
  show(location.hash.slice(1));
}

// Project filters
document.querySelectorAll(".filters").forEach(group => {
  const grid = document.getElementById(group.dataset.for);
  group.addEventListener("click", e => {
    const btn = e.target.closest("button");
    if (!btn) return;
    group.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b === btn));
    const f = btn.dataset.filter;
    grid.querySelectorAll(".tile").forEach(t => { t.hidden = f !== "all" && !t.dataset.tags.split(" ").includes(f); });
  });
});

// Project galleries: one screenshot at a time, with previous/next buttons and a counter, auto-advancing
// like a replay reel. Autoplay pauses while hovered or focused, for a while after the visitor swipes,
// scrolls or uses the buttons, and while off-screen or in a background tab; off for reduced motion.
const SLIDE_MS = 4500, HOLD_AFTER_INPUT_MS = 8000;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
document.querySelectorAll(".gallery").forEach(g => {
  const slides = [...g.children];
  if (slides.length < 2) return;
  const nav = document.createElement("div");
  nav.className = "gallery-nav";
  nav.innerHTML = '<button type="button" aria-label="Previous screenshot">‹</button><span></span><button type="button" aria-label="Next screenshot">›</button>';
  g.after(nav);
  const [prev, count, next] = nav.children;

  const step = () => slides[1].offsetLeft - slides[0].offsetLeft;
  const current = () => Math.round(g.scrollLeft / step());
  const go = i => g.scrollTo({ left: ((i + slides.length) % slides.length) * step(), behavior: reduceMotion ? "auto" : "smooth" });
  const label = () => count.textContent = `${current() + 1} / ${slides.length}`;
  let hovered = false, focused = false, visible = true, lastInput = 0;
  const input = () => lastInput = Date.now();
  prev.addEventListener("click", () => { input(); go(current() - 1); });
  next.addEventListener("click", () => { input(); go(current() + 1); });
  g.addEventListener("scroll", label, { passive: true });
  label();
  if (reduceMotion) return;

  g.addEventListener("pointerenter", () => hovered = true);
  g.addEventListener("pointerleave", () => hovered = false);
  g.addEventListener("focusin", () => focused = true);
  g.addEventListener("focusout", () => focused = false);
  ["pointerdown", "wheel", "touchstart", "keydown"].forEach(ev => g.addEventListener(ev, input, { passive: true }));
  new IntersectionObserver(([e]) => visible = e.isIntersecting).observe(g);
  setInterval(() => {
    if (hovered || focused || !visible || document.hidden || Date.now() - lastInput < HOLD_AFTER_INPUT_MS) return;
    go(current() + 1);
  }, SLIDE_MS);
});
