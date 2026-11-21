# Reusable 3D Model Viewer

A general-purpose browser-based tool for viewing models produced during InfoWindow development **and future projects**. Its source is stored only on the experimental `feature/esp32-c6-zigbee-infowindow` branch; the Raspberry Pi `master` branch is unchanged.

## Simple use — no installation

1. Open `viewer.html` in Chrome, Edge, Firefox, or Safari with an internet connection (needed once for Plotly from the CDN).
2. **Choose a model file** or drag/drop it onto the page. Supported: binary or ASCII **STL**, **OBJ** (geometry; materials ignored), **OFF**, ASCII **PLY**, and mesh **JSON** (`{"vertices": [[x,y,z],…], "faces": [[i,j,k],…]}`).
3. Or **paste the direct model URL** and click **Load**. For example, `https://raw.githubusercontent.com/justcop/InfoWindow/master/something.stl`. GitHub `blob` URLs are automatically translated to raw downloads.
4. Or **paste model data** (ASCII STL/OBJ/OFF/PLY/JSON) into the text box and press **Render pasted data**.
5. Rotate by dragging, zoom with mouse wheel or pinch, fit view, switch between perspective and orthographic, show axes, toggle/remove models, and save a PNG snapshot.

To preload a URL in a deployed viewer, use `viewer.html?url=https%3A%2F%2Fexample.com%2Fmodel.stl`.

**URL caveat:** The site serving a model must permit cross-origin browser requests (CORS). Browser-only code cannot bypass that. For unsupported hosts, download the file first and upload it locally. The viewer makes direct client-side HTTP(S) requests, not an external proxy. Do not embed token-bearing URLs in shared links.

## OpenSCAD source code, and shareable/offline previews

Browsers cannot directly render arbitrary OpenSCAD `.scad` code. The included Python helper makes this easy: it automatically compiles `.scad` to STL using the installed [OpenSCAD](https://openscad.org/) CLI, embeds the output geometry and writes a viewer HTML.

```bash
# .scad → ready-to-open HTML (requires openscad installed)
python make_viewer.py model.scad --offline -o model-preview.html

# Other 3D formats → HTML (no OpenSCAD needed)
python make_viewer.py model.stl --offline

# URL → HTML (you can also paste URLs into the viewer itself)
python make_viewer.py https://example.com/model.stl -o model-preview.html

# Pass model source code via stdin (especially convenient for AI-generated SCAD)
cat model.scad | python make_viewer.py - --type scad --offline -o model-preview.html
```

`--offline` bundles Plotly into the generated HTML (~5 MB), so the preview runs without an internet connection. It needs the Python `plotly` package (`pip install plotly`). Without `--offline`, the generated HTML uses a CDN, which is faster to build but needs an internet connection.

The embedded model remains entirely inside the resulting HTML; the user can still load other models from disk, pasted mesh data, or remote URLs.

## Formats / limitations

- Browser understands triangle-mesh formats, not arbitrary CAD scripts or CAD solid representations. **OpenSCAD requires the helper.** STEP/IGES, native Fusion 360 projects, 3MF and GLB/GLTF require converting to STL/OBJ first (or adding additional format loaders in the future).
- Plotly draws surfaces, not dimensionally guaranteed CAD measurements. Dimensions shown are the raw bounding box in *model units*, typically mm but not necessarily.
- Limit 30 MB per model and 180,000 triangles per model; simplify large models first.
- Remote loading works with CORS-enabled URLs, not normal GitHub HTML file pages or authentication-protected sites.
- Source HTML uses pinned Plotly 3.3.1 from the CDN. The `--offline` bundle is generated using the installed Plotly package (which may be a different version).

## GitHub project convention

When creating a new model in future ChatGPT conversations, save its `.scad` or `.stl` as usual, then run `make_viewer.py` to produce a clickable self-contained HTML preview. Keep this viewer general; do not bake a specific InfoWindow part into the reusable source. Use the `?url=` route when a direct remote mesh URL is available.

The source file `viewer.html` is a **generic empty viewer**; the model is inserted only when generating a preview or when using its input controls.