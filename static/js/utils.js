// Back to top button
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("back-to-top");
    if (!btn) return;

    // Show button after scrolling down 300px
    window.addEventListener("scroll", function () {
        if (window.scrollY > 300) {
            btn.classList.add("visible");
        } else {
            btn.classList.remove("visible");
        }
    });

    btn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});

// Add Tag / Add Person form toggles on Set Page
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
                if (input) input.focus();
            }
        });
    }

    if (personButton && personForm) {
        personButton.addEventListener("click", function () {
            const isHidden = personForm.style.display === "none" || personForm.style.display === "";
            personForm.style.display = isHidden ? "inline-flex" : "none";
            if (isHidden) {
                const input = personForm.querySelector("input[name='new_person']");
                if (input) input.focus();
            }
        });
    }
});