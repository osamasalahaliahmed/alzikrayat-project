function validateField(field) {
    field.setCustomValidity("");

    if (field.type === "hidden") {
        return;
    }
    if (field.required && !field.value.trim()) {
        field.setCustomValidity("Please fill in this field.");
    }
    if (field.name === "first_name" || field.name === "last_name") {
        if (field.value && !/^[\p{L}]+$/u.test(field.value.trim())) {
            field.setCustomValidity("Use letters only.");
        }
    }
    if (field.type === "email" && field.value) {
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value.trim())) {
            field.setCustomValidity("Enter a valid email address.");
        }
    }
    if (field.name === "confirm_password") {
        if (field.value !== field.form.elements.password.value) {
            field.setCustomValidity("The passwords do not match.");
        }
    }
    if (field.type === "file" && field.files.length > 0) {
        const file = field.files[0];
        if (file.type && !file.type.startsWith("image/")) {
            field.setCustomValidity("Choose an image.");
        }
    }
}

async function saveComment(form) {
    const button = form.querySelector("button[type=submit]");
    const message = form.querySelector(".form-error");
    if (button.disabled) {
        return;
    }

    button.disabled = true;
    message.textContent = "Saving your comment…";

    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: "POST",
            headers: {"Accept": "application/json"},
            body: new URLSearchParams(formData),
        });
        const result = await response.json();

        if (!response.ok) {
            message.textContent = result.error || "Your comment could not be saved.";
            return;
        }

        document.getElementById("comment-list").innerHTML = result.html;
        form.elements.comment.value = "";
        form.elements.comment.focus();
        message.textContent = "Comment added.";
    } catch (error) {
        message.textContent = "Connection lost. Refresh to check whether your comment was saved before trying again.";
    } finally {
        button.disabled = false;
    }
}

for (const form of document.querySelectorAll("form[data-validate]")) {
    const fields = form.querySelectorAll("input, textarea");

    for (const field of fields) {
        field.addEventListener("input", function () {
            validateField(field);
            if (field.name === "password" && form.elements.confirm_password) {
                validateField(form.elements.confirm_password);
            }
        });
        field.addEventListener("change", function () {
            validateField(field);
        });
    }

    form.addEventListener("submit", function (event) {
        for (const field of fields) {
            validateField(field);
        }

        if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
            return;
        }

        if (form.hasAttribute("data-comment-form")) {
            event.preventDefault();
            saveComment(form);
        }
    });
}

const layoutButtons = document.querySelectorAll("[data-layout]");
for (const button of layoutButtons) {
    button.addEventListener("click", function () {
        const gallery = document.getElementById("gallery");
        gallery.style.setProperty("--columns", button.dataset.layout);

        for (const otherButton of layoutButtons) {
            otherButton.setAttribute("aria-pressed", String(otherButton === button));
        }
    });
}
