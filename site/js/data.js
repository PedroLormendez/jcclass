import * as zarr from "zarrita";

const FILL_VALUE = -128;

/**
 * Thin wrapper around a zarrita-opened era5_cts.zarr store: loads the small
 * coordinate arrays and metadata once, then fetches one time step's cts_11
 * chunk at a time on demand (one HTTP request per step, matching how the
 * archive is chunked).
 */
export class CtsStore {
  constructor({ location, ctsArray, lats, lons, dates, meta }) {
    this.location = location;
    this.ctsArray = ctsArray;
    this.lats = lats;
    this.lons = lons;
    this.dates = dates; // JS Date[], one per valid_time step
    this.meta = meta; // group + array attrs, for provenance display
  }

  get ntime() {
    return this.ctsArray.shape[0];
  }
  get nlat() {
    return this.ctsArray.shape[1];
  }
  get nlon() {
    return this.ctsArray.shape[2];
  }

  /** Fetch + decode one time step's grid. Returns Int8Array of length nlat*nlon. */
  async getDay(timeIndex) {
    const chunk = await zarr.get(this.ctsArray, [timeIndex, null, null]);
    return chunk.data; // Int8Array, FILL_VALUE where masked/no-data
  }
}

const CF_TIME_UNIT_MS = {
  days: 86400000,
  hours: 3600000,
  minutes: 60000,
  seconds: 1000,
};

function decodeCfTime(rawValues, unitsAttr) {
  // xarray picks whichever unit exactly fits the data's spacing (e.g. "hours
  // since ..." for an hourly archive, "days since ..." for a daily one), so
  // this has to handle any of them, not just the cadence we happened to
  // write first.
  const m = /^(days|hours|minutes|seconds) since (.+)$/.exec(unitsAttr);
  if (!m) throw new Error(`Unsupported time units: ${unitsAttr}`);
  const [, unit, refStr] = m;
  const refMs = Date.parse(refStr.trim().replace(" ", "T") + "Z");
  const unitMs = CF_TIME_UNIT_MS[unit];
  return Array.from(rawValues, (v) => new Date(refMs + Number(v) * unitMs));
}

export async function openCtsStore(zarrUrl) {
  const store = new zarr.FetchStore(zarrUrl);
  const location = zarr.root(store);
  const group = await zarr.open(location, { kind: "group" });

  const ctsArray = await zarr.open(location.resolve("cts_11"), { kind: "array" });
  const latArray = await zarr.open(location.resolve("latitude"), { kind: "array" });
  const lonArray = await zarr.open(location.resolve("longitude"), { kind: "array" });
  const timeArray = await zarr.open(location.resolve("valid_time"), { kind: "array" });

  const [latData, lonData, timeData] = await Promise.all([
    zarr.get(latArray),
    zarr.get(lonArray),
    zarr.get(timeArray),
  ]);

  const dates = decodeCfTime(timeData.data, timeArray.attrs.units);

  return new CtsStore({
    location,
    ctsArray,
    lats: Array.from(latData.data),
    lons: Array.from(lonData.data),
    dates,
    meta: { group: group.attrs, cts_11: ctsArray.attrs },
  });
}

export { FILL_VALUE };
