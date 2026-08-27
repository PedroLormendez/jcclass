import { openCtsStore } from "./data.js";
import { Globe } from "./globe.js";
import { CT_COLORS } from "./ct-types.js";

const CT_LABELS = {
  "-1": "LF", "0": "A", "1": "NE", "2": "E", "3": "SE",
  "4": "S", "5": "SW", "6": "W", "7": "NW", "8": "N", "9": "C",
};
const CT_ORDER = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

const DATA_URL = new URL("../data/era5_cts.zarr", import.meta.url).href;

const globeContainer = document.getElementById("globe");
const legendList = document.getElementById("legend-list");
const slider = document.getElementById("time-slider");
const dateLabel = document.getElementById("date-label");
const statusEl = document.getElementById("status");
const playBtn = document.getElementById("play-btn");
const themeToggle = document.getElementById("theme-toggle");

const PLAY_INTERVAL_MS = 500;

// index.html's inline head script already picked light/dark (saved
// preference, else system) and set this before first paint, so read it
// back rather than re-detecting.
function currentTheme() {
  return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
}

function initThemeToggle(globe) {
  themeToggle.setAttribute("aria-label", currentTheme() === "dark" ? "Switch to light mode" : "Switch to dark mode");
  themeToggle.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
    themeToggle.setAttribute("aria-label", next === "dark" ? "Switch to light mode" : "Switch to dark mode");
    globe.setTheme(next);
  });
}

function buildLegend(globe) {
  const rows = new Map(); // code -> row element, so isolate/restore can sync every row at once

  function syncRows() {
    for (const [c, row] of rows) {
      const active = globe.selected.has(c);
      row.classList.toggle("active", active);
      row.setAttribute("aria-pressed", String(active));
    }
  }

  for (const code of CT_ORDER) {
    const row = document.createElement("button");
    row.className = "legend-row active";
    row.type = "button";
    row.title = "Click to toggle, double-click to isolate";
    row.dataset.code = String(code);
    row.setAttribute("aria-pressed", "true");

    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = CT_COLORS[String(code)];

    const label = document.createElement("span");
    label.className = "label";
    label.textContent = CT_LABELS[String(code)];

    row.append(swatch, label);

    row.addEventListener("click", () => {
      const c = Number(row.dataset.code);
      if (globe.selected.has(c)) globe.selected.delete(c);
      else globe.selected.add(c);
      syncRows();
      globe.setSelected(globe.selected);
    });

    // Double-click isolates this type; double-clicking an already-isolated
    // type restores all of them. A dblclick fires alongside two click
    // events (which toggle this row twice, net no-op on its own state), but
    // isolate/restore-all set the full selection outright, so the result
    // is correct regardless -- no need to suppress the single-click pair.
    row.addEventListener("dblclick", () => {
      const c = Number(row.dataset.code);
      const isIsolated = globe.selected.size === 1 && globe.selected.has(c);
      globe.selected.clear();
      if (isIsolated) {
        CT_ORDER.forEach((code) => globe.selected.add(code));
      } else {
        globe.selected.add(c);
      }
      syncRows();
      globe.setSelected(globe.selected);
    });

    rows.set(code, row);
    legendList.appendChild(row);
  }
}

function fmtDate(d) {
  // "2010-09-15 14:00 UTC" -- the archive can hold daily or hourly (or any
  // other) cadence, so always show the hour rather than assuming one day
  // per step.
  return `${d.toISOString().slice(0, 10)} ${d.toISOString().slice(11, 16)} UTC`;
}

async function main() {
  const globe = new Globe(globeContainer, currentTheme());
  buildLegend(globe);
  initThemeToggle(globe);

  statusEl.textContent = "Loading archive metadata…";
  const store = await openCtsStore(DATA_URL);

  slider.min = 0;
  slider.max = store.ntime - 1;
  slider.value = store.ntime - 1;

  // Token pattern rather than a plain busy flag: a rapid slider drag fires
  // several "input" events, and we want the *last* one to win, not for the
  // first one to swallow the rest.
  let requestToken = 0;
  async function showDay(index) {
    const token = ++requestToken;
    dateLabel.textContent = fmtDate(store.dates[index]);
    statusEl.textContent = "Loading…";
    try {
      const values = await store.getDay(index);
      if (token !== requestToken) return; // superseded by a newer request
      globe.setDayData(values, store.lats, store.lons);
      statusEl.textContent = "";
    } catch (err) {
      if (token !== requestToken) return;
      console.error("Failed to load time step", index, err);
      statusEl.textContent = `Error: ${err.message}`;
    }
  }

  // Play/pause: steps forward one time index at a time, waiting for each
  // fetch+render to finish before scheduling the next tick (rather than a
  // fixed-rate setInterval) so a slow connection can't pile up requests.
  // Loops back to the start at the end.
  let playing = false;

  function setPlaying(next) {
    playing = next;
    playBtn.classList.toggle("playing", playing);
    playBtn.setAttribute("aria-label", playing ? "Pause" : "Play");
    playBtn.setAttribute("aria-pressed", String(playing));
  }

  async function playLoop() {
    while (playing) {
      const next = (Number(slider.value) + 1) % store.ntime;
      slider.value = next;
      await showDay(next);
      if (!playing) break;
      await new Promise((resolve) => setTimeout(resolve, PLAY_INTERVAL_MS));
    }
  }

  playBtn.addEventListener("click", () => {
    if (playing) {
      setPlaying(false);
    } else {
      setPlaying(true);
      playLoop();
    }
  });

  slider.addEventListener("input", () => {
    setPlaying(false);
    showDay(Number(slider.value));
  });

  await showDay(store.ntime - 1);
}

main().catch((err) => {
  console.error(err);
  statusEl.textContent = `Failed to load: ${err.message}`;
});
