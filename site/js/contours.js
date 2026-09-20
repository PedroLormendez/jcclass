/**
 * Marching-squares contour extraction for a regular lat/lon grid. Used to
 * turn a raw MSLP field into isobar line segments for drawing on the globe
 * canvas -- a prototype for testing the isobar-overlay idea (see
 * scripts/build_era5_mslp_zarr.py for where the MSLP grid itself comes
 * from). No line-joining: each crossed cell edge yields one segment, which
 * is enough for stroking a visually continuous line and keeps this simple.
 */

// Standard 16-case marching-squares table. Corners: a=top-left, b=top-right,
// c=bottom-right, d=bottom-left; index bit order a,b,c,d (a = MSB). Each case
// lists which edge pairs to connect: T=top(a-b), R=right(b-c), B=bottom(d-c),
// L=left(a-d). Cases 5 and 10 are saddles, resolved per-cell via the center
// (average of all four corners) against the level.
const EDGE_PAIRS = {
  1: [["L", "B"]],
  2: [["B", "R"]],
  3: [["L", "R"]],
  4: [["T", "R"]],
  6: [["T", "B"]],
  7: [["T", "L"]],
  8: [["T", "L"]],
  9: [["T", "B"]],
  11: [["T", "R"]],
  12: [["L", "R"]],
  13: [["B", "R"]],
  14: [["L", "B"]],
};

/**
 * @param {Float32Array|Array<number>} grid flat, row-major (nlat x nlon)
 * @param {Array<number>} lats length nlat
 * @param {Array<number>} lons length nlon
 * @param {Array<number>} levels contour values to extract
 * @returns {Map<number, Array<[number, number, number, number]>>} level -> segments as [lon0, lat0, lon1, lat1]
 */
export function computeContours(grid, lats, lons, levels) {
  const nlat = lats.length;
  const nlon = lons.length;
  const byLevel = new Map(levels.map((lv) => [lv, []]));

  for (let i = 0; i < nlat - 1; i++) {
    for (let j = 0; j < nlon - 1; j++) {
      const a = grid[i * nlon + j]; // top-left
      const b = grid[i * nlon + j + 1]; // top-right
      const d = grid[(i + 1) * nlon + j]; // bottom-left
      const c = grid[(i + 1) * nlon + j + 1]; // bottom-right
      if (!Number.isFinite(a) || !Number.isFinite(b) || !Number.isFinite(c) || !Number.isFinite(d)) continue;

      const lon0 = lons[j], lon1 = lons[j + 1];
      const lat0 = lats[i], lat1 = lats[i + 1];
      const lo = Math.min(a, b, c, d);
      const hi = Math.max(a, b, c, d);

      for (const level of levels) {
        if (level < lo || level > hi) continue;

        let idx = 0;
        if (a > level) idx |= 8;
        if (b > level) idx |= 4;
        if (c > level) idx |= 2;
        if (d > level) idx |= 1;
        if (idx === 0 || idx === 15) continue;

        const edgePoint = (edge) => {
          if (edge === "T") {
            const t = (level - a) / (b - a);
            return [lon0 + t * (lon1 - lon0), lat0];
          }
          if (edge === "R") {
            const t = (level - b) / (c - b);
            return [lon1, lat0 + t * (lat1 - lat0)];
          }
          if (edge === "B") {
            const t = (level - d) / (c - d);
            return [lon0 + t * (lon1 - lon0), lat1];
          }
          // "L"
          const t = (level - a) / (d - a);
          return [lon0, lat0 + t * (lat1 - lat0)];
        };

        let pairs;
        if (idx === 5) {
          const center = (a + b + c + d) / 4;
          pairs = center > level ? [["T", "R"], ["L", "B"]] : [["T", "L"], ["B", "R"]];
        } else if (idx === 10) {
          const center = (a + b + c + d) / 4;
          pairs = center > level ? [["T", "L"], ["B", "R"]] : [["T", "R"], ["L", "B"]];
        } else {
          pairs = EDGE_PAIRS[idx] ?? [];
        }

        const segs = byLevel.get(level);
        for (const [e0, e1] of pairs) {
          const [x0, y0] = edgePoint(e0);
          const [x1, y1] = edgePoint(e1);
          segs.push([x0, y0, x1, y1]);
        }
      }
    }
  }

  return byLevel;
}

/** Levels at a fixed hPa interval spanning the grid's actual range. */
export function levelsForRange(grid, interval = 4) {
  let lo = Infinity, hi = -Infinity;
  for (let k = 0; k < grid.length; k++) {
    const v = grid[k];
    if (!Number.isFinite(v)) continue;
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return [];
  const start = Math.ceil(lo / interval) * interval;
  const levels = [];
  for (let lv = start; lv <= hi; lv += interval) levels.push(lv);
  return levels;
}
