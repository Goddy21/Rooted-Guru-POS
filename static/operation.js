document.addEventListener("DOMContentLoaded", () => {
    let cart = [];
    let totalAmount = 0.0;
    let selectedPaymentMethod = null;

    const completeTransactionBtn = document.querySelector("#complete-transaction-btn");
    const paymentMethodSelect = document.querySelector("#payment-method"); // Dropdown for selecting payment method
    const cartTableBody = document.querySelector("#cart tbody");
    const receiptContent = document.querySelector("#receipt-content");
    const printReceiptBtn = document.querySelector("#print-receipt-btn");

    completeTransactionBtn.disabled = true; // Disable transaction button initially

    // Enable transaction button upon selecting a payment method
    paymentMethodSelect.addEventListener("change", (event) => {
        selectedPaymentMethod = event.target.value; // Get selected payment method
        completeTransactionBtn.disabled = !selectedPaymentMethod; // Enable button if a method is selected
    });

    // Fetch CSRF token
    function getCookie(name) {
        const cookies = document.cookie.split(";").map(cookie => cookie.trim());
        const target = cookies.find(cookie => cookie.startsWith(`${name}=`));
        return target ? decodeURIComponent(target.split("=")[1]) : null;
    }

    // Add product to cart
    async function addToCart(event) {
        event.preventDefault();
        const productCode = document.getElementById("product-code").value.trim();

        if (!productCode) {
            alert("Please enter a product code.");
            return;
        }

        try {
            const response = await fetch("/operation/add-to-cart/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ product_code: productCode }),
            });

            if (response.ok) {
                const data = await response.json();
                cart = data.cart;
                totalAmount = data.total_amount;
                updateCartDisplay(cart, totalAmount);
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.message}`);
            }
        } catch (error) {
            console.error("Fetch error:", error);
            alert("An unexpected error occurred. Please try again.");
        }
    }

    // Update cart display
    function updateCartDisplay(cart, totalAmount) {
        cartTableBody.innerHTML = cart.length
            ? cart.map(item => `
                <tr>
                    <td>${item.product_code}</td>
                    <td>${item.name}</td>
                    <td>${item.price.toFixed(2)}</td>
                    <td>${item.weight}</td>
                    <td>${item.description}</td>
                    <td>${item.stock_level}</td>
                    <td>${item.sales_count}</td>
                    <td>${item.order_date || ""}</td>
                    <td>${item.last_purchase_date || ""}</td>
                    <td>${item.quantity}</td>
                    <td>${item.total.toFixed(2)}</td>
                </tr>
            `).join("")
            : "<tr><td colspan='11'>No items in the cart.</td></tr>";

        document.getElementById("total-amount").textContent = totalAmount.toFixed(2);
    }

    // Clear receipt preview
    function clearReceiptPreview() {
        receiptContent.innerHTML = `
            <h3>Rooted Guru Point Of Sale System</h3>
            <h3>Tel: (+254)-7266-100-18</h3>
            <p>No receipt available</p>`;
        cartTableBody.innerHTML = "<tr><td colspan='11'>No items in the cart.</td></tr>"; // Clear cart display
        document.getElementById("total-amount").textContent = "0.00"; // Reset total amount
    }

 
    paymentMethodSelect.addEventListener("change", (event) => {
        selectedPaymentMethod = event.target.value; // Get selected payment method
        console.log("Selected Payment Method:", selectedPaymentMethod); // Debugging line
        completeTransactionBtn.disabled = !selectedPaymentMethod; // Enable button if a method is selected
    });
        
    async function completeTransaction(event) {
        event.preventDefault();
        console.log("Transaction initiated");
        console.log("Payment method being sent:", selectedPaymentMethod); // Debugging line
        
        try {
            const response = await fetch("/operation/complete-transaction/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    payment_method: selectedPaymentMethod || "" // Ensure this value is not empty
                }),
            });
        
            console.log("Response received:", response);
            const data = await response.json();
            console.log("Data received:", data);
        
            if (data.status === "success") {
                alert("Transaction completed successfully!");
                //clearReceiptPreview(); // Clear receipt and cart
                cart = [];
                totalAmount = 0.0;
            } else {
                alert(`Error: ${data.message}`);
            }
            } catch (error) {
                console.error("Fetch error:", error);
                alert("An unexpected error occurred. Please try again.");
            }
    }
        

    async function printReceipt(event) {
        event.preventDefault();
    
        try {
            const response = await fetch("/operation/print-receipt/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            });
    
            if (response.ok) {
                const data = await response.json();
                if (data.status === "success") {
                    alert("Receipt printed successfully!");
                    clearReceiptPreview(); // Clear receipt and cart after successful printing
                } else {
                    alert(`Error printing receipt: ${data.message}`);
                }
            } else {
                const errorText = await response.text(); // Get HTML error content
                console.error("Error response:", errorText);
                alert("An error occurred while printing the receipt.");
            }
        } catch (error) {
            console.error("Print receipt error:", error);
            alert("An unexpected error occurred while printing the receipt.");
        }
    }
     
    // Attach the function to the button
    document.getElementById("print-receipt-btn").addEventListener("click", printReceipt);
    
    // Event listeners
    document.getElementById("product-form").addEventListener("submit", addToCart);
    completeTransactionBtn.addEventListener("click", completeTransaction);
    printReceiptBtn.addEventListener("click", printReceipt);
});
