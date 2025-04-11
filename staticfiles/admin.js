// Function to toggle dropdown menu visibility
function toggleDropdown() {
    document.getElementById("dropdown").classList.toggle("show");
}

// Function to show a specific section and hide others
function showSection(sectionId) {
    const sections = document.querySelectorAll('.admin-section');
    sections.forEach(section => section.style.display = 'none');
    
    // Hide the dashboard-info section when a button is clicked
    const dashboardInfo = document.querySelector('.dashboard-info');
    if (dashboardInfo) {
        dashboardInfo.style.display = 'none';
    }

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    } else {
        console.error(`Section with ID '${sectionId}' not found.`);
    }
}

// Function to open a modal
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

// DOMContentLoaded event to initialize user and product selection logic
document.addEventListener("DOMContentLoaded", function () {
    // Product selection logic (for updating product details)
    const productSelect = document.getElementById("product_id");
    const productDetails = document.getElementById("product-details");
    const updateProductForm = document.getElementById("update-product-form");

    if (productSelect) {
        productSelect.addEventListener("change", function () {
            const productId = this.value;

            if (productId) {
                // Fetch product details via an API or pre-loaded context
                fetch(`/dashboard/get_product/${productId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Populate form fields with product data
                            document.getElementById("product_code").value = data.product.product_code;
                            document.getElementById("name").value = data.product.name;
                            document.getElementById("product_weight").value = data.product.product_weight;
                            document.getElementById("price").value = data.product.price;
                            document.getElementById("stock_level").value = data.product.stock_level;
                            document.getElementById("sales_count").value = data.product.sales_count;
                            document.getElementById("order").value = data.product.order;
                            document.getElementById("last_purchase").value = data.product.last_purchase;
                            document.getElementById("ordered").value = data.product.ordered;

                            // Update form action dynamically
                            updateProductForm.action = `/dashboard/update_product/${productId}/`;
                            productDetails.style.display = "block";
                        } else {
                            console.error("Failed to fetch product details.");
                        }
                    })
                    .catch(error => console.error("Error fetching product details:", error));
            } else {
                productDetails.style.display = "none";
            }
        });
    } else {
        console.error("#product_id element not found.");
    }

    // User selection logic (for updating user details)
    const userSelect = document.getElementById("user");
    const userDetails = document.getElementById("user-details");
    const updateUserForm = document.getElementById("update-user-form");

    if (userSelect) {
        userSelect.addEventListener("change", function () {
            const userId = this.value;

            if (userId) {
                // Update the form action dynamically with the selected user ID
                updateUserForm.action = `/dashboard/update_user/${userId}/`;
                userDetails.style.display = "block";  // Show the user details form
            } else {
                userDetails.style.display = "none";  // Hide the user details form if no user is selected
            }
        });
    } else {
        console.error("#user element not found.");
    }

    if (!userDetails) {
        console.error("#user-details element not found.");
    }

    if (!updateUserForm) {
        console.error("#update-user-form element not found.");
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
