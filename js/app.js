/* Circadia — the loom */
(() => {
  const CATS = [
    { id: "work", label: "Work", color: "#e2b15a" },
    { id: "focus", label: "Focus", color: "#9b8ec4" },
    { id: "body", label: "Body", color: "#e06c5c" },
    { id: "life", label: "Life", color: "#7a9e7e" },
    { id: "people", label: "People", color: "#c97b8a" },
    { id: "other", label: "Other", color: "#6a9bb5" },
  ];

  const MONTHS = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December",
  ];
  const DOW = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  const DOW_S = ["S","M","T","W","T","F","S"];

  const $ = (id) => document.getElementById(id);
  const pad = (n) => String(n).padStart(2, "0");
  const dateStr = (d) =>
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const parseDate = (s) => {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  };
  const minutesToHHMM = (mins) => {
    const m = ((mins % 1440) + 1440) % 1440;
    return `${pad(Math.floor(m / 60))}:${pad(m % 60)}`;
  };
  const catOf = (id) => CATS.find((c) => c.id === id) || CATS[0];
  const uid = () =>
    crypto.randomUUID ? crypto.randomUUID() : "e" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

  const state = {
    events: [],
    selected: dateStr(new Date()),
    calCursor: new Date(),
    editing: null,
    reminderItem: null,
    soundOn: true,
    hour12: false,
    drag: null,
    plan: null,
    draftPlan: null,
  };

  /* ——— persistence of events in memory ——— */
  async function load() {
    await CircadiaDB.open();
    state.events = await CircadiaDB.getAllEvents();
    state.soundOn = (await CircadiaDB.getMeta("soundOn", true)) !== false;
    state.hour12 = (await CircadiaDB.getMeta("hour12", false)) === true;
    applyToggles();
    CircadiaReminders.setSound(state.soundOn);
    CircadiaReminders.setHour12(state.hour12);
    state.plan = (await CircadiaDB.getMeta("plan", null)) || null;
  }

  function eventsOn(day) {
    return state.events
      .filter((e) => CircadiaReminders.occursOn(e, day))
      .sort((a, b) => {
        if (a.allDay && !b.allDay) return -1;
        if (!a.allDay && b.allDay) return 1;
        return CircadiaReminders.parseMinutes(a.start) - CircadiaReminders.parseMinutes(b.start);
      });
  }

  /* ——— clock + ambient ——— */
  function formatClock(d) {
    const h = d.getHours();
    const m = pad(d.getMinutes());
    if (!state.hour12) return `${pad(h)}:${m}`;
    const ap = h >= 12 ? "pm" : "am";
    return `${((h + 11) % 12) + 1}:${m} ${ap}`;
  }

  function setAmbient(h) {
    let bg;
    if (h >= 5 && h < 8) bg = "radial-gradient(ellipse at 30% 0%, #3a2244 0%, #0c0b10 58%)";
    else if (h >= 8 && h < 12) bg = "radial-gradient(ellipse at 70% 0%, #3a2a16 0%, #0c0b10 55%)";
    else if (h >= 12 && h < 17) bg = "radial-gradient(ellipse at 50% 0%, #2a2816 0%, #0c0b10 55%)";
    else if (h >= 17 && h < 20) bg = "radial-gradient(ellipse at 80% 10%, #3d1c22 0%, #0c0b10 58%)";
    else bg = "radial-gradient(ellipse at 50% 100%, #14122c 0%, #0c0b10 55%)";
    $("ambient").style.background = bg;
  }

  let lastAgendaMin = -1;
  function tickClock() {
    const now = new Date();
    $("coreTime").textContent = formatClock(now).replace(/ am| pm/i, "");
    if (state.hour12) {
      $("coreKicker").textContent = now.getHours() >= 12 ? "pm · now" : "am · now";
    } else {
      $("coreKicker").textContent = "local time";
    }
    setAmbient(now.getHours());
    drawNowNeedle(now);
    updateCoreNext(now);
    const stamp = now.getHours() * 60 + now.getMinutes();
    if (stamp !== lastAgendaMin) {
      lastAgendaMin = stamp;
      renderAgenda();
    }
  }

  function updateCoreNext(now) {
    if (state.selected !== dateStr(now)) {
      const n = eventsOn(state.selected).length;
      $("coreNext").textContent = n ? `${n} thread${n === 1 ? "" : "s"} this day` : "No threads this day";
      return;
    }
    const mins = now.getHours() * 60 + now.getMinutes();
    const todays = eventsOn(state.selected).filter((e) => !e.allDay);
    const current = todays.find((e) => {
      const a = CircadiaReminders.parseMinutes(e.start);
      const b = CircadiaReminders.parseMinutes(e.end) || a + 30;
      return mins >= a && mins < b;
    });
    if (current) {
      $("coreNext").textContent = `In ${current.title}`;
      return;
    }
    const next = todays.find((e) => CircadiaReminders.parseMinutes(e.start) > mins);
    if (next) {
      const diff = CircadiaReminders.parseMinutes(next.start) - mins;
      const h = Math.floor(diff / 60);
      const m = diff % 60;
      const wait = h ? `${h}h ${m}m` : `${m}m`;
      $("coreNext").textContent = `${next.title} in ${wait}`;
      return;
    }
    $("coreNext").textContent = todays.length ? "Loom is quiet now" : "Drag the ring to begin";
  }

  /* ——— SVG dial ——— */
  const CX = 200, CY = 200, R_TICK = 176, R_LABEL = 164, R_ARC = 132;

  function minutesToAngle(mins) {
    return (mins / 1440) * 360 - 90;
  }
  function polar(r, mins) {
    const a = (minutesToAngle(mins) * Math.PI) / 180;
    return [CX + r * Math.cos(a), CY + r * Math.sin(a)];
  }
  function arcPath(r, a, b) {
    let start = a;
    let end = b;
    if (end <= start) end += 1440;
    const sweep = end - start;
    const large = sweep > 720 ? 1 : 0;
    const [x1, y1] = polar(r, start);
    const [x2, y2] = polar(r, end);
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  }

  function buildStaticDial() {
    const ticks = $("ticks");
    const hours = $("hours");
    ticks.innerHTML = "";
    hours.innerHTML = "";
    for (let i = 0; i < 144; i++) {
      const mins = i * 10;
      const major = i % 6 === 0;
      const hour = i % 18 === 0;
      const r1 = hour ? 182 : major ? 180 : 184;
      const r2 = 188;
      const [x1, y1] = polar(r1, mins);
      const [x2, y2] = polar(r2, mins);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", x1);
      line.setAttribute("y1", y1);
      line.setAttribute("x2", x2);
      line.setAttribute("y2", y2);
      line.setAttribute("stroke", hour ? "rgba(226,177,90,0.55)" : "rgba(226,177,90,0.18)");
      line.setAttribute("stroke-width", hour ? 1.6 : 1);
      ticks.appendChild(line);
    }
    for (let h = 0; h < 24; h += 3) {
      const [x, y] = polar(R_LABEL, h * 60);
      const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
      t.setAttribute("x", x);
      t.setAttribute("y", y);
      t.setAttribute("text-anchor", "middle");
      t.setAttribute("dominant-baseline", "middle");
      t.setAttribute("fill", "#b7b1a4");
      t.setAttribute("font-size", "9");
      t.setAttribute("font-family", "Outfit, sans-serif");
      t.setAttribute("letter-spacing", "0.12em");
      t.textContent = pad(h);
      hours.appendChild(t);
    }
  }

  function assignLanes(list) {
    const items = list
      .filter((e) => !e.allDay)
      .map((e) => ({
        e,
        a: CircadiaReminders.parseMinutes(e.start),
        b: CircadiaReminders.parseMinutes(e.end) || CircadiaReminders.parseMinutes(e.start) + 30,
      }));
    items.forEach((it) => {
      if (it.b <= it.a) it.b += 1440;
    });
    items.sort((x, y) => x.a - y.a);
    const lanes = [];
    items.forEach((it) => {
      let lane = 0;
      while (lanes[lane] && lanes[lane] > it.a) lane++;
      lanes[lane] = it.b;
      it.lane = lane;
    });
    return items;
  }

  function drawArcs() {
    const g = $("arcs");
    g.innerHTML = "";
    const laid = assignLanes(eventsOn(state.selected));
    laid.forEach((it) => {
      const r = R_ARC - it.lane * 20;
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", arcPath(r, it.a, it.b));
      path.setAttribute("fill", "none");
      path.setAttribute("stroke", catOf(it.e.category).color);
      path.setAttribute("stroke-width", 14);
      path.setAttribute("stroke-linecap", "round");
      path.setAttribute("opacity", "0.92");
      path.style.cursor = "pointer";
      path.dataset.id = it.e.id;
      path.addEventListener("click", (ev) => {
        ev.stopPropagation();
        openComposer(it.e);
      });
      g.appendChild(path);
    });
  }

  function drawNowNeedle(now) {
    const g = $("nowGroup");
    g.innerHTML = "";
    if (state.selected !== dateStr(now)) return;
    const mins = now.getHours() * 60 + now.getMinutes() + now.getSeconds() / 60;
    const [x2, y2] = polar(186, mins);
    const [x1, y1] = polar(118, mins);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("stroke", "#e2b15a");
    line.setAttribute("stroke-width", "1.6");
    g.appendChild(line);
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("cx", x2);
    dot.setAttribute("cy", y2);
    dot.setAttribute("r", 4.2);
    dot.setAttribute("fill", "#e2b15a");
    g.appendChild(dot);
    const tri = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    const [tx, ty] = polar(192, mins);
    const a = (minutesToAngle(mins) * Math.PI) / 180;
    const px = 5 * Math.cos(a + Math.PI / 2);
    const py = 5 * Math.sin(a + Math.PI / 2);
    const bx = tx - 9 * Math.cos(a);
    const by = ty - 9 * Math.sin(a);
    tri.setAttribute("points", `${tx},${ty} ${bx + px},${by + py} ${bx - px},${by - py}`);
    tri.setAttribute("fill", "#e2b15a");
    g.appendChild(tri);
  }

  function pointerMinutes(e) {
    const svg = $("dial");
    const rect = svg.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const pt = e.touches ? e.touches[0] : e;
    const dx = pt.clientX - cx;
    const dy = pt.clientY - cy;
    let deg = (Math.atan2(dy, dx) * 180) / Math.PI + 90;
    if (deg < 0) deg += 360;
    return Math.round(((deg / 360) * 1440) / 5) * 5;
  }

  function bindDialDrag() {
    const wrap = $("dialWrap");
    const onDown = (e) => {
      if (e.target.closest && e.target.closest("path[data-id]")) return;
      const start = pointerMinutes(e);
      state.drag = { start, end: start + 30 };
      e.preventDefault();
    };
    const onMove = (e) => {
      if (!state.drag) return;
      let end = pointerMinutes(e);
      if (end === state.drag.start) end = state.drag.start + 15;
      state.drag.end = end;
      paintDrag();
    };
    const onUp = () => {
      if (!state.drag) return;
      let a = state.drag.start;
      let b = state.drag.end;
      if (b < a) [a, b] = [b, a];
      if (b - a < 15) b = a + 30;
      const draft = {
        date: state.selected,
        start: minutesToHHMM(a),
        end: minutesToHHMM(b),
      };
      state.drag = null;
      paintDrag();
      openComposer(null, draft);
    };
    wrap.addEventListener("mousedown", onDown);
    wrap.addEventListener("touchstart", onDown, { passive: false });
    window.addEventListener("mousemove", onMove);
    window.addEventListener("touchmove", onMove, { passive: false });
    window.addEventListener("mouseup", onUp);
    window.addEventListener("touchend", onUp);
  }

  function paintDrag() {
    let ghost = document.getElementById("dragArc");
    if (!state.drag) {
      if (ghost) ghost.remove();
      return;
    }
    if (!ghost) {
      ghost = document.createElementNS("http://www.w3.org/2000/svg", "path");
      ghost.id = "dragArc";
      ghost.setAttribute("fill", "none");
      ghost.setAttribute("stroke", "rgba(226,177,90,0.7)");
      ghost.setAttribute("stroke-width", "14");
      ghost.setAttribute("stroke-linecap", "round");
      ghost.setAttribute("stroke-dasharray", "6 8");
      $("arcs").appendChild(ghost);
    }
    let a = state.drag.start;
    let b = state.drag.end;
    if (b < a) [a, b] = [b, a];
    ghost.setAttribute("d", arcPath(R_ARC, a, b === a ? a + 15 : b));
  }

  /* ——— ribbon, calendar, agenda ——— */
  function renderRibbon() {
    const root = $("ribbon");
    root.innerHTML = "";
    const sel = parseDate(state.selected);
    const start = new Date(sel);
    start.setDate(sel.getDate() - 3);
    for (let i = 0; i < 12; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      const ds = dateStr(d);
      const btn = document.createElement("button");
      btn.className = "day-pill";
      if (ds === dateStr(new Date())) btn.classList.add("is-today");
      if (ds === state.selected) btn.classList.add("is-selected");
      const marks = eventsOn(ds)
        .slice(0, 3)
        .map((e) => `<i style="background:${catOf(e.category).color}"></i>`)
        .join("");
      btn.innerHTML = `<span class="dow">${DOW[d.getDay()]}</span><span class="num">${d.getDate()}</span><span class="marks">${marks}</span>`;
      btn.addEventListener("click", () => selectDay(ds));
      root.appendChild(btn);
    }
  }

  function renderCalendar() {
    const y = state.calCursor.getFullYear();
    const m = state.calCursor.getMonth();
    $("calMonth").textContent = `${MONTHS[m].slice(0, 3)} ${y}`;
    const grid = $("calGrid");
    grid.innerHTML = "";
    DOW_S.forEach((d) => {
      const el = document.createElement("div");
      el.className = "hd";
      el.textContent = d;
      grid.appendChild(el);
    });
    const first = new Date(y, m, 1);
    const startPad = first.getDay();
    const days = new Date(y, m + 1, 0).getDate();
    const today = dateStr(new Date());
    for (let i = 0; i < startPad; i++) {
      const b = document.createElement("button");
      b.className = "cal-cell out";
      b.tabIndex = -1;
      grid.appendChild(b);
    }
    for (let day = 1; day <= days; day++) {
      const ds = `${y}-${pad(m + 1)}-${pad(day)}`;
      const b = document.createElement("button");
      b.className = "cal-cell";
      b.textContent = day;
      if (ds === today) b.classList.add("is-today");
      if (ds === state.selected) b.classList.add("is-selected");
      if (eventsOn(ds).length) b.classList.add("has");
      b.addEventListener("click", () => selectDay(ds));
      grid.appendChild(b);
    }
  }

  function renderCats() {
    $("catList").innerHTML = CATS.map(
      (c) =>
        `<div class="cat-row"><span class="swatch" style="background:${c.color}"></span>${c.label}</div>`
    ).join("");
    $("catChips").innerHTML = CATS.map(
      (c, i) =>
        `<button type="button" class="chip${i === 0 ? " is-on" : ""}" data-cat="${c.id}" style="--cat:${c.color}"><span class="swatch" style="background:${c.color}"></span>${c.label}</button>`
    ).join("");
    $("catChips").onclick = (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      $("catChips").querySelectorAll(".chip").forEach((c) => c.classList.remove("is-on"));
      chip.classList.add("is-on");
    };
  }

  function fmtRange(e) {
    if (e.allDay) return "All day";
    const a = CircadiaReminders.formatTime(e.start);
    const b = CircadiaReminders.formatTime(e.end);
    return b ? `${a} – ${b}` : a;
  }

  function renderAgenda() {
    const d = parseDate(state.selected);
    const today = dateStr(new Date());
    $("agendaKicker").textContent = state.selected === today ? "Today" : DOW[d.getDay()];
    $("agendaDate").textContent = d.getDate();
    $("agendaSub").textContent = `${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
    const list = eventsOn(state.selected);
    const root = $("agendaList");
    if (!list.length) {
      root.innerHTML = `<div class="empty"><p class="big">An open day</p><p>Press + Thread or drag across the ring.</p></div>`;
      return;
    }
    const now = new Date();
    const nowM = now.getHours() * 60 + now.getMinutes();
    const isToday = state.selected === today;
    root.innerHTML = "";
    list.forEach((e) => {
      const a = CircadiaReminders.parseMinutes(e.start);
      const b = CircadiaReminders.parseMinutes(e.end) || a + 30;
      const past = isToday && !e.allDay && b <= nowM;
      const current = isToday && !e.allDay && nowM >= a && nowM < b;
      const btn = document.createElement("button");
      btn.className = "event-card" + (past ? " is-past" : "") + (current ? " is-now" : "");
      btn.style.setProperty("--cat", catOf(e.category).color);
      btn.innerHTML = `<div class="when">${e.allDay ? "all day" : CircadiaReminders.formatTime(e.start).replace(" ", "\n")}</div>
        <div><p class="title"></p><div class="meta"></div></div>`;
      btn.querySelector(".title").textContent = e.title;
      btn.querySelector(".meta").textContent = [catOf(e.category).label, e.repeat && e.repeat !== "none" ? e.repeat : "", e.notes || ""]
        .filter(Boolean)
        .join(" · ");
      btn.addEventListener("click", () => openComposer(e));
      root.appendChild(btn);
    });
  }

  function selectDay(ds) {
    state.selected = ds;
    const d = parseDate(ds);
    if (d.getMonth() !== state.calCursor.getMonth() || d.getFullYear() !== state.calCursor.getFullYear()) {
      state.calCursor = new Date(d);
    }
    refresh();
  }

  function refresh() {
    renderRibbon();
    renderCalendar();
    drawArcs();
    tickClock();
    renderAgenda();
    renderPlanCard();
  }

  /* ——— composer ——— */
  function openComposer(event, draft) {
    state.editing = event ? event.id : null;
    $("composerTitle").textContent = event ? "Restitch" : "New thread";
    $("btnDelete").classList.toggle("hidden", !event);
    const form = $("composerForm");
    form.title.value = event ? event.title : "";
    form.date.value = event ? event.date : draft?.date || state.selected;
    form.start.value = event ? event.start : draft?.start || "09:00";
    form.end.value = event ? event.end : draft?.end || "10:00";
    form.allDay.checked = event ? !!event.allDay : false;
    form.reminder.value = event ? String(event.reminder) : "5";
    form.repeat.value = event ? event.repeat || "none" : "none";
    form.notes.value = event ? event.notes || "" : "";
    $("timeRow").style.opacity = form.allDay.checked ? 0.35 : 1;
    const cat = event ? event.category : "work";
    $("catChips").querySelectorAll(".chip").forEach((c) => {
      c.classList.toggle("is-on", c.dataset.cat === cat);
    });
    $("composer").classList.add("open");
    setTimeout(() => form.title.focus(), 50);
  }

  function closeComposer() {
    $("composer").classList.remove("open");
    state.editing = null;
  }

  $("composerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const cat = $("catChips").querySelector(".chip.is-on")?.dataset.cat || "work";
    const event = {
      id: state.editing || uid(),
      title: form.title.value.trim(),
      date: form.date.value,
      start: form.start.value || "09:00",
      end: form.end.value || "10:00",
      allDay: form.allDay.checked,
      category: cat,
      reminder: form.reminder.value,
      repeat: form.repeat.value,
      notes: form.notes.value.trim(),
      updatedAt: Date.now(),
    };
    if (!event.title) return;
    await CircadiaDB.putEvent(event);
    const idx = state.events.findIndex((x) => x.id === event.id);
    if (idx >= 0) state.events[idx] = event;
    else state.events.push(event);
    state.selected = event.date;
    closeComposer();
    refresh();
    CircadiaReminders.scheduleTriggers(state.events);
  });

  $("btnDelete").addEventListener("click", async () => {
    if (!state.editing) return;
    await CircadiaDB.deleteEvent(state.editing);
    state.events = state.events.filter((e) => e.id !== state.editing);
    closeComposer();
    refresh();
  });

  $("btnCancel").addEventListener("click", closeComposer);
  $("composer").addEventListener("click", (e) => {
    if (e.target === $("composer")) closeComposer();
  });
  $("composerForm").allDay.addEventListener("change", (e) => {
    $("timeRow").style.opacity = e.target.checked ? 0.35 : 1;
  });

  $("btnNew").addEventListener("click", () => openComposer());
  $("calPrev").addEventListener("click", () => {
    state.calCursor.setMonth(state.calCursor.getMonth() - 1);
    renderCalendar();
  });
  $("calNext").addEventListener("click", () => {
    state.calCursor.setMonth(state.calCursor.getMonth() + 1);
    renderCalendar();
  });

  /* ——— settings ——— */
  function applyToggles() {
    $("togSound").classList.toggle("on", state.soundOn);
    $("togSound").setAttribute("aria-pressed", String(state.soundOn));
    $("togHour").classList.toggle("on", state.hour12);
    $("togHour").setAttribute("aria-pressed", String(state.hour12));
  }

  $("btnSettings").addEventListener("click", () => $("settings").classList.add("open"));
  $("btnCloseSettings").addEventListener("click", () => $("settings").classList.remove("open"));
  $("settings").addEventListener("click", (e) => {
    if (e.target === $("settings")) $("settings").classList.remove("open");
  });
  $("togSound").addEventListener("click", async () => {
    state.soundOn = !state.soundOn;
    applyToggles();
    CircadiaReminders.setSound(state.soundOn);
    await CircadiaDB.setMeta("soundOn", state.soundOn);
  });
  $("togHour").addEventListener("click", async () => {
    state.hour12 = !state.hour12;
    applyToggles();
    CircadiaReminders.setHour12(state.hour12);
    await CircadiaDB.setMeta("hour12", state.hour12);
    refresh();
  });
  $("btnEnableNotes").addEventListener("click", async () => {
    const res = await CircadiaReminders.requestPermission();
    $("btnEnableNotes").textContent = res === "granted" ? "Armed" : res === "denied" ? "Blocked" : "Allow";
    updateStatus();
  });
  $("btnTest").addEventListener("click", () => {
    $("settings").classList.remove("open");
    const item = {
      id: "test|" + Date.now(),
      event: {
        id: "test",
        title: "A test lantern",
        start: minutesToHHMM(new Date().getHours() * 60 + new Date().getMinutes()),
        notes: "This is how a reminder pops — even with no internet.",
        category: "focus",
        allDay: false,
      },
      dateStr: state.selected,
    };
    CircadiaReminders.playChime();
    showReminder(item);
  });
  $("btnExport").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify({ events: state.events }, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "circadia-threads.json";
    a.click();
  });

  /* ——— reminders UI ——— */
  function showReminder(item) {
    state.reminderItem = item;
    const e = item.event;
    $("remKicker").textContent = item.snooze ? "Snoozed thread" : "It's time";
    $("remTitle").textContent = e.title || "Reminder";
    $("remMeta").textContent = `${fmtRange(e)} · ${catOf(e.category).label}`;
    $("remNotes").textContent = e.notes || "";
    $("reminderOverlay").classList.add("open");
  }
  function hideReminder() {
    $("reminderOverlay").classList.remove("open");
    state.reminderItem = null;
    CircadiaReminders.dismissed();
  }
  $("remDismiss").addEventListener("click", hideReminder);
  $("snooze5").addEventListener("click", () => {
    const item = state.reminderItem;
    $("reminderOverlay").classList.remove("open");
    state.reminderItem = null;
    if (item) CircadiaReminders.snooze(item, 5);
    else CircadiaReminders.dismissed();
  });
  $("snooze15").addEventListener("click", () => {
    const item = state.reminderItem;
    $("reminderOverlay").classList.remove("open");
    state.reminderItem = null;
    if (item) CircadiaReminders.snooze(item, 15);
    else CircadiaReminders.dismissed();
  });

  function updateStatus() {
    const chip = $("statusChip");
    const label = $("statusLabel");
    const online = navigator.onLine;
    const perm = "Notification" in window ? Notification.permission : "unsupported";
    chip.classList.remove("warn", "offline");
    if (!online) {
      chip.classList.add("offline");
      label.textContent = "Offline · armed";
      return;
    }
    if (perm === "granted") {
      label.textContent = "Popups armed";
    } else if (perm === "denied") {
      chip.classList.add("warn");
      label.textContent = "Popups blocked";
    } else {
      chip.classList.add("warn");
      label.textContent = "Popups idle";
    }
  }

  async function maybeCoach() {
    const seen = await CircadiaDB.getMeta("coach", false);
    if (seen) return;
    if (!("Notification" in window)) return;
    if (Notification.permission !== "default") return;
    $("coach").classList.add("show");
  }
  $("coachLater").addEventListener("click", async () => {
    $("coach").classList.remove("show");
    await CircadiaDB.setMeta("coach", true);
  });
  $("coachAllow").addEventListener("click", async () => {
    await CircadiaReminders.requestPermission();
    $("coach").classList.remove("show");
    await CircadiaDB.setMeta("coach", true);
    updateStatus();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeComposer();
      $("settings").classList.remove("open");
      if ($("reminderOverlay").classList.contains("open")) hideReminder();
    }
    const typing = /input|textarea|select/i.test(document.activeElement?.tagName);
    if (typing) return;
    if (e.key === "n" || e.key === "N") openComposer();
    if (e.key === "ArrowLeft") {
      const d = parseDate(state.selected);
      d.setDate(d.getDate() - 1);
      selectDay(dateStr(d));
    }
    if (e.key === "ArrowRight") {
      const d = parseDate(state.selected);
      d.setDate(d.getDate() + 1);
      selectDay(dateStr(d));
    }
  });

  window.addEventListener("online", updateStatus);
  window.addEventListener("offline", updateStatus);

  /* ——— service worker ——— */
  async function registerSW() {
    if (!("serviceWorker" in navigator)) return;
    try {
      await navigator.serviceWorker.register("./sw.js");
      navigator.serviceWorker.addEventListener("message", (e) => {
        if (e.data?.type === "check-reminders") CircadiaReminders.check();
        if (e.data?.type === "notification-click") CircadiaReminders.check();
      });
      const reg = await navigator.serviceWorker.ready;
      if (reg.periodicSync) {
        try {
          await reg.periodicSync.register("circadia-reminders", { minInterval: 15 * 60 * 1000 });
        } catch (err) {}
      }
    } catch (err) {}
  }

  async function seedIfEmpty() {
    const seen = await CircadiaDB.getMeta("seeded", false);
    if (seen || state.events.length) return;
    const today = dateStr(new Date());
    const h = new Date().getHours();
    const sample = [
      {
        id: uid(),
        title: "Morning pages",
        date: today,
        start: "07:30",
        end: "08:00",
        allDay: false,
        category: "focus",
        reminder: "5",
        repeat: "weekdays",
        notes: "Three pages, no audience.",
        updatedAt: Date.now(),
      },
      {
        id: uid(),
        title: "Deep work block",
        date: today,
        start: minutesToHHMM(Math.min(h * 60 + 30, 16 * 60)),
        end: minutesToHHMM(Math.min(h * 60 + 90, 17 * 60)),
        allDay: false,
        category: "work",
        reminder: "0",
        repeat: "none",
        notes: "Phone in another room.",
        updatedAt: Date.now(),
      },
      {
        id: uid(),
        title: "Walk at dusk",
        date: today,
        start: "18:15",
        end: "18:50",
        allDay: false,
        category: "body",
        reminder: "15",
        repeat: "none",
        notes: "",
        updatedAt: Date.now(),
      },
    ];
    for (const ev of sample) {
      await CircadiaDB.putEvent(ev);
      state.events.push(ev);
    }
    await CircadiaDB.setMeta("seeded", true);
  }

  /* ——— The Brief ——— */
  function esc(s) {
    return String(s || "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    })[c]);
  }

  function bindChipGroup(rootId, attr, onPick) {
    const root = $(rootId);
    if (!root) return;
    root.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      root.querySelectorAll(".chip").forEach((c) => c.classList.remove("is-on"));
      chip.classList.add("is-on");
      if (onPick) onPick(chip.dataset[attr]);
    });
  }

  function selectedChip(rootId, attr, fallback) {
    return $(rootId).querySelector(".chip.is-on")?.dataset[attr] || fallback;
  }

  function renderFreeDayChips(selected) {
    const root = $("freeDayChips");
    const on = selected && selected.length ? selected : [2, 4, 6];
    root.innerHTML = CircadiaPlanner.DAY_S.map(
      (label, i) =>
        `<button type="button" class="chip${on.includes(i) ? " is-on" : ""}" data-day="${i}">${label}</button>`
    ).join("");
  }

  $("freeDayChips").addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    chip.classList.toggle("is-on");
  });

  bindChipGroup("kindChips", "kind");
  bindChipGroup("timeChips", "time");
  bindChipGroup("styleChips", "style");

  function defaultDeadline() {
    const d = new Date();
    d.setDate(d.getDate() + 70);
    return dateStr(d);
  }

  function fillBriefForm(brief) {
    const form = $("briefForm");
    form.goal.value = brief?.goal || "";
    form.hoursPerWeek.value = brief?.hoursPerWeek || 6;
    form.deadline.value = brief?.deadline || defaultDeadline();
    form.reviewWeeks.value = String(brief?.reviewWeeks || 2);
    form.accountability.checked = !!brief?.accountability;
    form.commitments.value = brief?.commitments || "";
    form.startingPoint.value = brief?.startingPoint || "";
    form.target.value = brief?.target || "";
    const kind = brief?.kind || "learn";
    $("kindChips").querySelectorAll(".chip").forEach((c) => c.classList.toggle("is-on", c.dataset.kind === kind));
    const time = brief?.timeOfDay || "evening";
    $("timeChips").querySelectorAll(".chip").forEach((c) => c.classList.toggle("is-on", c.dataset.time === time));
    const style = brief?.sessionStyle || "daily";
    $("styleChips").querySelectorAll(".chip").forEach((c) => c.classList.toggle("is-on", c.dataset.style === style));
    renderFreeDayChips(brief?.freeDays);
  }

  function readBriefForm() {
    const form = $("briefForm");
    const freeDays = [...$("freeDayChips").querySelectorAll(".chip.is-on")].map((c) => Number(c.dataset.day));
    return {
      goal: form.goal.value.trim(),
      kind: selectedChip("kindChips", "kind", "learn"),
      hoursPerWeek: Number(form.hoursPerWeek.value),
      deadline: form.deadline.value,
      freeDays,
      timeOfDay: selectedChip("timeChips", "time", "evening"),
      sessionStyle: selectedChip("styleChips", "style", "daily"),
      reviewWeeks: Number(form.reviewWeeks.value),
      accountability: form.accountability.checked,
      commitments: form.commitments.value.trim(),
      startingPoint: form.startingPoint.value.trim(),
      target: form.target.value.trim(),
    };
  }

  function showBriefForm() {
    $("briefForm").classList.remove("hidden");
    $("briefResult").classList.add("hidden");
  }
  function showBriefResult() {
    $("briefForm").classList.add("hidden");
    $("briefResult").classList.remove("hidden");
  }

  function openBrief(mode) {
    if (mode === "result" && (state.draftPlan || state.plan)) {
      renderBriefResult(state.draftPlan || state.plan);
      showBriefResult();
    } else {
      fillBriefForm(state.plan?.brief || state.draftPlan?.brief);
      showBriefForm();
    }
    $("brief").classList.add("open");
  }
  function closeBrief() {
    $("brief").classList.remove("open");
  }

  function renderBriefResult(plan) {
    state.draftPlan = plan;
    const g = plan.brief.goal || "this work";
    $("resultTitle").textContent = g;
    $("resultLede").textContent =
      `${plan.weeks} weeks · ${plan.hoursPerWeek}h / week · ${plan.kindLabel.toLowerCase()} · on track by ${CircadiaPlanner.fmt(plan.deadline)}` +
      (plan.brief.startingPoint ? `. Starting from: ${plan.brief.startingPoint}` : "") +
      (plan.brief.target ? ` Target: ${plan.brief.target}` : "");

    $("resultFlags").innerHTML = (plan.flags || [])
      .map(
        (f) =>
          `<div class="flag ${f.level === "info" ? "info" : ""}"><span class="k">${
            f.level === "warn" ? "Unrealistic as written" : "A note"
          }</span>${esc(f.text)}<div class="alt">${esc(f.alternative)}</div></div>`
      )
      .join("");

    $("resultPhases").innerHTML = plan.phases
      .map(
        (p) => `<article class="phase">
        <div class="when">${esc(CircadiaPlanner.fmt(p.start))}<br>→ ${esc(CircadiaPlanner.fmt(p.end))}<br>${p.weeks} wk · ${p.hours}h</div>
        <div>
          <h4>${esc(p.name)}</h4>
          <p class="mile">${esc(p.milestone)}</p>
          <ul>${p.focus.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
        </div>
      </article>`
      )
      .join("");

    const byDay = new Map(plan.weekly.map((s) => [s.day, s]));
    $("resultWeek").innerHTML = CircadiaPlanner.DAY_S.map((label, i) => {
      const s = byDay.get(i);
      if (!s) {
        return `<div class="wo-day is-rest"><div class="dn">${label}</div><div class="slot">Rest</div></div>`;
      }
      const mins = s.minutes;
      const dur = mins >= 60 ? `${Math.round((mins / 60) * 10) / 10}h` : `${mins}m`;
      return `<div class="wo-day is-on"><div class="dn">${label}</div><div class="slot">${s.start}–${s.end}<br>${dur}</div></div>`;
    }).join("");

    $("resultTable").innerHTML =
      `<thead><tr><th>Week</th><th>Dates</th><th>Phase</th><th>Focus</th><th>Review</th></tr></thead><tbody>` +
      plan.weekByWeek
        .map(
          (w) => `<tr>
          <td>${w.week}</td>
          <td>${esc(CircadiaPlanner.fmt(w.from))} – ${esc(CircadiaPlanner.fmt(w.to))}</td>
          <td>${esc(w.phase)}</td>
          <td>${esc(w.focus)}</td>
          <td>${w.review ? esc(CircadiaPlanner.fmt(w.review)) : "—"}</td>
        </tr>`
        )
        .join("") +
      `</tbody>`;

    $("resultChecks").innerHTML = plan.checkpoints
      .map(
        (c) =>
          `<div class="flag info"><span class="k">Week ${c.week} · ${esc(CircadiaPlanner.fmt(c.date))}</span><strong>${esc(
            c.title
          )}</strong><div class="alt">${esc(c.notes)}</div></div>`
      )
      .join("");
  }

  function renderPlanCard() {
    const card = $("planCard");
    if (!state.plan) {
      card.classList.add("hidden");
      return;
    }
    card.classList.remove("hidden");
    const today = dateStr(new Date());
    const phase = state.plan.phases.find((p) => today >= p.start && today <= p.end) || state.plan.phases[0];
    const nextReview = (state.plan.checkpoints || []).find((c) => c.date >= today);
    $("planCardTitle").textContent = state.plan.brief.goal || "Active brief";
    $("planCardMeta").textContent = `${phase.name} · ${phase.weeks} wk phase · next review ${
      nextReview ? CircadiaPlanner.fmt(nextReview.date) : "—"
    }`;
  }

  $("btnBrief").addEventListener("click", () => openBrief(state.plan ? "result" : "form"));
  $("btnOpenPlan").addEventListener("click", () => openBrief("result"));
  $("btnBriefClose").addEventListener("click", closeBrief);
  $("btnBriefDismiss").addEventListener("click", async () => {
    if (state.draftPlan) {
      const stored = { ...state.draftPlan, events: [] };
      await CircadiaDB.setMeta("plan", stored);
      state.plan = stored;
      renderPlanCard();
    }
    closeBrief();
  });
  $("btnBriefRewrite").addEventListener("click", () => {
    fillBriefForm(state.draftPlan?.brief || state.plan?.brief);
    showBriefForm();
  });
  $("brief").addEventListener("click", (e) => {
    if (e.target === $("brief")) closeBrief();
  });

  $("briefForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const brief = readBriefForm();
    if (!brief.goal) return;
    const plan = CircadiaPlanner.weave(brief);
    renderBriefResult(plan);
    showBriefResult();
    $("brief").querySelector(".sheet").scrollTop = 0;
  });

  $("btnBriefStitch").addEventListener("click", async () => {
    const plan = state.draftPlan;
    if (!plan) return;
    const old = state.events.filter((ev) => ev.source === "plan");
    for (const ev of old) await CircadiaDB.deleteEvent(ev.id);
    state.events = state.events.filter((ev) => ev.source !== "plan");
    for (const ev of plan.events) {
      await CircadiaDB.putEvent(ev);
      state.events.push(ev);
    }
    await CircadiaDB.setMeta("plan", plan);
    state.plan = plan;
    closeBrief();
    refresh();
    CircadiaReminders.scheduleTriggers(state.events);
  });

  async function boot() {
    buildStaticDial();
    renderCats();
    bindDialDrag();
    await load();
    await seedIfEmpty();
    CircadiaReminders.configure({
      getEvents: async () => state.events,
      onShow: showReminder,
      onHide: () => {},
      soundOn: state.soundOn,
      hour12: state.hour12,
    });
    CircadiaReminders.arm();
    refresh();
    updateStatus();
    setInterval(tickClock, 1000);
    await registerSW();
    CircadiaReminders.scheduleTriggers(state.events);
    maybeCoach();
  }

  boot();
})();
