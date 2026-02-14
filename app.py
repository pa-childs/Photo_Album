from flask import Flask, jsonify, render_template, request, send_from_directory, abort
from pathlib import Path
import json, os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_DIR = os.path.join(app.static_folder, "sets")

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
def archive():
    tag = request.args.get("tag")
    person = request.args.get("person")

    sets = load_all_sets()

    if tag:
        sets = [
            s for s in sets
            if any(p.lower() == tag.lower() for p in s["tags"])
        ]
    elif person:
        sets = [
            s for s in sets
            if any(p.lower() == person.lower() for p in s["people"])
        ]


    return render_template(
        "archive.html",
        sets=sets,
        active_tag=tag,
        active_person=person
    )

@app.route("/set/<slug>")
def view_set(slug):
    sets = load_all_sets()
    set_obj = next((s for s in sets if s["slug"] == slug), None)

    if not set_obj:
        return "Set not found", 404

    return render_template("set.html", set=set_obj)

def load_all_sets():
    sets = []

    for folder in os.listdir(SETS_DIR):
        set_path = os.path.join(SETS_DIR, folder)

        if not os.path.isdir(set_path):
            continue

        meta_path = os.path.join(set_path, "meta.json")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as f:
            meta = json.load(f)

        images = [
            file for file in os.listdir(set_path)
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]

        images.sort()

        sets.append({
            "slug": folder,
            "title": meta.get("title", folder),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "people": meta.get("people", []),
            "images": images,
            "cover": images[0] if images else None
        })

    return sets

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

    for set_dir in SETS_DIR.iterdir():
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
            "created": set_dir.stat().st_ctime  # <-- creation timestamp
        })

    # Sort by creation timestamp descending (most recent first)
    sets.sort(key=lambda s: s["created"], reverse=True)

    return sets

@app.route("/images/sets/<set_id>/<filename>")
def serve_image(set_id, filename):
    set_dir = SETS_DIR / set_id

    if not set_dir.exists() or not set_dir.is_dir():
        abort(404)

    return send_from_directory(set_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)