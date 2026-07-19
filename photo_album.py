from flask import Flask, redirect, render_template, request, url_for, jsonify
from collections import defaultdict

import argparse, json, os, random, re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_DIR = os.path.join(app.static_folder, "sets")
COLLECTIONS_DIR = os.path.join(app.static_folder, "collections")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ART_SECTION = True          # Set to False to hide the art section entirely from the UI
LIGHTBOX_THUMBNAILS = True  # Set to False to hide the thumbnail strip at the bottom of the lightbox

def normalize_name(value):
    value = value.strip()

    if not value:
        return ""

    # If the entire string is uppercase, keep it as-is
    if value.isupper():
        return value

    # Otherwise convert to title case
    return value.title()

def slugify(value):
    value = value.strip().lower()
    value = re.sub(r'[^\w\s-]', '', value)
    value = re.sub(r'[\s_]+', '-', value)
    value = re.sub(r'-+', '-', value)
    return value.strip('-')

def load_all_collections():
    all_collections = []

    if not os.path.exists(COLLECTIONS_DIR):
        return all_collections

    for folder in os.listdir(COLLECTIONS_DIR):
        collection_path = os.path.join(COLLECTIONS_DIR, folder)

        if not os.path.isdir(collection_path):
            continue

        json_path = os.path.join(collection_path, "collection.json")
        if not os.path.exists(json_path):
            continue

        with open(json_path) as f:
            data = json.load(f)

        # Resolve cover image URL if set
        cover_url = None
        cover = data.get("cover")
        if cover and isinstance(cover, dict):
            cover_set = cover.get("set")
            cover_image = cover.get("image")
            if cover_set and cover_image:
                basename = cover_image.rsplit('.', 1)[0]
                cover_url = f"sets/{cover_set}/thumbnails/{basename}_thumb_400.jpg"

        all_collections.append({
            "folder": folder,
            "slug": data.get("slug", folder),
            "title": data.get("title", folder),
            "images": data.get("images", []),
            "image_count": len(data.get("images", [])),
            "cover_url": cover_url,
            "cover": cover,
            "mtime": os.path.getmtime(collection_path)
        })

    all_collections.sort(key=lambda c: c["title"].lower())

    return all_collections

def get_next_collection_folder():
    if not os.path.exists(COLLECTIONS_DIR):
        os.makedirs(COLLECTIONS_DIR)
        return "10000"

    existing = [
        int(f) for f in os.listdir(COLLECTIONS_DIR)
        if os.path.isdir(os.path.join(COLLECTIONS_DIR, f)) and f.isdigit()
    ]

    return str(max(existing) + 1) if existing else "10000"

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
    if ART_SECTION:
        all_sets = [image_set for image_set in all_sets if image_set["type"] == "photo"]

    if sort == "images":
        all_sets.sort(key=lambda image_set: image_set["image_count"], reverse=True)
    elif sort == "random":
        random.shuffle(all_sets)
    elif sort == "recent":
        all_sets.sort(key=lambda image_set: image_set["mtime"], reverse=True)
    else:
        # Default: folder number descending
        all_sets.sort(key=lambda image_set: int(image_set["slug"]), reverse=True)

    return render_template(
        "archive.html",
        sets=all_sets,
        grouped_art=None,
        mode=mode,
        current_sort=sort,
        art_section=ART_SECTION
    )

@app.route("/collections")
def collections_index():
    all_collections = load_all_collections()
    sort = request.args.get("sort")

    if sort == "images":
        all_collections.sort(key=lambda c: c["image_count"], reverse=True)
    elif sort == "random":
        random.shuffle(all_collections)
    elif sort == "recent":
        all_collections.sort(key=lambda c: c["mtime"], reverse=True)
    else:
        # Default: alphabetical
        all_collections.sort(key=lambda c: c["title"].lower())

    return render_template(
        "collections.html",
        collections=all_collections,
        current_sort=sort
    )

@app.route("/collection/<folder>")
def view_collection(folder):
    all_collections = load_all_collections()
    collection = next((c for c in all_collections if c["folder"] == folder), None)

    if not collection:
        return "Collection not found", 404

    # Build full image data for each referenced image
    images = []
    for ref in collection["images"]:
        set_slug = ref.get("set")
        image_file = ref.get("image")
        if set_slug and image_file:
            basename = image_file.rsplit('.', 1)[0]
            images.append({
                "set": set_slug,
                "image": image_file,
                "src": f"sets/{set_slug}/{image_file}",
                "thumb_400": f"sets/{set_slug}/thumbnails/{basename}_thumb_400.jpg",
                "thumb_150": f"sets/{set_slug}/thumbnails/{basename}_thumb_150.jpg",
            })

    return render_template(
        "collection.html",
        collection=collection,
        images=images,
        lightbox_thumbnails=LIGHTBOX_THUMBNAILS
    )

@app.route("/collection/add-image", methods=["POST"])
def collection_add_image():
    data = request.get_json()
    collection_folder = data.get("collection_folder")
    set_slug = data.get("set")
    image = data.get("image")

    if not all([collection_folder, set_slug, image]):
        return jsonify({"error": "Missing data"}), 400

    json_path = os.path.join(COLLECTIONS_DIR, collection_folder, "collection.json")

    if not os.path.exists(json_path):
        return jsonify({"error": "Collection not found"}), 404

    with open(json_path, "r") as f:
        col_data = json.load(f)

    already_exists = any(
        r.get("set") == set_slug and r.get("image") == image
        for r in col_data.get("images", [])
    )

    if not already_exists:
        col_data.setdefault("images", []).append({"set": set_slug, "image": image})

        with open(json_path, "w") as f:
            json.dump(col_data, f, indent=4)

    return jsonify({"success": True})

@app.route("/collection/remove-image", methods=["POST"])
def collection_remove_image():
    data = request.get_json()
    collection_folder = data.get("collection_folder")
    set_slug = data.get("set")
    image = data.get("image")

    if not all([collection_folder, set_slug, image]):
        return jsonify({"error": "Missing data"}), 400

    json_path = os.path.join(COLLECTIONS_DIR, collection_folder, "collection.json")

    if not os.path.exists(json_path):
        return jsonify({"error": "Collection not found"}), 404

    with open(json_path, "r") as f:
        col_data = json.load(f)

    col_data["images"] = [
        r for r in col_data.get("images", [])
        if not (r.get("set") == set_slug and r.get("image") == image)
    ]

    # Delete collection entirely if no images remain
    if not col_data["images"]:
        folder_path = os.path.join(COLLECTIONS_DIR, collection_folder)
        os.remove(json_path)
        os.rmdir(folder_path)
        return jsonify({"success": True, "deleted": True})

    with open(json_path, "w") as f:
        json.dump(col_data, f, indent=4)

    return jsonify({"success": True, "deleted": False})

@app.route("/collection/create", methods=["POST"])
def collection_create():
    data = request.get_json()
    title = data.get("title", "").strip()
    set_slug = data.get("set")
    image = data.get("image")

    if not title or not set_slug or not image:
        return jsonify({"error": "Missing data"}), 400

    slug = slugify(title)
    folder = get_next_collection_folder()
    folder_path = os.path.join(COLLECTIONS_DIR, folder)
    os.makedirs(folder_path)

    col_data = {
        "title": title,
        "slug": slug,
        "cover": {"set": set_slug, "image": image},
        "images": [{"set": set_slug, "image": image}]
    }

    json_path = os.path.join(folder_path, "collection.json")
    with open(json_path, "w") as f:
        json.dump(col_data, f, indent=4)

    return jsonify({"success": True, "folder": folder, "title": title})

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

    # Pass collection folders each image belongs to, for the right-click menu
    all_collections = load_all_collections()
    image_collections = {}
    for collection in all_collections:
        for ref in collection["images"]:
            if ref.get("set") == slug:
                key = ref.get("image")
                if key not in image_collections:
                    image_collections[key] = []
                image_collections[key].append(collection["folder"])

    return render_template(
        "set.html",
        set=image_set,
        lightbox_thumbnails=LIGHTBOX_THUMBNAILS,
        all_collections=all_collections,
        image_collections=image_collections
    )

@app.route("/tag/<tag_name>")
def view_tag(tag_name):
    all_sets = load_all_sets()

    filtered = [
        image_set for image_set in all_sets
        if tag_name in image_set["tags"]
    ]

    filtered.sort(key=lambda image_set: int(image_set["slug"]), reverse=True)

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

    filtered.sort(key=lambda image_set: int(image_set["slug"]), reverse=True)

    return render_template(
        "archive.html",
        sets=filtered,
        filter_type="person",
        filter_value=person_name
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()

    host = '127.0.0.1' if args.debug else '0.0.0.0'
    app.run(host=host, port=5000, debug=args.debug)