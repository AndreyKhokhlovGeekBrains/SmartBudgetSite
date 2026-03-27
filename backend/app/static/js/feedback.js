document.addEventListener("DOMContentLoaded", () => {
    const texts = window.feedbackTexts;

    const form = document.getElementById("feedback-form");
    const status = document.getElementById("feedback-status");

    const typeSelect = document.getElementById("message_type");
    const emailInput = document.getElementById("email");
    const emailLabel = document.querySelector('label[for="email"]');
    const emailHint = document.getElementById("email-hint");

    const purchaseStatus = document.getElementById("purchase-status");

    const subjectGroup = document.getElementById("subjectGroup");
    const messageGroup = document.getElementById("messageGroup");

    const purchaseSelectorGroup = document.getElementById("purchaseSelectorGroup");
    const purchaseSelect = document.getElementById("purchase_select");
    const purchasePlaceholderText = purchaseSelect.options[0].text;

    const submitButton = form.querySelector('button[type="submit"]');

    const contactEmailGroup = document.getElementById("contactEmailGroup");
    const contactEmailInput = document.getElementById("contact_email");

    const messageInput = document.getElementById("message");
    const messageCounter = document.getElementById("messageCounter");

    function updateEmailVisibility() {
        const type = typeSelect.value;

        if (type === "product_feedback") {
            emailLabel.style.display = "block";
            emailInput.style.display = "block";
            emailHint.style.display = "block";
            emailInput.required = true;

            contactEmailGroup.style.display = "none";
            contactEmailInput.required = false;
            contactEmailInput.value = "";
        } else {
            emailLabel.style.display = "none";
            emailInput.style.display = "none";
            emailHint.style.display = "none";
            emailInput.required = false;
            emailInput.value = "";

            contactEmailGroup.style.display = "block";
            contactEmailInput.required = false;
        }
    }

    function updateSubmitState() {
        const type = typeSelect.value;

        if (type !== "product_feedback") {
            submitButton.disabled = false;
            return;
        }

        const hasVerifiedPurchase =
            purchaseStatus.classList.contains("success") && !!purchaseSelect.value;

        submitButton.disabled = !hasVerifiedPurchase;
    }

    function updateFormVisibility(isVisible) {
        if (isVisible) {
            subjectGroup.style.display = "block";
            messageGroup.style.display = "block";
        } else {
            subjectGroup.style.display = "none";
            messageGroup.style.display = "none";
        }

        updateSubmitState();
    }

    async function updatePurchaseStatus() {
        purchaseStatus.style.display = "none";
        purchaseStatus.textContent = "";
        purchaseStatus.className = "feedback-purchase-status";

        purchaseSelectorGroup.style.display = "none";

        const type = typeSelect.value;
        const email = emailInput.value.trim().toLowerCase();

        if (type !== "product_feedback") {
            purchaseStatus.style.display = "none";
            purchaseStatus.textContent = "";
            purchaseStatus.className = "feedback-purchase-status";

            purchaseSelectorGroup.style.display = "none";
            purchaseSelect.innerHTML = `<option value="">${purchasePlaceholderText}</option>`;

            updateFormVisibility(true);
            return;
        }

        if (!email) {
            purchaseStatus.style.display = "none";
            purchaseStatus.textContent = "";
            purchaseStatus.className = "feedback-purchase-status";

            purchaseSelectorGroup.style.display = "none";
            purchaseSelect.innerHTML = `<option value="">${purchasePlaceholderText}</option>`;

            updateFormVisibility(false);
            return;
        }

        purchaseStatus.style.display = "block";
        purchaseStatus.className = "feedback-purchase-status";
        purchaseStatus.textContent = texts.checkingPurchase;

        try {
            const response = await fetch("/v1/check-purchase", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email
                }),
            });

            if (!response.ok) {
                throw new Error("Purchase check failed");
            }

            const result = await response.json();

            if (result.verified) {
                purchaseStatus.style.display = "block";
                purchaseStatus.className = "feedback-purchase-status success";
                purchaseStatus.textContent = texts.purchaseConfirmed;

                purchaseSelect.innerHTML = `<option value="">${purchasePlaceholderText}</option>`;

                result.purchases.forEach((p) => {
                    const option = document.createElement("option");
                    option.value = p.sale_id;

                    const purchaseDate = p.created_at
                        ? new Date(p.created_at).toLocaleDateString()
                        : "";

                    option.textContent =
                        `${p.product_name || texts.productFallback}${p.edition ? " (" + p.edition + ")" : ""}` +
                        `${purchaseDate ? " — " + purchaseDate : ""}`;

                    purchaseSelect.appendChild(option);
                });

                purchaseSelectorGroup.style.display = "block";

                if (result.purchases.length === 1) {
                    purchaseSelect.value = String(result.purchases[0].sale_id);
                    updateFormVisibility(true);
                    subject.focus();
                } else {
                    updateFormVisibility(false);
                }
            } else {
                purchaseStatus.style.display = "block";
                purchaseStatus.className = "feedback-purchase-status error";
                purchaseStatus.textContent = texts.noPurchaseFound;

                purchaseSelectorGroup.style.display = "none";
                purchaseSelect.innerHTML = `<option value="">${purchasePlaceholderText}</option>`;

                updateFormVisibility(false);
            }
        } catch (error) {
            console.error("CHECK PURCHASE ERROR:", error);

            purchaseStatus.style.display = "block";
            purchaseStatus.className = "feedback-purchase-status error";
            purchaseStatus.textContent = texts.purchaseCheckFailed;

            purchaseSelectorGroup.style.display = "none";
            purchaseSelect.innerHTML = `<option value="">${purchasePlaceholderText}</option>`;

            updateFormVisibility(false);
        }
    }

    updateEmailVisibility();
    updatePurchaseStatus();
    updateSubmitState();

    emailInput.addEventListener("blur", updatePurchaseStatus);

    emailInput.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            await updatePurchaseStatus();
            emailInput.blur();
        }
    });

    if (messageInput && messageCounter) {
        const maxLength = messageInput.maxLength;

        const updateCounter = () => {
            const currentLength = messageInput.value.length;
            messageCounter.textContent = `${currentLength} / ${maxLength}`;
        };

        messageInput.addEventListener("input", updateCounter);

        updateCounter(); // ← важно: инициализация при загрузке
    }

    typeSelect.addEventListener("change", () => {
        updateEmailVisibility();
        updatePurchaseStatus();
    });

    purchaseSelect.addEventListener("change", () => {
        if (purchaseSelect.value) {
            updateFormVisibility(true);
            subject.focus();
        } else {
            updateFormVisibility(false);
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        status.textContent = texts.sending;
        status.className = "feedback-form__status";

        const payload = {
            message_type: form.message_type.value,
            name: form.name.value || null,
            email: form.email.value || "",
            subject: form.subject.value,
            message: form.message.value,
            page_url: form.page_url.value || window.location.pathname,
            sale_id: form.purchase_select.value ? Number(form.purchase_select.value) : null,
        };

        try {
            const response = await fetch("/v1/feedback", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error("Request failed");
            }

            const result = await response.json();

            status.textContent = `${texts.sentSuccessPrefix} ${result.id}`;
            status.className = "feedback-form__status feedback-form__status--success";

            form.reset();
            form.page_url.value = window.location.pathname;

            purchaseSelectorGroup.style.display = "none";
            purchaseSelect.innerHTML = `<option value="">${purchasePlaceholderText}</option>`;

            purchaseStatus.style.display = "none";
            purchaseStatus.textContent = "";
            purchaseStatus.className = "feedback-purchase-status";

            updateFormVisibility(false);
            updateEmailVisibility();
            updateSubmitState();
        } catch (error) {
            status.textContent = texts.sendFailed;
            status.className = "feedback-form__status feedback-form__status--error";
        }
    });
});