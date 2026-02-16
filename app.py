from flask import Flask, render_template, request
from collections import defaultdict

import json, os, random

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_DIR = os.path.join(app.static_folder, "sets")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

@app.route("/")
def archive():
    sets = load_all_sets()
    sort = request.args.get("sort")

    if sort == "title":
        sets.sort(key=lambda s: s["title"].lower())

    elif sort == "images":
        sets.sort(key=lambda s: s["image_count"], reverse=True)

    elif sort == "random":
        random.shuffle(sets)

    # default already sorted by newest

    return render_template(
        "archive.html",
        sets=sets,
        current_sort=sort
    )

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

        folder_mtime = os.path.getmtime(set_path)

        sets.append({
            "slug": folder,
            "title": meta.get("title", folder),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "people": meta.get("people", []),
            "images": images,
            "cover": cover,
            "image_count": len(images),
            "mtime": folder_mtime
        })

        sets.sort(key=lambda s: s["mtime"], reverse=True)

    return sets

@app.route("/people")
def people_index():
    sets = load_all_sets()

    people_counts = {}

    for s in sets:
        for person in s["people"]:
            people_counts[person] = people_counts.get(person, 0) + 1

    sorted_people = sorted(people_counts.items())

    grouped_people = defaultdict(list)

    for label, count in sorted_people:
        if not label or not label.strip():
            continue  # skip blanks safely

        clean_label = label.strip()
        first_letter = clean_label[0].upper()

        grouped_people[first_letter].append({
            "label": clean_label,
            "count": count
        })

    return render_template(
        "people.html",
        grouped_people=dict(grouped_people)
    )

@app.route("/tags")
def tags_index():
    sets = load_all_sets()

    tag_counts = {}

    for s in sets:
        for tag in s["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort alphabetically
    sorted_tags = sorted(tag_counts.items())

    # Group by first letter
    grouped_tags = defaultdict(list)

    for label, count in sorted_tags:
        if not label or not label.strip():
            continue  # skip empty tags safely

        clean_label = label.strip()
        first_letter = clean_label[0].upper()

        grouped_tags[first_letter].append({
            "label": clean_label,
            "count": count
        })

    return render_template(
        "tags.html",
        grouped_tags=dict(grouped_tags)
    )

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