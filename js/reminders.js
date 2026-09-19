/* Circadia reminder engine — in-app cinematic popups + system notifications.
   Works fully offline. Data is local; the engine never talks to a server. */
const CircadiaReminders = (() => {
  const GRACE_MS = 30 * 60 * 1000; // catch missed reminders from the last 30 min
  let timer = null;
  let snoozes = []; // { id, at, event, dateStr }
  let queue = [];
  let showing = false;
  let soundOn = true;
  let hour12 = false;
  let audioCtx = null;
  let onShow = () => {};
  let onHide = () => {};
  let getEvents = async () => [];

  function configure(opts) {
    if (opts.getEvents) getEvents = opts.getEvents;
    if (opts.onShow) onShow = opts.onShow;
    if (opts.onHide) onHide = opts.onHide;
    if (typeof opts.soundOn === "boolean") soundOn = opts.soundOn;
    if (typeof opts.hour12 === "boolean") hour12 = opts.hour12;
  }

  function setSound(v) {
    soundOn = v;
  }

  function setHour12(v) {
    hour12 = v;
  }

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function parseMinutes(hhmm) {
    if (!hhmm) return 0;
    const [h, m] = hhmm.split(":").map(Number);
    return h * 60 + m;
  }

  function weekday(dateStr) {
    const [y, mo, d] = dateStr.split("-").map(Number);
    return new Date(y, mo - 1, d).getDay();
  }

  function occursOn(event, dateStr) {
    if (!event.repeat || event.repeat === "none") return event.date === dateStr;
    if (dateStr < event.date) return false;
    if (event.repeatEnd && dateStr > event.repeatEnd) return false;
    if (event.repeat === "daily") return true;
    if (event.repeat === "weekly") return weekday(dateStr) === weekday(event.date);
    if (event.repeat === "weekdays") {
      const d = weekday(dateStr);
      return d >= 1 && d <= 5;
    }
    return false;
  }

  function dateStrFromDate(d) {
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }

  function eventStartMs(event, dateStr) {
    const [y, mo, da] = dateStr.split("-").map(Number);
    if (event.allDay) return new Date(y, mo - 1, da, 9, 0, 0, 0).getTime();
    const mins = parseMinutes(event.start);
    return new Date(y, mo - 1, da, Math.floor(mins / 60), mins % 60, 0, 0).getTime();
  }

  function formatTime(hhmm) {
    if (!hhmm) return "";
    const [h, m] = hhmm.split(":").map(Number);
    if (!hour12) return `${pad(h)}:${pad(m)}`;
    const ap = h >= 12 ? "pm" : "am";
    const hr = ((h + 11) % 12) + 1;
    return `${hr}:${pad(m)} ${ap}`;
  }

  function fireId(event, dateStr) {
    return `${event.id}|${dateStr}|${event.reminder}`;
  }

  async function dueReminders(now = Date.now()) {
    const events = await getEvents();
    const today = new Date(now);
    const dates = [-1, 0, 1].map((off) => {
      const d = new Date(today);
      d.setDate(d.getDate() + off);
      return dateStrFromDate(d);
    });

    const due = [];
    for (const event of events) {
      if (event.reminder === "none" || event.reminder === "" || event.reminder == null) continue;
      const lead = Number(event.reminder);
      if (Number.isNaN(lead) || lead < 0) continue;
      for (const dateStr of dates) {
        if (!occursOn(event, dateStr)) continue;
        const start = eventStartMs(event, dateStr);
        const fireAt = start - lead * 60 * 1000;
        if (now >= fireAt && now <= start + GRACE_MS) {
          const id = fireId(event, dateStr);
          if (!(await CircadiaDB.wasFired(id))) {
            due.push({ id, event, dateStr, fireAt, start });
          }
        }
      }
    }

    let snoozeChanged = false;
    for (const s of snoozes.slice()) {
      if (now >= s.at) {
        due.push({ id: s.id + "|snooze|" + s.at, event: s.event, dateStr: s.dateStr, fireAt: s.at, start: s.at, snooze: true });
        snoozes = snoozes.filter((x) => x !== s);
        snoozeChanged = true;
      }
    }
    if (snoozeChanged) CircadiaDB.setMeta("snoozes", snoozes).catch(() => {});

    due.sort((a, b) => a.fireAt - b.fireAt);
    return due;
  }

  function playChime() {
    if (!soundOn) return;
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      if (!audioCtx) audioCtx = new AC();
      if (audioCtx.state === "suspended") audioCtx.resume();
      const ctx = audioCtx;
      const now = ctx.currentTime;
      const notes = [392, 523.25, 659.25, 783.99];
      notes.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = i === 3 ? "triangle" : "sine";
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.0001, now + i * 0.11);
        gain.gain.exponentialRampToValueAtTime(0.12, now + i * 0.11 + 0.03);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.11 + 0.9);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + i * 0.11);
        osc.stop(now + i * 0.11 + 1);
      });
    } catch (e) {
      /* autoplay may be blocked until a gesture; popup still shows */
    }
  }

  async function systemNotify(item) {
    const title = item.event.title || "Reminder";
    const when = item.event.allDay ? "All day" : formatTime(item.event.start);
    const body = `${when}${item.event.notes ? " · " + item.event.notes : ""}`;
    const tag = item.id;

    if (navigator.serviceWorker && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: "notify",
        title,
        body,
        tag,
        eventId: item.event.id,
      });
      return;
    }

    try {
      const reg = navigator.serviceWorker ? await navigator.serviceWorker.ready : null;
      if (reg && reg.showNotification) {
        await reg.showNotification(title, {
          body,
          icon: "./icons/icon-192.png",
          tag,
          renotify: true,
          vibrate: [180, 80, 180],
          requireInteraction: true,
          data: { eventId: item.event.id },
        });
        return;
      }
    } catch (e) {}

    if ("Notification" in window && Notification.permission === "granted") {
      try {
        new Notification(title, { body, icon: "./icons/icon-192.png", tag });
      } catch (e) {}
    }
  }

  async function scheduleTriggers(events) {
    if (!navigator.serviceWorker) return;
    let reg;
    try {
      reg = await navigator.serviceWorker.ready;
    } catch (e) {
      return;
    }
    const now = Date.now();
    const horizon = now + 7 * 24 * 60 * 60 * 1000;
    for (const event of events) {
      if (event.reminder === "none" || event.reminder == null || event.reminder === "") continue;
      const lead = Number(event.reminder);
      if (Number.isNaN(lead) || lead < 0) continue;
      for (let i = 0; i < 14; i++) {
        const d = new Date();
        d.setDate(d.getDate() + i);
        const dateStr = dateStrFromDate(d);
        if (!occursOn(event, dateStr)) continue;
        const start = eventStartMs(event, dateStr);
        const fireAt = start - lead * 60 * 1000;
        if (fireAt <= now || fireAt > horizon) continue;
        const id = fireId(event, dateStr);
        if (await CircadiaDB.wasFired(id)) continue;
        navigator.serviceWorker.controller?.postMessage({
          type: "schedule",
          timestamp: fireAt,
          title: event.title || "Reminder",
          body: event.allDay ? "All day" : formatTime(event.start),
          tag: id,
          eventId: event.id,
        });
      }
    }
  }

  async function present(item) {
    await CircadiaDB.markFired(item.id);
    queue.push(item);
    if (!showing) drain();
  }

  function drain() {
    if (showing) return;
    const item = queue.shift();
    if (!item) return;
    showing = true;
    playChime();
    try {
      navigator.vibrate && navigator.vibrate([180, 70, 180, 70, 260]);
    } catch (e) {}
    systemNotify(item);
    onShow(item);
  }

  function dismissed() {
    showing = false;
    onHide();
    if (queue.length) setTimeout(drain, 280);
  }

  function snooze(item, minutes) {
    const at = Date.now() + minutes * 60 * 1000;
    snoozes.push({
      id: item.event.id,
      at,
      event: item.event,
      dateStr: item.dateStr,
    });
    CircadiaDB.setMeta("snoozes", snoozes).catch(() => {});
    dismissed();
  }

  async function check() {
    const due = await dueReminders();
    for (const item of due) {
      await present(item);
    }
  }

  function arm() {
    disarm();
    const tick = async () => {
      try {
        await check();
      } catch (e) {}
      const now = Date.now();
      const msToNextMinute = 60000 - (now % 60000) + 40;
      timer = setTimeout(tick, Math.min(msToNextMinute, 15000));
    };
    tick();
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("focus", check);
  }

  function onVis() {
    if (document.visibilityState === "visible") check();
  }

  function disarm() {
    if (timer) clearTimeout(timer);
    timer = null;
    document.removeEventListener("visibilitychange", onVis);
    window.removeEventListener("focus", check);
  }

  async function requestPermission() {
    if (!("Notification" in window)) return "unsupported";
    if (Notification.permission === "granted") return "granted";
    if (Notification.permission === "denied") return "denied";
    try {
      const res = await Notification.requestPermission();
      return res;
    } catch (e) {
      return "denied";
    }
  }

  return {
    configure,
    setSound,
    setHour12,
    arm,
    disarm,
    check,
    dismissed,
    snooze,
    requestPermission,
    scheduleTriggers,
    occursOn,
    eventStartMs,
    formatTime,
    dateStrFromDate,
    parseMinutes,
    weekday,
    playChime,
  };
})();
