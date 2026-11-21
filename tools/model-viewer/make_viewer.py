#!/usr/bin/env python3
"""Build a shareable HTML 3D viewer from STL/OBJ/OFF/PLY/JSON or OpenSCAD.

Dependencies: Python 3 stdlib. Optional: openscad CLI for .scad, plotly for --offline.
Examples:
  python make_viewer.py battery_mount.scad --offline
  python make_viewer.py model.stl --output /tmp/inspect.html
  python make_viewer.py https://raw.githubusercontent.com/OWNER/REPO/main/model.stl
  cat model.scad | python make_viewer.py - --type scad --offline

The generated browser page includes the original triangle mesh and permits
loading other mesh files, pasted data, or CORS-enabled remote URLs.
"""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

MAX_BYTES = 30 * 1024 * 1024
DEFAULT_VIEWER = Path(__file__).with_name('viewer.html')


def load_source(source: str, kind: str | None) -> tuple[bytes, str]:
    if source == '-':
        if not kind:
            raise ValueError('For stdin, specify --type (e.g. --type scad)')
        data = sys.stdin.buffer.read(MAX_BYTES + 1)
        name = 'pasted-model.' + kind
    elif urllib.parse.urlsplit(source).scheme.lower() in ('http', 'https'):
        req = urllib.request.Request(source, headers={'User-Agent': 'Reusable3DModelViewer/1.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            data = response.read(MAX_BYTES + 1)
        name = Path(urllib.parse.urlsplit(source).path).name or 'remote-model.stl'
    else:
        p = Path(source).expanduser().resolve()
        data = p.read_bytes()
        name = p.name
    if len(data) > MAX_BYTES:
        raise ValueError('Input is larger than 30 MB')
    return data, name


def convert_scad(data: bytes, *, openscad: str) -> bytes:
    executable = shutil.which(openscad)
    if not executable:
        raise RuntimeError(f'OpenSCAD executable not found ({openscad}). Install OpenSCAD or provide an STL mesh.')
    with tempfile.TemporaryDirectory(prefix='model_viewer_') as tmp:
        scad = Path(tmp) / 'model.scad'
        stl = Path(tmp) / 'model.stl'
        scad.write_bytes(data)
        proc = subprocess.run([executable, '-o', str(stl), str(scad)],
                              text=True, capture_output=True, timeout=120,
                              check=False)
        if proc.returncode or not stl.exists() or not stl.stat().st_size:
            raise RuntimeError('OpenSCAD failed to compile:\n' + (proc.stderr or proc.stdout)[-3500:])
        result = stl.read_bytes()
        if len(result) > MAX_BYTES:
            raise ValueError('Compiled STL is larger than 30 MB')
        return result


def generate_html(html: str, data: bytes, filename: str, kind: str, offline: bool) -> str:
    payload = {'name': filename, 'format': kind, 'base64': base64.b64encode(data).decode('ascii')}
    # JSON is embedded in script[type=application/json], not evaluated as JavaScript.
    payload_json = json.dumps(payload, separators=(',', ':')).replace('<', '\\u003c')
    html = html.replace('<script id="embedded-model" type="application/json">null</script>',
                        f'<script id="embedded-model" type="application/json">{payload_json}</script>', 1)
    if offline:
        try:
            from plotly.offline import get_plotlyjs
        except ImportError as exc:
            raise RuntimeError('Offline mode requires Plotly: python -m pip install plotly') from exc
        html = html.replace('<script id="plotly-loader" src="https://cdn.plot.ly/plotly-3.3.1.min.js"></script>',
                            '<script id="plotly-loader">' + get_plotlyjs() + '</script>', 1)
    return html


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', help='model file, raw direct URL, or - (read stdin)')
    ap.add_argument('--type', choices=['scad', 'stl', 'obj', 'off', 'ply', 'json'],
                    help='file type (required for stdin; otherwise inferred by extension)')
    ap.add_argument('--output', '-o', type=Path, help='output HTML filename')
    ap.add_argument('--offline', action='store_true', help='bundle Plotly so the HTML works without Internet (requires Python plotly)')
    ap.add_argument('--openscad', default='openscad', help='OpenSCAD binary for .scad conversion')
    args = ap.parse_args()
    try:
        data, name = load_source(args.source, args.type)
        kind = args.type or Path(name).suffix.removeprefix('.').lower()
        if kind not in ('scad', 'stl', 'obj', 'off', 'ply', 'json'):
            raise ValueError('Unsupported file extension; specify --type stl/obj/off/ply/json/scad')
        if kind == 'scad':
            data = convert_scad(data, openscad=args.openscad)
            name = Path(name).stem + '.stl'
            kind = 'stl'
        template = DEFAULT_VIEWER.read_text(encoding='utf-8')
        result = generate_html(template, data, name, kind, args.offline)
        out = args.output or Path(name).with_suffix('.viewer.html')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result, encoding='utf-8')
        print(f'Created: {out.resolve()} ({out.stat().st_size:,} bytes)')
        print('Open this file in a browser. You can load further models through its file, URL and paste controls.')
        return 0
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
