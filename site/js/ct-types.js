// Colors match jcclass/plotting/functions/plot_utils.py::get_cmap_and_norm exactly.
// Labels/flag values are also read live from the zarr's own attrs at load time
// (data.js); this table is the single place colors are defined and is keyed
// by the same integer codes so the two stay in sync regardless of load order.
export const CT_COLORS = {
  "-1": "#7C7C77", // LF
  "0": "#17344F", // A
  "1": "#0255F4", // NE
  "2": "#0F78ED", // E
  "3": "#9E09EE", // SE
  "4": "#F6664C", // S
  "5": "#F24E64", // SW
  "6": "#D3C42D", // W
  "7": "#2FC698", // NW
  "8": "#20E1D7", // N
  "9": "#BD0000", // C
};

export function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
