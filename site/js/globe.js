import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { LAND_RINGS } from "./land.js";
import { CT_COLORS, hexToRgb } from "./ct-types.js";

const RADIUS = 2;
const CT_COLORS_RGB = Object.fromEntries(
  Object.entries(CT_COLORS).map(([k, v]) => [k, hexToRgb(v)])
);

// Stipple dot tile: 2 dots per tileSize x tileSize tile, offset diagonally.
const DOT_TILE_SIZE = 12;
const DOT_RADIUS = 1.6;
// Faint color wash under the stipple, so a region's color still reads
// between dots instead of only at them -- otherwise adjacent, differently
// colored regions have nothing but sparse dots to tell them apart by.
const WASH_ALPHA = 0.58;

// The globe's ocean/land/coastline/starfield colors are painted onto a
// canvas texture, not styled with CSS, so they need their own theme
// palette. CT colors themselves stay fixed across themes -- they're the
// data, not chrome, and changing them would break visual consistency with
// the rest of the project (the static reference plots, the artifact).
const GLOBE_PALETTES = {
  dark: {
    ocean: "#0d1626",
    land: "#22304a",
    coastline: "rgba(255, 255, 255, 0.65)",
    stars: true,
    starColor: 0xaab4c8,
  },
  light: {
    ocean: "#dce4ef",
    land: "#c3cede",
    coastline: "rgba(20, 27, 39, 0.55)",
    stars: false,
    starColor: 0xaab4c8,
  },
};

function lonToX(lon, w) {
  return ((lon + 180) / 360) * w;
}
function latToY(lat, h) {
  return ((90 - lat) / 180) * h;
}

export class Globe {
  constructor(container, theme = "dark") {
    this.container = container;
    this.theme = theme;
    this.selected = new Set(Object.keys(CT_COLORS).map(Number));

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    this.camera.position.set(0, 0, 6.2);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.enablePan = false;
    this.controls.minDistance = 2.6;
    this.controls.maxDistance = 9;
    this.controls.rotateSpeed = 0.5;
    this.controls.zoomSpeed = 0.7;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.6;
    this.controls.addEventListener("start", () => {
      this.controls.autoRotate = false;
    });

    this._addStarfield();
    this._addGlobeMesh();
    this._addLights();

    window.addEventListener("resize", () => this.resize());
    this.resize();
    this._animate();
  }

  _addStarfield() {
    const count = 2200;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 40 + Math.random() * 60;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      color: GLOBE_PALETTES[this.theme].starColor,
      size: 0.06,
      sizeAttenuation: true,
    });
    this.stars = new THREE.Points(geom, mat);
    this.stars.visible = GLOBE_PALETTES[this.theme].stars;
    this.scene.add(this.stars);
  }

  _addLights() {
    this.scene.add(new THREE.AmbientLight(0xffffff, 1.0));
  }

  _addGlobeMesh() {
    // Canvas texture: land basemap baked in once; the data layer is redrawn
    // into the same canvas on top whenever the date/selection changes.
    this.texW = 2880;
    this.texH = 1440;
    this.canvas = document.createElement("canvas");
    this.canvas.width = this.texW;
    this.canvas.height = this.texH;
    this.ctx = this.canvas.getContext("2d");

    // Scratch canvas for compositing the CT color fill with the dot mask
    // each frame (see setDayData), and the mask itself -- both reused
    // across frames rather than rebuilt.
    this._dataLayer = document.createElement("canvas");
    this._dataLayer.width = this.texW;
    this._dataLayer.height = this.texH;
    this._dataLayerCtx = this._dataLayer.getContext("2d");
    this._dotMask = this._buildDotMask();

    this._drawBase();

    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.wrapS = THREE.RepeatWrapping;
    this.texture.wrapT = THREE.ClampToEdgeWrapping;
    this.texture.minFilter = THREE.NearestFilter; // no blending across CT boundaries
    this.texture.magFilter = THREE.NearestFilter;
    this.texture.colorSpace = THREE.SRGBColorSpace;

    const geometry = new THREE.SphereGeometry(RADIUS, 96, 64);
    const material = new THREE.MeshBasicMaterial({ map: this.texture });
    this.sphere = new THREE.Mesh(geometry, material);
    // Default SphereGeometry UV has seam/orientation that doesn't match a
    // lon=-180..180, lat=90..-90 equirectangular canvas; rotate so lon=0
    // faces the camera's default view, verified visually.
    this.sphere.rotation.y = -Math.PI / 2;
    this.scene.add(this.sphere);
  }

  _buildLandPath() {
    const { texW: w, texH: h } = this;
    const path = new Path2D();
    for (const ring of LAND_RINGS) {
      ring.forEach(([lon, lat], i) => {
        const x = lonToX(lon, w);
        const y = latToY(lat, h);
        if (i === 0) path.moveTo(x, y);
        else path.lineTo(x, y);
      });
      path.closePath();
    }
    return path;
  }

  /**
   * A full-canvas-sized, fully opaque-vs-transparent stipple pattern, built
   * once and reused every frame. Compositing the CT color fill against this
   * with "destination-in" (see setDayData) keeps only the dotted parts of
   * the fill, letting the basemap show through the gaps -- a stipple rather
   * than a flat wash, without redrawing per grid cell (up to ~230k of them)
   * on every frame, which a naive per-cell pattern fill would require.
   */
  _buildDotMask() {
    const tile = document.createElement("canvas");
    const tileSize = DOT_TILE_SIZE;
    tile.width = tileSize;
    tile.height = tileSize;
    const tctx = tile.getContext("2d");
    tctx.fillStyle = "#fff";
    tctx.beginPath();
    tctx.arc(tileSize * 0.25, tileSize * 0.25, DOT_RADIUS, 0, Math.PI * 2);
    tctx.arc(tileSize * 0.75, tileSize * 0.75, DOT_RADIUS, 0, Math.PI * 2);
    tctx.fill();

    const mask = document.createElement("canvas");
    mask.width = this.texW;
    mask.height = this.texH;
    const mctx = mask.getContext("2d");
    mctx.fillStyle = mctx.createPattern(tile, "repeat");
    mctx.fillRect(0, 0, this.texW, this.texH);
    return mask;
  }

  _drawBase() {
    const { ctx, texW: w, texH: h } = this;
    const palette = GLOBE_PALETTES[this.theme];
    this._landPath = this._buildLandPath();
    ctx.fillStyle = palette.ocean;
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = palette.land;
    ctx.fill(this._landPath);
    this._baseImageData = ctx.getImageData(0, 0, w, h);
  }

  /** Coastline outline, drawn on top of the data layer so it stays visible
   * against every CT color instead of being hidden underneath it. */
  _strokeCoastlines() {
    const { ctx } = this;
    ctx.strokeStyle = GLOBE_PALETTES[this.theme].coastline;
    ctx.lineWidth = 2.2; // texW/texH are 2x their original size; keep the same on-globe weight
    ctx.stroke(this._landPath);
  }

  /** Switch the ocean/land/coastline/starfield palette and repaint. */
  setTheme(theme) {
    if (!GLOBE_PALETTES[theme] || theme === this.theme) return;
    this.theme = theme;
    const palette = GLOBE_PALETTES[theme];
    this.stars.material.color.setHex(palette.starColor);
    this.stars.visible = palette.stars;
    this._drawBase();
    if (this._lastDay) {
      const { dayValues, lats, lons } = this._lastDay;
      this.setDayData(dayValues, lats, lons);
    } else {
      this.texture.needsUpdate = true;
    }
  }

  /** Redraw the data layer (grid of dayValues over lats/lons) onto the base. */
  setDayData(dayValues, lats, lons) {
    this._lastDay = { dayValues, lats, lons };
    const { ctx, texW: w, texH: h } = this;
    ctx.putImageData(this._baseImageData, 0, 0);

    const nlat = lats.length;
    const nlon = lons.length;
    const latStep = Math.abs(lats[1] - lats[0]);
    const lonStep = Math.abs(lons[1] - lons[0]);

    // Off-grid raster at data resolution, then scaled onto the canvas -- much
    // faster than one fillRect per cell for ~230k cells. Fully opaque here;
    // the stipple look comes from masking against _dotMask below, not from
    // per-pixel alpha.
    const off = document.createElement("canvas");
    off.width = nlon;
    off.height = nlat;
    const octx = off.getContext("2d");
    const img = octx.createImageData(nlon, nlat);
    for (let i = 0; i < nlat; i++) {
      for (let j = 0; j < nlon; j++) {
        const v = dayValues[i * nlon + j];
        const p = (i * nlon + j) * 4;
        if (v === -128 || !this.selected.has(v)) {
          img.data[p + 3] = 0;
          continue;
        }
        const [r, g, b] = CT_COLORS_RGB[String(v)] ?? [255, 0, 255];
        img.data[p] = r;
        img.data[p + 1] = g;
        img.data[p + 2] = b;
        img.data[p + 3] = 255;
      }
    }
    octx.putImageData(img, 0, 0);

    const x0 = lonToX(lons[0] - lonStep / 2, w);
    const x1 = lonToX(lons[nlon - 1] + lonStep / 2, w);
    const y0 = latToY(lats[0] + latStep / 2, h);
    const y1 = latToY(lats[nlat - 1] - latStep / 2, h);

    // Faint wash first, at full coverage, so color still reads between dots.
    ctx.imageSmoothingEnabled = false;
    ctx.globalAlpha = WASH_ALPHA;
    ctx.drawImage(off, 0, 0, nlon, nlat, x0, y0, x1 - x0, y1 - y0);
    ctx.globalAlpha = 1;

    // Then the full-opacity stipple on top: build the color fill on its own
    // layer, punch the dot pattern out of it (keep color only where the
    // mask is opaque), and composite that onto the base -- one full-canvas
    // composite, not one draw call per grid cell.
    const dctx = this._dataLayerCtx;
    dctx.clearRect(0, 0, w, h);
    dctx.imageSmoothingEnabled = false;
    dctx.drawImage(off, 0, 0, nlon, nlat, x0, y0, x1 - x0, y1 - y0);
    dctx.globalCompositeOperation = "destination-in";
    dctx.drawImage(this._dotMask, 0, 0);
    dctx.globalCompositeOperation = "source-over";

    ctx.drawImage(this._dataLayer, 0, 0);

    this._strokeCoastlines();

    this.texture.needsUpdate = true;
  }

  setSelected(selectedSet) {
    this.selected = selectedSet;
    if (this._lastDay) {
      const { dayValues, lats, lons } = this._lastDay;
      this.setDayData(dayValues, lats, lons);
    }
  }

  resize() {
    const { clientWidth: w, clientHeight: h } = this.container;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  _animate() {
    requestAnimationFrame(() => this._animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
