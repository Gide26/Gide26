/* Shoot Like a Pro With Your Phone — small progressive enhancements.
   Everything on the page works without JS; this adds:
   - reading progress bar
   - table-of-contents scroll spy + mobile drawer
   - image lightbox
   - rule-of-thirds grid toggle
   - before / after editing slider
*/
(function () {
  "use strict";

  /* ---------- progress bar ---------- */
  var bar = document.querySelector(".progress");
  function updateProgress() {
    if (!bar) return;
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
    bar.style.width = pct + "%";
  }
  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();

  /* ---------- TOC scroll spy ---------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
  var sections = tocLinks
    .map(function (a) { return document.querySelector(a.getAttribute("href")); })
    .filter(Boolean);

  function setActive(id) {
    tocLinks.forEach(function (a) {
      a.classList.toggle("active", a.getAttribute("href") === "#" + id);
    });
  }

  if ("IntersectionObserver" in window && sections.length) {
    var visible = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      // pick the first visible section in document order
      for (var i = 0; i < sections.length; i++) {
        if (visible[sections[i].id]) { setActive(sections[i].id); return; }
      }
    }, { rootMargin: "-20% 0px -65% 0px", threshold: 0 });
    sections.forEach(function (s) { io.observe(s); });
  }

  /* ---------- mobile drawer ---------- */
  var sidebar = document.querySelector(".sidebar");
  var scrim = document.querySelector(".scrim");
  var toggle = document.querySelector(".toc-toggle");
  function closeDrawer() {
    if (!sidebar) return;
    sidebar.classList.remove("open");
    if (scrim) scrim.classList.remove("show");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      var open = sidebar.classList.toggle("open");
      if (scrim) scrim.classList.toggle("show", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    if (scrim) scrim.addEventListener("click", closeDrawer);
    tocLinks.forEach(function (a) { a.addEventListener("click", closeDrawer); });
  }

  /* ---------- lightbox ---------- */
  var lb = document.querySelector(".lightbox");
  if (lb) {
    var lbImg = lb.querySelector("img");
    var lbCap = lb.querySelector(".cap");
    var lbClose = lb.querySelector(".close");
    function openLightbox(img) {
      lbImg.src = img.currentSrc || img.src;
      lbImg.alt = img.alt || "";
      var fig = img.closest("figure");
      var cap = fig ? fig.querySelector("figcaption") : null;
      var card = img.closest(".card");
      var title = card ? card.querySelector("h4") : null;
      lbCap.textContent = cap ? cap.textContent.trim() : (title ? title.textContent.trim() : (img.alt || ""));
      lb.classList.add("open");
      document.body.style.overflow = "hidden";
    }
    function closeLightbox() {
      lb.classList.remove("open");
      lbImg.src = "";
      document.body.style.overflow = "";
    }
    document.addEventListener("click", function (ev) {
      var img = ev.target.closest(".figure img, .card img");
      if (!img) return;
      if (img.closest(".grid-demo") || img.closest(".ba")) return; // interactive demos handle themselves
      openLightbox(img);
    });
    lb.addEventListener("click", function (ev) {
      if (ev.target === lb || ev.target === lbClose) closeLightbox();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { closeLightbox(); closeDrawer(); }
    });
  }

  /* ---------- rule of thirds toggle ---------- */
  document.querySelectorAll(".grid-demo").forEach(function (demo) {
    var btn = demo.querySelector(".toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var off = demo.classList.toggle("off");
      btn.textContent = off ? "Show grid" : "Hide grid";
      btn.setAttribute("aria-pressed", off ? "false" : "true");
    });
  });

  /* ---------- before / after slider ---------- */
  document.querySelectorAll(".ba").forEach(function (ba) {
    var range = ba.querySelector("input[type=range]");
    var before = ba.querySelector(".before");
    var handle = ba.querySelector(".handle");
    if (!range || !before || !handle) return;
    function update() {
      var v = Number(range.value);
      before.style.clipPath = "inset(0 " + (100 - v) + "% 0 0)";
      handle.style.left = v + "%";
    }
    range.addEventListener("input", update);
    update();
  });

  /* ---------- print button ---------- */
  document.querySelectorAll("[data-print]").forEach(function (b) {
    b.addEventListener("click", function () { window.print(); });
  });
})();
