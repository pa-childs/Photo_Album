from flask import Flask, render_template, jsonify, send_from_directory, abort
from pathlib import Path
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
SETS_DIR = BASE_DIR / "images" / "sets"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

@app.route("/api/sets/<set_id>")
def api_set(set_id):
    data = load_set(set_id)
    if data is None:
        abort(404)
    return jsonify(data)

@app.route("/api/sets")
def api_sets():
    return jsonify(load_sets())

@app.route("/")
def index():
    return render_template("index.html")

def load_set(set_id):
    set_dir = SETS_DIR / set_id

    if not set_dir.exists() or not set_dir.is_dir():
        return None

    meta_file = set_dir / "meta.json"
    meta = {}

    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}

    images = sorted(
        f"/images/sets/{set_id}/{f.name}"
        for f in set_dir.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS
    )

    return {
        "id": set_id,
        "title": meta.get("title", set_id),
        "tags": meta.get("tags", []),
        "description": meta.get("description", ""),
        "images": images,
    }

def load_sets():
    sets = []

    if not SETS_DIR.exists():
        return sets

    for set_dir in sorted(SETS_DIR.iterdir()):
        if not set_dir.is_dir():
            continue

        meta_file = set_dir / "meta.json"
        meta = {}

        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}

        images = sorted(
            f.name
            for f in set_dir.iterdir()
            if f.suffix.lower() in IMAGE_EXTENSIONS
        )

        preview_image = (
            f"/images/sets/{set_dir.name}/{images[0]}"
            if images else None
        )

        sets.append({
            "id": set_dir.name,
            "title": meta.get("title", set_dir.name),
            "tags": meta.get("tags", []),
            "description": meta.get("description", ""),
            "image_count": len(images),
            "preview_image": preview_image,
        })

    return sets

@app.route("/images/sets/<set_id>/<filename>")
def serve_image(set_id, filename):
    set_dir = SETS_DIR / set_id

    if not set_dir.exists() or not set_dir.is_dir():
        abort(404)

    return send_from_directory(set_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)