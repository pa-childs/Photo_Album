from flask import Flask, redirect, render_template, request, url_for
from collections import defaultdict

import json, os, random

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_DIR = os.path.join(app.static_folder, "sets")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Set to False to hide the art section entirely from the UI
ART_SECTION = True

def normalize_name(value):
    value = value.strip()

    if not value:
        return ""

    # If the entire string is uppercase, keep it as-is
    if value.isupper():
        return value

    # Otherwise convert to title case
    return value.title()

@app.route("/set/<slug>/add-person", methods=["POST"])
def add_person(slug):
    raw_person = request.form.get("new_person", "")
    new_person = normalize_name(raw_person)

    if not new_person:
        return redirect(url_for("view_set", slug=slug))

    all_sets = load_all_sets()

    for image_set in all_sets:
        if image_set["slug"] == slug:
            existing_people_lower = [person.lower() for person in image_set["people"]]

            if new_person.lower() not in existing_people_lower:
                image_set["people"].append(new_person)

                meta_path = os.path.join(SETS_DIR, slug, "meta.json")

                with open(meta_path, "r") as meta_file:
                    meta = json.load(meta_file)

                meta["people"] = image_set["people"]

                with open(meta_path, "w") as meta_file:
                    json.dump(meta, meta_file, indent=4)

            break

    return redirect(url_for("view_set", slug=slug))

@app.route("/set/<slug>/add-tag", methods=["POST"])
def add_tag(slug):
    raw_tag = request.form.get("new_tag", "")
    new_tag = normalize_name(raw_tag)

    if not new_tag:
        return redirect(url_for("view_set", slug=slug))

    all_sets = load_all_sets()

    for image_set in all_sets:
        if image_set["slug"] == slug:
            existing_tags_lower = [tag.lower() for tag in image_set["tags"]]

            if new_tag.lower() not in existing_tags_lower:
                image_set["tags"].append(new_tag)

                meta_path = os.path.join(SETS_DIR, slug, "meta.json")

                with open(meta_path, "r") as meta_file:
                    meta = json.load(meta_file)

                meta["tags"] = image_set["tags"]

                with open(meta_path, "w") as meta_file:
                    json.dump(meta, meta_file, indent=4)

            break

    return redirect(url_for("view_set", slug=slug))

@app.route("/")
def archive():
    all_sets = load_all_sets()
    mode = request.args.get("mode", "photo")
    sort = request.args.get("sort")

    # If art section is disabled, force photo mode
    if not ART_SECTION:
        mode = "photo"

    if mode == "art":
        all_sets = [image_set for image_set in all_sets if image_set["type"] == "art"]

        grouped_art = defaultdict(list)
        for image_set in all_sets:
            series_name = image_set["series"] or image_set["title"]
            grouped_art[series_name].append(image_set)

        for series in grouped_art.values():
            series.sort(key=lambda image_set: image_set["issue"] or 0)

        return render_template(
            "archive.html",
            sets=all_sets,
            grouped_art=dict(sorted(grouped_art.items())),
            mode=mode,
            current_sort=None,
            art_section=ART_SECTION
        )

    # Photo mode (default)
    # When art section is disabled, show all types rather than hiding art sets
    if ART_SECTION:
        all_sets = [image_set for image_set in all_sets if image_set["type"] == "photo"]

    if sort == "title":
        all_sets.sort(key=lambda image_set: image_set["title"].lower())
    elif sort == "images":
        all_sets.sort(key=lambda image_set: image_set["image_count"], reverse=True)
    elif sort == "random":
        random.shuffle(all_sets)

    return render_template(
        "archive.html",
        sets=all_sets,
        grouped_art=None,
        mode=mode,
        current_sort=sort,
        art_section=ART_SECTION
    )

def load_all_sets():
    all_sets = []

    for folder in os.listdir(SETS_DIR):
        set_path = os.path.join(SETS_DIR, folder)

        if not os.path.isdir(set_path):
            continue

        meta_path = os.path.join(set_path, "meta.json")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as meta_file:
            meta = json.load(meta_file)

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

        all_sets.append({
            "slug": folder,
            "title": meta.get("title", folder),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "people": meta.get("people", []),
            "images": images,
            "cover": cover,
            "image_count": len(images),
            "mtime": folder_mtime,
            "type": meta.get("type", "photo").lower(),
            "series": meta.get("series", None),
            "issue": meta.get("issue", None)
        })

    all_sets.sort(key=lambda image_set: image_set["mtime"], reverse=True)

    return all_sets

@app.route("/people")
def people_index():
    all_sets = load_all_sets()

    people_counts = {}

    for image_set in all_sets:
        for person in image_set["people"]:
            people_counts[person] = people_counts.get(person, 0) + 1

    sorted_people = sorted(people_counts.items())

    grouped_people = defaultdict(list)

    for label, count in sorted_people:
        if not label or not label.strip():
            continue

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

@app.route("/set/<slug>/remove-person", methods=["POST"])
def remove_person(slug):
    person_to_remove = request.form.get("person_to_remove", "")

    all_sets = load_all_sets()

    for image_set in all_sets:
        if image_set["slug"] == slug:
            image_set["people"] = [person for person in image_set["people"] if person.lower() != person_to_remove.lower()]

            meta_path = os.path.join(SETS_DIR, slug, "meta.json")

            with open(meta_path, "r") as meta_file:
                meta = json.load(meta_file)

            meta["people"] = image_set["people"]

            with open(meta_path, "w") as meta_file:
                json.dump(meta, meta_file, indent=4)

            break

    return redirect(url_for("view_set", slug=slug))

@app.route("/set/<slug>/remove-tag", methods=["POST"])
def remove_tag(slug):
    tag_to_remove = request.form.get("tag_to_remove", "")

    all_sets = load_all_sets()

    for image_set in all_sets:
        if image_set["slug"] == slug:
            image_set["tags"] = [tag for tag in image_set["tags"] if tag.lower() != tag_to_remove.lower()]

            meta_path = os.path.join(SETS_DIR, slug, "meta.json")

            with open(meta_path, "r") as meta_file:
                meta = json.load(meta_file)

            meta["tags"] = image_set["tags"]

            with open(meta_path, "w") as meta_file:
                json.dump(meta, meta_file, indent=4)

            break

    return redirect(url_for("view_set", slug=slug))

@app.route("/tags")
def tags_index():
    all_sets = load_all_sets()

    tag_counts = {}

    for image_set in all_sets:
        for tag in image_set["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    sorted_tags = sorted(tag_counts.items())

    grouped_tags = defaultdict(list)

    for label, count in sorted_tags:
        if not label or not label.strip():
            continue

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
    all_sets = load_all_sets()
    image_set = next((image_set for image_set in all_sets if image_set["slug"] == slug), None)

    if not image_set:
        return "Set not found", 404

    return render_template("set.html", set=image_set)

@app.route("/tag/<tag_name>")
def view_tag(tag_name):
    all_sets = load_all_sets()

    filtered = [
        image_set for image_set in all_sets
        if tag_name in image_set["tags"]
    ]

    filtered.sort(key=lambda image_set: (image_set["series"] or "", image_set["issue"] or 0))

    return render_template(
        "archive.html",
        sets=filtered,
        filter_type="tag",
        filter_value=tag_name
    )

@app.route("/person/<person_name>")
def view_person(person_name):
    all_sets = load_all_sets()

    filtered = [
        image_set for image_set in all_sets
        if person_name in image_set["people"]
    ]

    return render_template(
        "archive.html",
        sets=filtered,
        filter_type="person",
        filter_value=person_name
    )

if __name__ == "__main__":
    app.run(debug=True)