// For lightbox
let zoomLevel = 1;
let panX = 0;
let panY = 0;
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;

let galleryImages = [];

// Lightbox functions
function openLightbox(index) {
    currentImageIndex = index;

    const lightbox = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-image");

    image.src = galleryImages[currentImageIndex];
    lightbox.style.display = "flex";
}

function closeLightbox() {
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
}

function zoomImage(delta) {
    const img = document.getElementById("lightbox-image");
    zoomLevel += delta;
    if (zoomLevel < 1) zoomLevel = 1; // prevent negative zoom
    if (zoomLevel > 5) zoomLevel = 5; // optional max zoom
    img.style.transform = `translate(${panX}px, ${panY}px) scale(${zoomLevel})`;
}

document.addEventListener("DOMContentLoaded", () => {

    const img = document.getElementById("lightbox-image");

    galleryImages = Array.from(document.querySelectorAll(".gallery-image"))
        .map(img => img.src);

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
    }

});

