let currentImageIndex = 0;
let currentSet = null;
let allSets = [];
let activeTag = null;

// For lightbox
let zoomLevel = 1;
let panX = 0;
let panY = 0;
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;

// Helper: create a single set card
function createSetCard(set) {
    const card = document.createElement("div");
    card.className = "set-card";

    // Preview image
    const img = document.createElement("img");
    img.src = set.preview_image || "";
    img.alt = set.title;
    card.appendChild(img);

    // Title
    const title = document.createElement("h2");
    title.textContent = set.title;
    card.appendChild(title);

    // Tags (optional)
    if (set.tags && set.tags.length > 0) {
        const tags = document.createElement("p");
        tags.textContent = set.tags.join(", ");
        card.appendChild(tags);
    }

    // Click handler
    card.addEventListener("click", () => {
        loadSet(set.id);
    });

    return card;
}

// Render sets
function renderSets(sets) {
    const container = document.getElementById("sets-container");
    container.innerHTML = ""; // clear existing content

    sets.forEach(set => {
        const card = createSetCard(set);
        container.appendChild(card);
    });
}

function renderSetImages(set) {
    const setsContainer = document.getElementById("sets-container");
    const imagesContainer = document.getElementById("images-container");
    const tagFilters = document.getElementById("tag-filters");
    const setTags = document.getElementById("set-tags");
    const title = document.getElementById("page-title");

    // Hide sets grid and global tags
    setsContainer.style.display = "none";
    tagFilters.style.display = "none";
    tagFilters.innerHTML = "";

    // Show images grid and set-specific tags
    imagesContainer.style.display = "grid";
    setTags.style.display = "flex";

    // Update title
    title.textContent = set.title;

    // Clear previous content
    imagesContainer.innerHTML = "";
    setTags.innerHTML = "";

    // Render set tags
    renderSetTags(set.tags);

    // Back button (in header, not grid)
    const controls = document.getElementById("set-controls");
    controls.innerHTML = "";

    const backBtn = document.createElement("button");
    backBtn.className = "back-button";
    backBtn.textContent = "Return to Archive";
    backBtn.onclick = showSets;

controls.appendChild(backBtn);

    // Render images
    set.images.forEach((url, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "image-thumb";

        const img = document.createElement("img");
        img.src = url;
        img.alt = `${set.title} ${index + 1}`;

        wrapper.appendChild(img);

        wrapper.addEventListener("click", () => {
            openLightbox(index);
        });

        imagesContainer.appendChild(wrapper);
    });

    // Update active tag highlighting only for visible tags
    updateActiveTag();
}

function renderSetTags(tags) {
    const container = document.getElementById("set-tags");
    container.innerHTML = "";

    if (!tags || tags.length === 0) return;

    tags.forEach(tag => {
        const el = document.createElement("span");
        el.className = "tag";
        el.textContent = tag;
        container.appendChild(el);
    });
}

function showSets() {
    const setsContainer = document.getElementById("sets-container");
    const imagesContainer = document.getElementById("images-container");
    const tagFilters = document.getElementById("tag-filters");
    const setTags = document.getElementById("set-tags");

    setsContainer.style.display = "grid";
    imagesContainer.style.display = "none";

    tagFilters.style.display = "flex";  // show global tags
    renderTagFilters(allSets);           // re-render global tags

    setTags.style.display = "none";     // hide set tags
    setTags.innerHTML = "";             // clear set tags

    document.getElementById("sets-container").style.display = "grid";
    document.getElementById("images-container").style.display = "none";
    document.getElementById("page-title").textContent = "Image Archive";

    document.getElementById("tag-filters").style.display = "block";
    document.getElementById("set-tags").innerHTML = "";
    document.getElementById("set-controls").innerHTML = "";

    updateActiveTag();
}


// Fetch sets from API
fetch("/api/sets")
    .then(res => res.json())
    .then(data => {
        allSets = data;
        renderTagFilters(allSets);
        renderSets(allSets);
        activeTag = null;
        updateActiveTag();
    })
    .catch(err => console.error("Failed to load sets:", err));

function loadSet(setId) {
    fetch(`/api/sets/${setId}`)
        .then(res => res.json())
        .then(set => {
            currentSet = set;
            renderSetImages(set);
        })
        .catch(err => console.error("Failed to load set:", err));
}

// Lightbox functions
function openLightbox(index) {
    currentImageIndex = index;

    const lightbox = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-image");

    image.src = currentSet.images[currentImageIndex];
    lightbox.style.display = "flex";
}

function closeLightbox() {
    document.getElementById("lightbox").style.display = "none";
}

function showNextImage() {
    currentImageIndex =
        (currentImageIndex + 1) % currentSet.images.length;
    updateLightboxImage();
}

function showPrevImage() {
    currentImageIndex =
        (currentImageIndex - 1 + currentSet.images.length) %
        currentSet.images.length;
    updateLightboxImage();
}

function updateLightboxImage() {
    const img = document.getElementById("lightbox-image");
    img.src = currentSet.images[currentImageIndex];

    // Reset zoom & pan
    zoomLevel = 1;
    panX = 0;
    panY = 0;
    img.style.transform = `translate(0px, 0px) scale(1)`;
}

function zoomImage(delta) {
    const img = document.getElementById("lightbox-image");
    zoomLevel += delta;
    if (zoomLevel < 1) zoomLevel = 1; // prevent negative zoom
    if (zoomLevel > 5) zoomLevel = 5; // optional max zoom
    img.style.transform = `translate(${panX}px, ${panY}px) scale(${zoomLevel})`;
}

function renderTagFilters(sets) {
    const container = document.getElementById("tag-filters");
    container.innerHTML = "";

    const tags = new Set();

    sets.forEach(set => {
        (set.tags || []).forEach(tag => tags.add(tag));
    });

    // "All" button
    const allBtn = createTagButton("All", null);
    container.appendChild(allBtn);

    tags.forEach(tag => {
        container.appendChild(createTagButton(tag, tag));
    });
}

function createTagButton(label, tagValue) {
    const btn = document.createElement("div");
    btn.className = "tag";
    btn.textContent = label;

    btn.addEventListener("click", () => {
        activeTag = tagValue;
        updateActiveTag();
        filterSets();
    });

    return btn;
}

function filterSets() {
    if (!activeTag) {
        renderSets(allSets);
        return;
    }

    const filtered = allSets.filter(set =>
        (set.tags || []).includes(activeTag)
    );

    renderSets(filtered);
}

function updateActiveTag() {
    // Global tags
    const tagFilters = document.getElementById("tag-filters");
    if (tagFilters.style.display !== "none") {
        const globalTags = tagFilters.querySelectorAll(".tag");
        globalTags.forEach(tag => tag.classList.remove("active"));
        globalTags.forEach(tag => {
            if ((activeTag === null && tag.textContent === "All") || tag.textContent === activeTag) {
                tag.classList.add("active");
            }
        });
    }

    // Set tags
    const setTags = document.getElementById("set-tags");
    if (setTags.style.display !== "none") {
        const tags = setTags.querySelectorAll(".tag");
        tags.forEach(tag => tag.classList.remove("active"));
        tags.forEach(tag => {
            if (activeTag && tag.textContent === activeTag) {
                tag.classList.add("active");
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const img = document.getElementById("lightbox-image");

    // Start dragging
    img.addEventListener("mousedown", (e) => {
        isDragging = true;
        dragStartX = e.clientX - panX;
        dragStartY = e.clientY - panY;
        img.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        panX = e.clientX - dragStartX;
        panY = e.clientY - dragStartY;
        img.style.transform = `translate(${panX}px, ${panY}px) scale(${zoomLevel})`;
    });

    document.addEventListener("mouseup", () => {
        isDragging = false;
        img.style.cursor = "grab";
    });

    // Lightbox close button
    document.querySelector(".lightbox-close").addEventListener("click", closeLightbox);

    // Navigation buttons
    document.querySelector(".lightbox-next").addEventListener("click", showNextImage);
    document.querySelector(".lightbox-prev").addEventListener("click", showPrevImage);

    // Close on background click
    document.getElementById("lightbox").addEventListener("click", (e) => {
        if (e.target.id === "lightbox") closeLightbox();
    });

    // Keyboard controls
    document.addEventListener("keydown", (e) => {
        const lightbox = document.getElementById("lightbox");
        if (lightbox.style.display !== "flex") return;

        if (e.key === "Escape") closeLightbox();
        if (e.key === "ArrowRight") showNextImage();
        if (e.key === "ArrowLeft") showPrevImage();
    });

    // Wheel for zoom
    document.getElementById("lightbox").addEventListener("wheel", (e) => {
        e.preventDefault();
        zoomImage(e.deltaY < 0 ? 0.1 : -0.1);
    });
});

