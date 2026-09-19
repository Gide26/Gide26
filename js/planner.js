/* Circadia — The Brief.
   Offline planner: turns a life-constraint brief into phases,
   a weekly rhythm, checkpoints, and loom-ready threads. */
const CircadiaPlanner = (() => {
  const DAY = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const DAY_S = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];

  const WINDOWS = {
    dawn: 5 * 60 + 30,
    morning: 7 * 60,
    afternoon: 13 * 60,
    evening: 18 * 60,
    night: 20 * 60 + 30,
  };

  const KINDS = {
    learn: {
      label: "Learn",
      cat: "focus",
      phases: [
        {
          name: "Foundations",
          share: 0.25,
          milestone: "You can do the basic work without looking everything up.",
          focus: [
            "Set up the tools and a single home for notes",
            "Daily drills on the absolute basics",
            "One tiny artifact (notebook, worksheet, or sketch) by the end",
          ],
        },
        {
          name: "Build",
          share: 0.35,
          milestone: "A small real project exists, however rough.",
          focus: [
            "Work from a project, not only tutorials",
            "One applied exercise every session",
            "Keep a 'stuck list' and close one item per week",
          ],
        },
        {
          name: "Depth",
          share: 0.25,
          milestone: "One piece of work you'd show someone.",
          focus: [
            "A portfolio-sized piece, not a new start",
            "Read other people's work and steal structure",
            "Harder problems on purpose, timed",
          ],
        },
        {
          name: "Ship",
          share: 0.15,
          milestone: "Done enough to demo, apply, or hand off.",
          focus: [
            "Polish the one piece — stop collecting new ones",
            "Write a short explanation of what you built",
            "A demo, mock interview, or publish date",
          ],
        },
      ],
    },
    train: {
      label: "Train",
      cat: "body",
      phases: [
        {
          name: "Adapt",
          share: 0.2,
          milestone: "Showing up is automatic; movement quality is clean.",
          focus: [
            "Learn the lifts or the route with light load",
            "Sleep and protein as part of the session notes",
            "Never miss twice",
          ],
        },
        {
          name: "Load",
          share: 0.35,
          milestone: "Weights or volume are moving up on a log.",
          focus: [
            "Progressive overload, written down",
            "Same session shape each week so you can compare",
            "One easy day stays easy",
          ],
        },
        {
          name: "Intensify",
          share: 0.3,
          milestone: "You can hit the working sets you planned.",
          focus: [
            "Peak sets, then honest accessories",
            "Guard rest — intensity without sleep is injury",
            "Deload if two sessions in a row feel ugly",
          ],
        },
        {
          name: "Arrive",
          share: 0.15,
          milestone: "A test week, then a lighter week, then the next cycle.",
          focus: [
            "Retest the original lifts or time",
            "Take a deload, even if you feel fine",
            "Write the next 8-week aim in one sentence",
          ],
        },
      ],
    },
    create: {
      label: "Create",
      cat: "work",
      phases: [
        {
          name: "Voice",
          share: 0.2,
          milestone: "You know what this is about, and you have a pile of ideas.",
          focus: [
            "Ten ideas, two practice pieces that stay private",
            "Define the audience in one sentence",
            "Set the format so you stop reinventing it",
          ],
        },
        {
          name: "Cadence",
          share: 0.4,
          milestone: "Publishing happens on a named day, not 'when it's ready'.",
          focus: [
            "Ship on a fixed weekday",
            "Batch one extra so a bad week doesn't break the chain",
            "Quantity over taste for this phase",
          ],
        },
        {
          name: "Craft",
          share: 0.25,
          milestone: "The work is recognizably yours, and tighter.",
          focus: [
            "One craft experiment per week (hook, edit, thumbnail, line)",
            "Kill anything that doesn't serve the point",
            "Study three pieces you admire, steal one move",
          ],
        },
        {
          name: "Grow",
          share: 0.15,
          milestone: "A small series, or a first collaboration, is out.",
          focus: [
            "Turn one idea into a series",
            "Ask for one guest, comment, or collab",
            "Review what actually got a response — drop the rest",
          ],
        },
      ],
    },
    launch: {
      label: "Launch",
      cat: "work",
      phases: [
        {
          name: "Scope",
          share: 0.2,
          milestone: "One sentence for the offer, and a short must-have list.",
          focus: [
            "Write the offer as if to one person",
            "Cut the list until it fits the hours you actually have",
            "Name the first person who will try it",
          ],
        },
        {
          name: "Build",
          share: 0.4,
          milestone: "The smallest version a stranger could use.",
          focus: [
            "Ship a slice, not the cathedral",
            "End each session with something runnable",
            "Park nice-to-haves on a later list",
          ],
        },
        {
          name: "Prove",
          share: 0.25,
          milestone: "Three people have used it; the top three frictions are fixed.",
          focus: [
            "Watch someone use it without helping",
            "Fix only what blocked them",
            "Write the launch note while the memory is fresh",
          ],
        },
        {
          name: "Ship",
          share: 0.15,
          milestone: "It's out. Then a quiet week of follow-up, not new features.",
          focus: [
            "Pick a launch day and tell people",
            "Office hours / replies for one week",
            "Only then decide what version two is",
          ],
        },
      ],
    },
    custom: {
      label: "Other",
      cat: "life",
      phases: [
        {
          name: "Orient",
          share: 0.2,
          milestone: "The target is specific enough that you would know if you missed it.",
          focus: [
            "Write 'done' in one sentence",
            "List what you already have vs. what you lack",
            "Protect the hours on the loom before adding more goals",
          ],
        },
        {
          name: "Practice",
          share: 0.4,
          milestone: "A weekly rhythm you can keep even on a bad week.",
          focus: [
            "Same days, same time, no bargaining",
            "Each session ends with a one-line log",
            "Drop one extra commitment if you miss twice",
          ],
        },
        {
          name: "Stretch",
          share: 0.25,
          milestone: "The work is harder than the version you started with.",
          focus: [
            "Raise the difficulty, not the hours",
            "Ask for one piece of outside feedback",
            "Keep the rest of life boring on purpose",
          ],
        },
        {
          name: "Arrive",
          share: 0.15,
          milestone: "You can point at the thing and say it exists.",
          focus: [
            "Finish, don't start a sibling project",
            "Show it to someone",
            "Schedule the review that sets the next brief",
          ],
        },
      ],
    },
  };

  function pad(n) {
    return String(n).padStart(2, "0");
  }
  function dateStr(d) {
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }
  function parseDate(s) {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  function addDays(d, n) {
    const x = new Date(d.getTime());
    x.setDate(x.getDate() + n);
    return x;
  }
  function fmt(s) {
    if (!s) return "";
    const d = typeof s === "string" ? parseDate(s) : s;
    return `${d.getDate()} ${MONTHS[d.getMonth()].slice(0, 3)} ${d.getFullYear()}`;
  }
  function minutesToHHMM(mins) {
    const m = ((mins % 1440) + 1440) % 1440;
    return `${pad(Math.floor(m / 60))}:${pad(m % 60)}`;
  }
  function uid() {
    return crypto.randomUUID
      ? crypto.randomUUID()
      : "p" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }
  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }
  function weeksBetween(a, b) {
    const ms = parseDate(b) - parseDate(a);
    return Math.max(1, Math.round(ms / (7 * 24 * 3600 * 1000)));
  }
  function nextWeekday(fromStr, weekday) {
    const d = parseDate(fromStr);
    const diff = (weekday - d.getDay() + 7) % 7;
    d.setDate(d.getDate() + diff);
    return dateStr(d);
  }
  function round15(mins) {
    return Math.round(mins / 15) * 15;
  }

  function distribute(totalMin, n, minM, maxM) {
    const step = 15;
    let each = round15(totalMin / n);
    each = clamp(each, minM, maxM);
    const slots = Array.from({ length: n }, () => each);
    let sum = each * n;
    let i = 0;
    let guard = 0;
    while (sum + step <= totalMin && guard < 80) {
      const idx = i % n;
      if (slots[idx] + step <= maxM) {
        slots[idx] += step;
        sum += step;
      }
      i++;
      guard++;
      if (slots.every((s) => s >= maxM)) break;
    }
    return { slots, sum };
  }

  function pickBlockDays(freeDays, count) {
    const prefer = [6, 0, 5, 4, 3, 2, 1];
    const ranked = prefer.filter((d) => freeDays.includes(d));
    const rest = freeDays.filter((d) => !ranked.includes(d));
    return ranked.concat(rest).slice(0, count).sort((a, b) => a - b);
  }

  function weave(brief) {
    const flags = [];
    const kind = KINDS[brief.kind] ? brief.kind : "custom";
    const kit = KINDS[kind];
    const today = dateStr(new Date());
    let start = brief.start && brief.start >= today ? brief.start : today;
    let deadline = brief.deadline || dateStr(addDays(new Date(), 70));
    if (deadline <= start) {
      flags.push({
        level: "warn",
        text: "The target date is already here or behind you.",
        alternative: "I moved it 8 weeks out so there is a season to work in. Change it if you meant a sprint that starts later.",
      });
      deadline = dateStr(addDays(parseDate(start), 56));
    }

    let freeDays = (brief.freeDays || []).map(Number).filter((d) => d >= 0 && d <= 6);
    freeDays = [...new Set(freeDays)].sort((a, b) => a - b);
    if (!freeDays.length) {
      flags.push({
        level: "warn",
        text: "No free days were marked.",
        alternative: "I used Tuesday, Thursday and Saturday — three days most people can actually defend. Edit the brief if your week looks different.",
      });
      freeDays = [2, 4, 6];
    }

    let hours = Number(brief.hoursPerWeek) || 0;
    if (hours <= 0) {
      flags.push({
        level: "warn",
        text: "Hours per week was empty.",
        alternative: "I set 5 hours — enough to move, not enough to wreck the rest of life.",
      });
      hours = 5;
    }

    let style = brief.sessionStyle === "blocks" ? "blocks" : "daily";
    if (style === "daily" && freeDays.length <= 2) {
      flags.push({
        level: "warn",
        text: "A 'daily' rhythm on one or two days is just a couple of appointments.",
        alternative: "Switched to long blocks on those days so the hours have somewhere to live.",
      });
      style = "blocks";
    }
    if (style === "blocks" && freeDays.length >= 5 && hours <= 5) {
      flags.push({
        level: "info",
        text: "Long blocks with five-plus free days and only a few hours will leave the week looking empty — and empty weeks are easy to skip.",
        alternative: "Switched to shorter sessions across the free days. Habit first, heroics later.",
      });
      style = "daily";
    }

    const maxPerDay = style === "daily" ? 120 : 240;
    const minPerDay = style === "daily" ? 30 : 90;
    const theoreticalMaxH = (freeDays.length * maxPerDay) / 60;
    if (hours > 15) {
      flags.push({
        level: "warn",
        text: `${hours} hours a week on top of existing commitments is where people quit, not where they finish.`,
        alternative: "Capped at 10 protected hours. Anything extra is bonus, not the plan.",
      });
      hours = 10;
    }
    if (hours > theoreticalMaxH) {
      flags.push({
        level: "warn",
        text: `${hours}h cannot fit into ${freeDays.length} day${freeDays.length === 1 ? "" : "s"} without sessions running longer than anyone keeps.`,
        alternative: `Capped at ${theoreticalMaxH}h, or add a free day / switch to ${style === "daily" ? "long blocks" : "more days"}.`,
      });
      hours = theoreticalMaxH;
    }
    if (hours < 3) {
      flags.push({
        level: "info",
        text: "Under 3 hours a week, progress will feel almost invisible.",
        alternative: "Keep this pace only if the deadline is honest. Otherwise: four sessions of 45 minutes, or push the date.",
      });
    }

    const timeOfDay = WINDOWS[brief.timeOfDay] ? brief.timeOfDay : "evening";
    const startMin = WINDOWS[timeOfDay];
    if (timeOfDay === "night" && style === "blocks" && hours / Math.min(3, freeDays.length) >= 2.5) {
      flags.push({
        level: "warn",
        text: "Long night blocks will eat sleep, and sleep is part of the work.",
        alternative: "I kept the night start but capped each block at 2 hours. Dawn or evening is kinder if you can move it.",
      });
    }
    if (timeOfDay === "dawn" && style === "blocks") {
      flags.push({
        level: "info",
        text: "Dawn long-blocks mean starting in the dark and finishing near the workday.",
        alternative: "Fine if you already wake then. Otherwise use dawn for 45–60 minutes and put the long block on a weekend morning.",
      });
    }

    const commit = (brief.commitments || "").toLowerCase();
    if (commit) {
      flags.push({
        level: "info",
        text: "You already named commitments. Those hours are not spare, even if a calendar looks empty.",
        alternative: "If a planned session collides with them, move the session — don't 'make it up' at midnight.",
      });
      if ((/evening|family|kids|dinner/.test(commit)) && (timeOfDay === "evening" || timeOfDay === "night")) {
        flags.push({
          level: "warn",
          text: "Family or evening commitments sit on top of an evening work block.",
          alternative: "Dawn or a weekend morning is usually the hour nobody else claims. Keep one evening only if it is already yours.",
        });
      }
      if ((/work|job|office|9\s*[–-]\s*5|8\s*[–-]\s*5/.test(commit)) && (timeOfDay === "morning" || timeOfDay === "afternoon")) {
        flags.push({
          level: "warn",
          text: "Work hours and a morning/afternoon block are likely to collide on weekdays.",
          alternative: "Park weekday sessions at dawn or after work, and put the long block on a free weekend day.",
        });
      }
      if (/sunday|church/.test(commit) && freeDays.includes(0)) {
        flags.push({
          level: "info",
          text: "Sunday is marked free, but you also mentioned Sunday/church.",
          alternative: "I left Sunday on the loom — uncheck it in the brief if that morning is already spoken for.",
        });
      }
    }

    let weeks = weeksBetween(start, deadline);
    const endDate = parseDate(deadline);
    if (weeks < 4 && kind !== "custom") {
      flags.push({
        level: "warn",
        text: `That's about ${weeks} week${weeks === 1 ? "" : "s"} — a sprint, not a season.`,
        alternative: "I kept your date, but collapsed the plan into fewer phases with one milestone only. Move the date if you wanted depth.",
      });
    }

    const nPhases = weeks <= 2 ? 2 : weeks <= 5 ? 3 : 4;
    const phaseSrc = kit.phases.slice(0, nPhases);
    const shareSum = phaseSrc.reduce((a, p) => a + p.share, 0);

    let remainingWeeks = weeks;
    const phases = phaseSrc.map((p, i) => {
      let w = i === phaseSrc.length - 1 ? remainingWeeks : Math.max(1, Math.round((p.share / shareSum) * weeks));
      if (w > remainingWeeks - (phaseSrc.length - 1 - i)) {
        w = Math.max(1, remainingWeeks - (phaseSrc.length - 1 - i));
      }
      remainingWeeks -= w;
      return { ...p, weeks: w };
    });
    if (remainingWeeks > 0) phases[phases.length - 1].weeks += remainingWeeks;

    let cursor = parseDate(start);
    phases.forEach((p) => {
      p.start = dateStr(cursor);
      const end = addDays(cursor, p.weeks * 7 - 1);
      if (end > endDate) p.end = deadline;
      else p.end = dateStr(end);
      p.hours = Math.round(p.weeks * hours);
      cursor = addDays(parseDate(p.end), 1);
    });

    const sessionDays =
      style === "blocks"
        ? pickBlockDays(freeDays, hours >= 8 && freeDays.length >= 3 ? 3 : Math.min(2, freeDays.length))
        : freeDays.slice();

    const cap = timeOfDay === "night" && style === "blocks" ? 120 : maxPerDay;
    const dist = distribute(Math.round(hours * 60), sessionDays.length, minPerDay, cap);
    if (dist.sum < hours * 60 - 20) {
      flags.push({
        level: "info",
        text: `Sessions add up to ${(dist.sum / 60).toFixed(1)}h, a little under the ${hours}h you asked for, because each day has a ceiling.`,
        alternative: "Add a free day if you want the missing minutes, or accept this as the honest week.",
      });
    }

    const weekly = sessionDays.map((day, i) => {
      const mins = dist.slots[i];
      let from = startMin;
      if (from + mins > 23 * 60 + 45) from = 23 * 60 + 45 - mins;
      if (from < 5 * 60) from = 5 * 60;
      return {
        day,
        dayName: DAY[day],
        start: minutesToHHMM(from),
        end: minutesToHHMM(from + mins),
        minutes: mins,
        title: brief.goal ? brief.goal : "Deep work",
        kind: "session",
      };
    });

    const reviewEvery = Number(brief.reviewWeeks) === 4 ? 4 : Number(brief.reviewWeeks) === 3 ? 3 : 2;
    const reviewWeekday = freeDays.includes(0) ? 0 : freeDays[freeDays.length - 1];
    const checkpoints = [];
    for (let w = reviewEvery; w <= weeks; w += reviewEvery) {
      const weekStart = addDays(parseDate(start), (w - 1) * 7);
      const when = nextWeekday(dateStr(weekStart), reviewWeekday);
      if (when > deadline) break;
      const phase = phases.find((p) => when >= p.start && when <= p.end) || phases[phases.length - 1];
      checkpoints.push({
        week: w,
        date: when,
        title: `Loom review · week ${w}`,
        phase: phase.name,
        notes: `Ask: What moved? What did I skip twice? What do I drop? Hours I actually did vs ${hours}h promised. Phase: ${phase.name}.`,
      });
    }
    if (!checkpoints.length) {
      checkpoints.push({
        week: weeks,
        date: deadline,
        title: "Loom review · end of brief",
        phase: phases[phases.length - 1].name,
        notes: "Did the target happen? If not, was it hours, focus, or an honest deadline?",
      });
    }

    const weekByWeek = [];
    for (let w = 1; w <= weeks; w++) {
      const ws = addDays(parseDate(start), (w - 1) * 7);
      const we = addDays(ws, 6);
      const mid = dateStr(addDays(ws, 3));
      const phase = phases.find((p) => mid >= p.start && mid <= p.end) || phases[Math.min(w - 1, phases.length - 1)];
      const review = checkpoints.find((c) => c.week === w);
      weekByWeek.push({
        week: w,
        from: dateStr(ws),
        to: dateStr(we > endDate ? endDate : we),
        phase: phase.name,
        focus: phase.focus[0],
        review: review ? review.date : null,
      });
    }

    const reminder = brief.accountability ? "5" : "15";
    const events = [];
    phases.forEach((phase) => {
      weekly.forEach((slot) => {
        const first = nextWeekday(phase.start, slot.day);
        if (first > phase.end) return;
        events.push({
          id: uid(),
          title: `${phase.name} · ${brief.goal || "Session"}`,
          date: first,
          start: slot.start,
          end: slot.end,
          allDay: false,
          category: kit.cat,
          reminder,
          repeat: "weekly",
          repeatEnd: phase.end,
          notes: phase.focus[0],
          source: "plan",
          updatedAt: Date.now(),
        });
      });
    });
    checkpoints.forEach((cp) => {
      events.push({
        id: uid(),
        title: cp.title,
        date: cp.date,
        start: weekly[weekly.length - 1] ? weekly[weekly.length - 1].start : "18:00",
        end: weekly[weekly.length - 1]
          ? minutesToHHMM(
              (function () {
                const [h, m] = (weekly[weekly.length - 1].start || "18:00").split(":").map(Number);
                return h * 60 + m + 40;
              })()
            )
          : "18:40",
        allDay: false,
        category: "life",
        reminder: "15",
        repeat: "none",
        notes: cp.notes,
        source: "plan",
        updatedAt: Date.now(),
      });
    });

    return {
      id: uid(),
      createdAt: Date.now(),
      brief: { ...brief, hoursPerWeek: hours, freeDays, sessionStyle: style, timeOfDay, deadline, start, kind },
      kind,
      kindLabel: kit.label,
      weeks,
      hoursPerWeek: Math.round((dist.sum / 60) * 10) / 10,
      askedHours: hours,
      start,
      deadline,
      flags,
      phases,
      weekly,
      checkpoints,
      weekByWeek,
      events,
      reviewEvery,
    };
  }

  return { weave, fmt, DAY, DAY_S, KINDS, WINDOWS };
})();
