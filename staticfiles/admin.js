// Function to toggle dropdown menu visibility
function toggleDropdown() {
    document.getElementById("dropdown").classList.toggle("show");
}

// Function to show a specific section and hide others
function showSection(sectionId) {
    const sections = document.querySelectorAll('.admin-section');
    sections.forEach(section => section.style.display = 'none');
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    } else {
        console.error(`Section with ID '${sectionId}' not found.`);
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "block";
        console.log(`${modalId} modal opened`); // Debugging line
    } else {
        console.error(`Modal with ID '${modalId}' not found.`);
    }
}

// Function to close a modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    } else {
        console.error(`Modal with ID '${modalId}' not found.`);
    }
}

// Close the modal when clicking outside of it
window.onclick = function (event) {
    const modals = document.querySelectorAll(".modal");
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
};

document.getElementById("product_id").addEventListener("change", function() {
    var productId = this.value;
    if (productId) {
        // Update the form action URL with the selected product ID
        const formAction = "{% url 'update_product' 'product_id' %}".replace('product_id', productId);
        document.getElementById("product-selection-form").action = formAction;
    }
});

// Optional: Close modals when pressing the Escape key
window.onkeydown = function (event) {
    if (event.key === "Escape") {
        const modals = document.querySelectorAll(".modal");
        modals.forEach(modal => {
            if (modal.style.display === "block") {
                modal.style.display = "none";
            }
        });
    }
};

document.addEventListener("DOMContentLoaded", function () {
    const userSelect = document.getElementById("user");
    const userDetails = document.getElementById("user-details");
    const form = userDetails.querySelector("form");

    if (userSelect) {
        userSelect.addEventListener("change", function () {
            const userId = this.value;

            if (userId) {
                form.action = `/dashboard/update_user/${userId}/`; // Update the form action
                userDetails.style.display = "block";
            } else {
                userDetails.style.display = "none"; // Hide the user details form
            }
        });
    } else {
        console.error("#user element not found.");
    }

    if (!userDetails) {
        console.error("#user-details element not found.");
    }
});


