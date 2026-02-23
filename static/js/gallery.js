let currentImageIndex = 0;
let galleryImages = [];

// For lightbox
let dragStartX = 0;
let dragStartY = 0;
let isDragging = false;
let panX = 0;
let panY = 0;
let zoomLevel = 1;

// Lightbox functions
function openLightbox(index) {
    currentImageIndex = index;

    const lightbox = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-image");

    image.src = galleryImages[currentImageIndex];
    lightbox.style.display = "flex";

    updateCounter();
    updateDownloadLink();
    updateActiveThumbnail();
}

function closeLightbox() {
    // Exit fullscreen if active when closing
    if (document.fullscreenElement) {
        document.exitFullscreen();
    }
    document.getElementById("lightbox").style.display = "none";
}

function showNextImage() {
    currentImageIndex =
        (currentImageIndex + 1) % galleryImages.length;
    updateLightboxImage();
}

function showPrevImage() {
    currentImageIndex =
        (currentImageIndex - 1 + galleryImages.length) %
        galleryImages.length;
    updateLightboxImage();
}

function updateLightboxImage() {
    const img = document.getElementById("lightbox-image");
    img.src = galleryImages[currentImageIndex];

    // Reset zoom & pan
    zoomLevel = 1;
    panX = 0;
    panY = 0;
    img.style.transform = `translate(0px, 0px) scale(1)`;

    updateCounter();
    updateDownloadLink();
    updateActiveThumbnail();
}

function zoomImage(delta) {
    const img = document.getElementById("lightbox-image");
    zoomLevel += delta;
    if (zoomLevel < 1) zoomLevel = 1;
    if (zoomLevel > 5) zoomLevel = 5;

    // Reset pan if zoomed back to 1
    if (zoomLevel === 1) {
        panX = 0;
        panY = 0;
    }

    img.style.transform = `translate(${panX}px, ${panY}px) scale(${zoomLevel})`;
}

// Image counter
function updateCounter() {
    const counter = document.getElementById("lightbox-counter");
    if (counter) {
        counter.textContent = `${currentImageIndex + 1} of ${galleryImages.length}`;
    }
}

// Download button - points to current image
function updateDownloadLink() {
    const link = document.getElementById("lightbox-download");
    if (link) {
        const src = galleryImages[currentImageIndex];
        link.href = src;
        // Use the filename from the path as the download name
        link.download = src.split("/").pop();
    }
}

// Fullscreen toggle
function toggleFullscreen() {
    const lightbox = document.getElementById("lightbox");
    if (!document.fullscreenElement) {
        lightbox.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

// Thumbnail strip
function buildThumbnails() {
    const strip = document.getElementById("lightbox-thumbnails");
    if (!strip) return;

    strip.innerHTML = "";

    galleryImages.forEach((src, index) => {
        const thumb = document.createElement("img");
        thumb.src = src;
        thumb.className = "lightbox-thumb";
        thumb.addEventListener("click", (e) => {
            e.stopPropagation();
            currentImageIndex = index;
            updateLightboxImage();
        });
        strip.appendChild(thumb);
    });
}

function updateActiveThumbnail() {
    const thumbs = document.querySelectorAll(".lightbox-thumb");
    thumbs.forEach((thumb, index) => {
        thumb.classList.toggle("lightbox-thumb-active", index === currentImageIndex);
    });

    // Scroll the active thumbnail into view within the strip
    if (thumbs[currentImageIndex]) {
        thumbs[currentImageIndex].scrollIntoView({
            behavior: "smooth",
            block: "nearest",
            inline: "center"
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const img = document.getElementById("lightbox-image");

    galleryImages = Array.from(document.querySelectorAll(".gallery-image"))
        .map(img => img.src);

    // Build thumbnail strip once on load
    buildThumbnails();

    if (img) {
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

        // Fullscreen button
        document.getElementById("lightbox-fullscreen").addEventListener("click", (e) => {
            e.stopPropagation();
            toggleFullscreen();
        });

        // Keyboard controls
        document.addEventListener("keydown", (e) => {
            const lightbox = document.getElementById("lightbox");
            if (lightbox.style.display !== "flex") return;

            if (e.key === "Escape") closeLightbox();
            if (e.key === "ArrowRight") showNextImage();
            if (e.key === "ArrowLeft") showPrevImage();
            if (e.key === "f" || e.key === "F") toggleFullscreen();
        });

        // Wheel for zoom
        document.getElementById("lightbox").addEventListener("wheel", (e) => {
            e.preventDefault();
            zoomImage(e.deltaY < 0 ? 0.1 : -0.1);
        });
    }

});

// Add Tag Button on Set Page
document.addEventListener("DOMContentLoaded", function () {
    const tagButton = document.getElementById("add-tag-button");
    const tagForm = document.getElementById("add-tag-form");
    const personButton = document.getElementById("add-person-button");
    const personForm = document.getElementById("add-person-form");

    if (tagButton && tagForm) {
        tagButton.addEventListener("click", function () {

            const isHidden = tagForm.style.display === "none" || tagForm.style.display === "";

            tagForm.style.display = isHidden ? "inline-flex" : "none";

            if (isHidden) {
                const input = tagForm.querySelector("input[name='new_tag']");
                if (input) {
                    input.focus();
                }
            }
        });
    }

    if (personButton && personForm) {
        personButton.addEventListener("click", function () {

            const isHidden = personForm.style.display === "none" || personForm.style.display === "";

            personForm.style.display = isHidden ? "inline-flex" : "none";

            if (isHidden) {
                const input = personForm.querySelector("input[name='new_person']");
                if (input) {
                    input.focus();
                }
            }
        });
    }
});