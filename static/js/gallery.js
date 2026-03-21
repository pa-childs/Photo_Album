let currentImageIndex = 0;
let galleryImages = [];
let galleryThumbs = [];

// For lightbox
let zoomLevel = 1;
let scrollOffset = 0; // Manual vertical scroll position when zoomed
let isTransitioning = false; // Prevent navigation during animation

// Lightbox functions
function openLightbox(index) {
    currentImageIndex = index;

    const lightbox = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-image");

    // No transition on first open — just show the image
    image.src = galleryImages[currentImageIndex];
    image.style.transform = "";
    image.style.opacity = "1";
    lightbox.style.display = "flex";

    updateCounter();
    updateDownloadLink();
    updateActiveThumbnail();
    preloadAdjacentImages();
}

function closeLightbox() {
    if (document.fullscreenElement) {
        document.exitFullscreen();
    }
    document.getElementById("lightbox").style.display = "none";
    isTransitioning = false;
}

function showNextImage() {
    const nextIndex = (currentImageIndex + 1) % galleryImages.length;
    slideToImage(nextIndex, "next");
}

function showPrevImage() {
    const prevIndex = (currentImageIndex - 1 + galleryImages.length) % galleryImages.length;
    slideToImage(prevIndex, "prev");
}

function slideToImage(newIndex, direction) {
    if (isTransitioning || newIndex === currentImageIndex) return;
    isTransitioning = true;

    const current = document.getElementById("lightbox-image");
    const incoming = document.getElementById("lightbox-image-incoming");

    // Reset zoom and scroll for the transition
    // zoomLevel = 1;
    // scrollOffset = 0;

    // Position incoming image off-screen in the correct direction
    const startX = direction === "next" ? "100%" : "-100%";
    const exitX = direction === "next" ? "-100%" : "100%";

    incoming.src = galleryImages[newIndex];
    incoming.style.transition = "none";
    incoming.style.transform = `translateX(${startX})`;
    incoming.style.opacity = "1";

    // Force reflow so the initial position is applied before animating
    incoming.getBoundingClientRect();

    // Animate both images simultaneously
    const duration = "300ms";
    const easing = "ease";

    current.style.transition = `transform ${duration} ${easing}, opacity ${duration} ${easing}`;
    incoming.style.transition = `transform ${duration} ${easing}, opacity ${duration} ${easing}`;

    current.style.transform = `translateX(${exitX})`;
    current.style.opacity = "0";
    incoming.style.transform = "translateX(0)";
    incoming.style.opacity = "1";

    incoming.addEventListener("transitionend", function onEnd() {
        incoming.removeEventListener("transitionend", onEnd);

        // Swap — make incoming the new current
        current.src = galleryImages[newIndex];
        current.style.transition = "none";
        current.style.transform = `translateY(${scrollOffset}px) scale(${zoomLevel})`;
        current.style.opacity = "1";

        // Reset incoming back off-screen ready for next transition
        incoming.style.transition = "none";
        incoming.style.transform = "translateX(100%)";
        incoming.style.opacity = "0";
        incoming.src = "";

        currentImageIndex = newIndex;
        isTransitioning = false;

        updateCounter();
        updateDownloadLink();
        updateActiveThumbnail();
        preloadAdjacentImages();
    }, { once: true });

    // Update index immediately for counter/download during transition
    currentImageIndex = newIndex;
    updateCounter();
    updateDownloadLink();
    updateActiveThumbnail();
}

function applyTransform(img) {
    img.style.transform = `translateY(${scrollOffset}px) scale(${zoomLevel})`;
}

function zoomImage(delta) {
    const img = document.getElementById("lightbox-image");
    zoomLevel += delta;
    if (zoomLevel < 1) zoomLevel = 1;
    if (zoomLevel > 5) zoomLevel = 5;

    // Reset scroll offset when zooming back to 1
    if (zoomLevel === 1) scrollOffset = 0;

    applyTransform(img);
}

function scrollImage(delta) {
    // Only scroll if zoomed in
    if (zoomLevel <= 1) return;

    const img = document.getElementById("lightbox-image");

    // Calculate how far the image extends beyond the viewport vertically
    const imgHeight = img.getBoundingClientRect().height;
    const viewportHeight = window.innerHeight;
    const maxScroll = Math.max(0, (imgHeight - viewportHeight) / 2);

    scrollOffset -= delta * 0.5;
    scrollOffset = Math.max(-maxScroll, Math.min(maxScroll, scrollOffset));

    applyTransform(img);
}

// Image counter
function updateCounter() {
    const counter = document.getElementById("lightbox-counter");
    if (counter) {
        counter.textContent = `${currentImageIndex + 1} of ${galleryImages.length}`;
    }
}

// Download button - points to current full-size image
function updateDownloadLink() {
    const link = document.getElementById("lightbox-download");
    if (link) {
        const src = galleryImages[currentImageIndex];
        link.href = src;
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

// Preload the full-size images immediately before and after the current one
function preloadAdjacentImages() {
    const indices = [
        (currentImageIndex - 1 + galleryImages.length) % galleryImages.length,
        (currentImageIndex + 1) % galleryImages.length
    ];
    indices.forEach(i => {
        const pre = new Image();
        pre.src = galleryImages[i];
    });
}

// Thumbnail strip - uses 150px thumbnails
function buildThumbnails() {
    const strip = document.getElementById("lightbox-thumbnails");
    if (!strip) return;

    strip.innerHTML = "";

    galleryThumbs.forEach((src, index) => {
        const thumb = document.createElement("img");
        thumb.src = src;
        thumb.className = "lightbox-thumb";
        thumb.addEventListener("click", (e) => {
            e.stopPropagation();
            const direction = index > currentImageIndex ? "next" : "prev";
            slideToImage(index, direction);
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
    const incoming = document.getElementById("lightbox-image-incoming");

    // Set incoming image off-screen initially
    if (incoming) {
        incoming.style.transform = "translateX(100%)";
        incoming.style.opacity = "0";
    }

    const galleryEls = Array.from(document.querySelectorAll(".gallery-image"));

    // Full-size paths for the lightbox main image and preloading
    galleryImages = galleryEls.map(img => img.dataset.src);

    // 150px thumbnail paths for the lightbox strip
    galleryThumbs = galleryEls.map(img => img.dataset.thumb);

    // Build thumbnail strip once on load
    buildThumbnails();

    if (img) {
        // Lightbox close button
        document.querySelector(".lightbox-close").addEventListener("click", closeLightbox);

        // Navigation buttons
        document.querySelector(".lightbox-next").addEventListener("click", showNextImage);
        document.querySelector(".lightbox-prev").addEventListener("click", showPrevImage);

        // Close on background click
        document.getElementById("lightbox").addEventListener("click", (e) => {
            if (e.target.id === "lightbox" || e.target.classList.contains("lightbox-image-area")) {
                closeLightbox();
            }
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

        // Ctrl+scroll to zoom, scroll alone scrolls the image vertically
        document.getElementById("lightbox").addEventListener("wheel", (e) => {
            e.preventDefault();
            if (e.ctrlKey) {
                zoomImage(e.deltaY < 0 ? 0.1 : -0.1);
            } else {
                scrollImage(e.deltaY);
            }
        }, { passive: false });
    }

});