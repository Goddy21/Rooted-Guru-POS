// operation.js
let cart = [];
let totalAmount = 0.00;
let selectedPaymentMethod = null;

function addToCart() {
    const productCode = document.getElementById('product-code').value.trim();
    if (productCode === '') return;

    // Here, simulate fetching product info (replace with Django AJAX logic later)
    const product = { name: `Product ${productCode}`, price: (Math.random() * 100).toFixed(2) };
    
    // Check if product is already in cart
    let productInCart = cart.find(item => item.name === product.name);
    
    if (productInCart) {
        productInCart.quantity += 1;
        productInCart.total = (productInCart.quantity * productInCart.price).toFixed(2);
    } else {
        cart.push({ ...product, quantity: 1, total: product.price });
    }
    
    updateCartDisplay();
}

function updateCartDisplay() {
    const cartTableBody = document.querySelector('#cart-table tbody');
    cartTableBody.innerHTML = '';
    
    cart.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>${item.price}</td>
            <td>${item.total}</td>
        `;
        cartTableBody.appendChild(row);
    });
    
    totalAmount = cart.reduce((sum, item) => sum + parseFloat(item.total), 0).toFixed(2);
    document.getElementById('total-amount').textContent = totalAmount;
}

function selectPayment(paymentMethod) {
    selectedPaymentMethod = paymentMethod;
    alert(`Selected payment method: ${paymentMethod}`);
}

function completeTransaction() {
    if (!selectedPaymentMethod) {
        alert('Please select a payment method!');
        return;
    }
    
    // Handle transaction completion (e.g., send data to server, clear cart)
    alert(`Transaction complete! Payment method: ${selectedPaymentMethod}\nTotal: $${totalAmount}`);
    cart = [];
    updateCartDisplay();
}

function printReceipt() {
    const receiptContent = document.getElementById('receipt-content').innerText;
    if (!receiptContent.trim()) {
        alert('No items in receipt!');
        return;
    }
    alert(`Printing Receipt:\n\n${receiptContent}`);
}
