from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
#from .models import Profile, Product
from .models import User, Product, Order, Profile
from django.db import IntegrityError
from django.contrib.auth.models import User
from datetime import date
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.utils import timezone
from escpos.printer import Usb


# Index view
def index(request):
    return render(request, 'index.html')

# Registration view
def register(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        designation = request.POST['designation']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists!')
                return redirect('register')
            else:
                try:
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )

                    # Create Profile
                    profile, created = Profile.objects.get_or_create(user=user)
                    profile.designation = designation
                    profile.save()

                    messages.success(request, 'Registration successful! Please log in.')
                    return redirect('login')

                except IntegrityError as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                    return redirect('register')

        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

    return render(request, 'register.html')

# Login view
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # Fetch user profile and handle designation
            try:
                profile = user.profile
                designation = profile.designation.lower() if profile.designation else None
            except Profile.DoesNotExist:
                designation = None

            if designation == 'administrator':
                return redirect('admin_dashboard')
            elif designation == 'operator':
                return redirect('operation')
            else:
                messages.warning(request, 'Designation not assigned. Please contact the admin.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid Username or Password')
            return redirect('login')

    return render(request, 'login.html')


# Logout view
def logout(request):
    auth_logout(request)
    request.session.flush()  # Clear all session data
    return redirect('/')

# Admin dashboard view
from django.shortcuts import render
from .models import User, Product, Order

def admin_dashboard(request):
    # Fetch all users, products, and orders from the database
    users = User.objects.all()
    products = Product.objects.all()
    recent_orders = Order.objects.filter(order_date__gte='2024-11-01')  # Adjust the date range accordingly
    total_sales = sum(order.total_price for order in recent_orders)

    # Debugging step: Check if products and users have valid IDs and names
    for product in products:
        print(f"Product ID: {product.id}, Product Name: {product.name}")
    
    for user in users:
        print(f"User ID: {user.id}, User Name: {user.username}")

    # Prepare the context to pass to the template
    context = {
        'users': users,
        'products': products,
        'recent_orders': recent_orders,
        'total_sales': total_sales,
    }

    # Render the admin dashboard template with the context
    return render(request, 'admin_dashboard.html', context)

# Add user
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        designation = request.POST['designation']

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
        else:
            # Create the user with first_name and last_name
            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=first_name, last_name=last_name)
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.designation = designation
            profile.save()

            messages.success(request, f'User "{username}" added successfully!')
            return redirect('admin_dashboard')

    return render(request, 'add_user.html')


# Update user view
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.profile.designation = request.POST.get('designation', user.profile.designation)
        user.save()
        user.profile.save()

        messages.success(request, f'User "{user.username}" updated successfully!')
        return redirect('admin_dashboard')

    return render(request, 'admin_dashboard.html', {'user': user})

# Delete user view
def delete_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user_to_delete = User.objects.get(username=username)
            user_to_delete.delete()
            messages.success(request, f'User "{username}" deleted successfully!')
        except User.DoesNotExist:
            messages.error(request, f'User "{username}" not found!')
        return redirect('admin_dashboard')
    return render(request, 'admin_dashboard.html')

# Add product
def add_product(request):
    if request.method == 'POST':
        product_code = request.POST['product_code']
        name = request.POST['name']
        price = float(request.POST['price'])
        product_weight = request.POST['product_weight']
        description = request.POST.get('description', '')
        stock_level = int(request.POST['stock_level'])
        sales_count = 0  # Default sales count to 0 when product is added
        order_received = request.POST.get('order', None)
        last_purchase = request.POST.get('last_purchase', None)
        ordered = request.POST.get('ordered', None)

        # Parse the dates if provided
        if order_received:
            order_received = date.fromisoformat(order_received)
        if last_purchase:
            last_purchase = date.fromisoformat(last_purchase)
        if ordered:
            ordered = date.fromisoformat(ordered)

        # Create the product
        Product.objects.create(
            product_code=product_code,
            name=name,
            price=price,
            product_weight=product_weight,
            description=description,
            stock_level=stock_level,
            sales_count=sales_count,
            order_received=order_received,
            last_purchase=last_purchase,
            ordered=ordered,
        )
        messages.success(request, f'Product "{name}" added successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'add_product.html')

def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        data = {
            "success": True,
            "product": {
                "product_code": product.product_code,
                "name": product.name,
                "product_weight": product.product_weight,
                "price": product.price,
                "stock_level": product.stock_level,
                "sales_count": product.sales_count,
                "order_received": product.order_received,
                "last_purchase": product.last_purchase.isoformat() if product.last_purchase else None,
                "ordered": product.ordered,
            },
        }
    except Product.DoesNotExist:
        data = {"success": False, "error": "Product not found."}
    
    return JsonResponse(data)

#Update Product
def update_product(request, product_id):
    if request.method == "POST":
        try:
            product = Product.objects.get(id=product_id)
            product.product_code = request.POST.get("product_code")
            product.name = request.POST.get("name")
            product.product_weight = request.POST.get("product_weight")
            product.price = request.POST.get("price")
            product.stock_level = request.POST.get("stock_level")
            product.sales_count = request.POST.get("sales_count")
            product.order_received = request.POST.get("order_received")
            product.last_purchase = request.POST.get("last_purchase")
            product.ordered = request.POST.get("ordered")
            product.save()
            messages.success(request, "Product updated successfully.")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
    return redirect("admin_dashboard")

# Delete Product
def delete_product(request):
    if request.method == 'POST':
        product_code = request.POST.get('product_code')  # Get the product code from the form

        try:
            # Find the product by its product code
            product = Product.objects.get(product_code=product_code)  # Assuming 'product_code' is the field used for identification
            product_name = product.name
            product.delete()  # Delete the product

            messages.success(request, f'Product "{product_name}" removed successfully!')
        except Product.DoesNotExist:
            messages.error(request, 'Product with that code does not exist!')

        return redirect('admin_dashboard')  # Redirect back to the admin dashboard after deletion

    # If it's not a POST request, simply redirect to the admin dashboard
    return redirect('admin_dashboard')







@csrf_protect
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_code = data.get('product_code')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        if not product_code:
            return JsonResponse({'status': 'error', 'message': 'Product code is required'}, status=400)

        try:
            product = Product.objects.get(product_code=product_code)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        cart = request.session.get('cart', [])
        total_amount = request.session.get('total_amount', 0.0)

        # Update the cart
        for item in cart:
            if item['product_code'] == product.product_code:
                item['quantity'] += 1
                item['total'] = round(item['quantity'] * float(product.price), 2)
                break
        else:  # If no break occurred
            cart.append({
                'product_code': product.product_code,
                'name': product.name,
                'price': float(product.price),
                'weight': product.product_weight,
                'description': product.description,
                'stock_level': product.stock_level,
                'sales_count': product.sales_count,
                'order_date': product.order_received.isoformat() if product.order_received else None,
                'last_purchase_date': product.last_purchase.isoformat() if product.last_purchase else None,
                'quantity': 1,
                'total': float(product.price),
            })

        total_amount = round(sum(item['total'] for item in cart), 2)
        request.session['cart'] = cart
        request.session['total_amount'] = total_amount

        return JsonResponse({'status': 'success', 'cart': cart, 'total_amount': total_amount})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_protect
def select_payment(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        print("Payment Method Selected:", payment_method)  # Debug log
        if payment_method:
            request.session['payment_method'] = payment_method
            #messages.success(request, f'Payment method selected: {payment_method}')
        #else:
            #messages.error(request, 'No payment method selected! Please try again.')
    return redirect('operation')

@csrf_protect
def operation(request):
    if request.user.is_authenticated and request.user.profile.designation == 'operator':
        cart = request.session.get('cart', [])
        total_amount = request.session.get('total_amount', 0.0)
        payment_method = request.session.get('payment_method', None)
        receipt_number = request.session.get('receipt_number', "N/A")
        receipt_time = request.session.get('receipt_time', "N/A")

        context = {
            'cart': cart,
            'total_amount': total_amount,
            'payment_method': payment_method,
            'receipt_number': receipt_number,
            'receipt_time': receipt_time,
        }
        return render(request, 'operation.html', context)
    return redirect('login')

@csrf_protect
def complete_transaction(request):
    if request.method == 'POST':
        # Get the payment method from the request body (JSON)
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        if not payment_method:
            return JsonResponse({'status': 'error', 'message': 'Please select a payment method first.'})

        # Proceed with the transaction logic
        receipt_number = str(uuid.uuid4())[:8]
        current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        request.session['receipt_number'] = receipt_number
        request.session['receipt_time'] = current_time
        request.session['cart'] = []
        request.session['total_amount'] = 0.0
        request.session.pop('payment_method', None)  # Optionally clear the session payment method after use

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def print_receipt(request):
    if request.method == "POST":
        try:
            # Replace with your USB printer details
            printer = Usb(0x04b8, 0x0202)

            # Example receipt content
            receipt_content = [
                "Rooted Guru Point Of Sale System",
                "Tel: (+254)-7266-100-18",
                f"Receipt No: {request.session.get('receipt_number', 'N/A')}",
                f"Date: {request.session.get('receipt_time', 'N/A')}",
                "\nItems:\n",
            ]

            
            cart = request.session.get("cart", [])
            for item in cart:
                receipt_content.append(
                    f"{item['name']} x{item['quantity']} - ${item['total']:.2f}"
                )
            receipt_content.append(f"\nTotal: ${request.session.get('total_amount', 0):.2f}")

            # Print receipt
            for line in receipt_content:
                printer.text(line + "\n")

            printer.cut()  # Cut the receipt
            return JsonResponse({"status": "success", "message": "Receipt printed successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error printing receipt: {str(e)}"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)