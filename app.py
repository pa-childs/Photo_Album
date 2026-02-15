from flask import Flask, render_template, request
import json, os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_DIR = os.path.join(app.static_folder, "sets")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

@app.route("/")
def archive():
    sets = load_all_sets()
    return render_template("archive.html", sets=sets)

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

        meta_cover = meta.get("cover")

        if meta_cover in images:
            cover = meta_cover
        elif images:
            cover = images[0]
        else:
            cover = None

        sets.append({
            "slug": folder,
            "title": meta.get("title", folder),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "people": meta.get("people", []),
            "images": images,
            "cover": cover
        })

    return sets

@app.route("/people")
def people_index():
    sets = load_all_sets()

    people_counts = {}

    for s in sets:
        for person in s["people"]:
            people_counts[person] = people_counts.get(person, 0) + 1

    people = [
        {"label": person, "count": count}
        for person, count in sorted(people_counts.items())
    ]

    return render_template("people.html", people=people)
@app.route("/tags")

def tags_index():
    sets = load_all_sets()

    tag_counts = {}

    for s in sets:
        for tag in s["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    tags = [
        {"label": tag, "count": count}
        for tag, count in sorted(tag_counts.items())
    ]

    return render_template("tags.html", tags=tags)

@app.route("/set/<slug>")
def view_set(slug):
    sets = load_all_sets()
    set_obj = next((s for s in sets if s["slug"] == slug), None)

    if not set_obj:
        return "Set not found", 404

    return render_template("set.html", set=set_obj)

@app.route("/tag/<tag_name>")
def view_tag(tag_name):
    sets = load_all_sets()

    filtered = [
        s for s in sets
        if tag_name in s["tags"]
    ]

    return render_template(
        "archive.html",
        sets=filtered,
        filter_type="tag",
        filter_value=tag_name
    )

@app.route("/person/<person_name>")
def view_person(person_name):
    sets = load_all_sets()

    filtered = [
        s for s in sets
        if person_name in s["people"]
    ]

    return render_template(
        "archive.html",
        sets=filtered,
        filter_type="person",
        filter_value=person_name
    )

if __name__ == "__main__":
    app.run(debug=True)