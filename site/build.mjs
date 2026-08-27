// Builds site/ into site/dist/: bundles js/app.js (and its zarrita/three
// deps) with esbuild, copies index.html + css, and copies the zarr archive
// from sample_data/ into dist/data/ so app.js's relative fetch resolves the
// same way in local dev and once deployed to Pages.
import { build } from "esbuild";
import { fileURLToPath } from "node:url";
import path from "node:path";
import fs from "node:fs";

const here = path.dirname(fileURLToPath(import.meta.url));
const dist = path.join(here, "dist");
const repoRoot = path.join(here, "..");

fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(path.join(dist, "js"), { recursive: true });
fs.mkdirSync(path.join(dist, "css"), { recursive: true });
fs.mkdirSync(path.join(dist, "data"), { recursive: true });

await build({
  entryPoints: [path.join(here, "js", "app.js")],
  bundle: true,
  minify: true,
  sourcemap: true,
  format: "esm",
  target: "es2022",
  outfile: path.join(dist, "js", "bundle.js"),
});

fs.copyFileSync(path.join(here, "index.html"), path.join(dist, "index.html"));
fs.copyFileSync(path.join(here, ".nojekyll"), path.join(dist, ".nojekyll"));
fs.cpSync(path.join(here, "css"), path.join(dist, "css"), { recursive: true });

const zarrSrc = path.join(repoRoot, "sample_data", "era5_cts.zarr");
const zarrDest = path.join(dist, "data", "era5_cts.zarr");
if (fs.existsSync(zarrSrc)) {
  fs.cpSync(zarrSrc, zarrDest, { recursive: true });
  console.log(`copied ${zarrSrc} -> ${zarrDest}`);
} else {
  console.warn(`WARNING: ${zarrSrc} not found, site will have no data to load`);
}

console.log("build complete:", dist);
