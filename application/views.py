from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Product,Order, OrderItem,Supplier
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.db.models import Q
import pprint
# Create your views here.




@login_required
@staff_member_required
def admin_dashboard(request):
   
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    orders = Order.objects.all().order_by('-created_at')[:10]  

    context = {
        'suppliers': suppliers,
        'products': products,
        'orders': orders,
     
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@staff_member_required
def approve_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.is_approved = True
    supplier.save()
    return redirect('admin_dashboard')

@login_required
@staff_member_required
def deactivate_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.is_approved = False
    supplier.save()
    return redirect('admin_dashboard')

@login_required
@staff_member_required
def delete_product_admin(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_dashboard')

@staff_member_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('admin_dashboard')

def home(request):
    return render(request, 'home.html' ,{'Product':Product})




#this is for reginstration
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
             messages.info(request, "email already exist.")
             return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "username already exist.")
                return redirect('register')
            else:
                user = User.objects.create_user(username=username , email=email, password=password )
                user.save();
                return redirect('login')
        else:
            messages.info(request, 'password not the same')
            return redirect('register')
    else:
        return render(request, 'register.html')
    



def supplier_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        company_name = request.POST.get('company_name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        if password==password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('supplier_register')
            else:
                user = User.objects.create_user(username=username, password=password)
                Supplier.objects.create(
                user=user,
                company_name=company_name,
                contact_number=contact_number,
                address=address,
                is_approved=False, 
            )
            messages.success(request, 'Registration successful! Wait for admin approval.')
            return redirect('login') 
        else:
            return render(request, 'supplier_register')
    return render(request, 'supplier_register.html')



def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            
            if Supplier.objects.filter(user=user).exists():
                auth_login(request, user) 
                return redirect('supplier_dashboard')
            else:
                auth_login(request,user)
                return redirect('product_list')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')



@login_required
def supplier_dashboard(request):
    try:
        supplier = request.user.supplier
    except Supplier.DoesNotExist:
        return HttpResponse("You are not a supplier.")

    if not supplier.is_approved:
        return HttpResponse("Your account is pending admin approval.")

    # Start with all products for this supplier
    products = Product.objects.filter(supplier=supplier)

    # Filtering
    status = request.GET.get('status')
    if status == 'active':
        products = products.filter(status=True)
    elif status == 'inactive':
        products = products.filter(status=False)

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'name':
        products = products.order_by('name')

    return render(request, 'supplier_dashboard.html', {
        'products': products,
        'status': status,
        'sort_by': sort_by,
    })

@login_required
def add_product(request):
    # Ensure the user is a supplier
    try:
        supplier = request.user.supplier
    except Supplier.DoesNotExist:
        return HttpResponse("Access denied: Only suppliers can add products.")

    if request.method == 'POST':
        # Get form data directly
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')  # For file uploads

        # Basic validation
        if not all([name, description, price, stock]):
            return render(request, 'add_product.html', {'error': 'All fields except image are required.'})

        # Convert price and stock to proper types
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            return render(request, 'add_product.html', {'error': 'Price must be a number and stock an integer.'})

        # Create and save the product
        Product.objects.create(
            supplier=supplier,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )
        return redirect('add_product')  # Replace with your actual redirect

    return render(request, 'add_product.html')


@login_required
def delete_product(request, product_id):
    try:
        supplier = request.user.supplier
    except Supplier.DoesNotExist:
        return HttpResponse("Access denied.")

    product = get_object_or_404(Product, id=product_id, supplier=supplier)
    product.delete()
    return redirect('supplier_dashboard')



@login_required
def edit_product(request, product_id):
    try:
        supplier = request.user.supplier
        user = request.user.is_staff
    except Supplier.DoesNotExist and not user:
        return HttpResponse("Access denied.")

    product = get_object_or_404(Product, id=product_id, supplier=supplier)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        image = request.FILES.get('image')

        if image:
            product.image = image

        product.save()
        return redirect('supplier_dashboard')

    return render(request, 'edit_product.html', {'product': product})




    # for login 


    



#this tis for logout
def logout(request):
    auth.logout(request)
    return redirect('/')



# --- 2. Product List ---
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'Product': products})



#this is for product details
def product_detail(request, pk):
    products = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': products})



# --- 4. Add to Cart ---
def add_to_cart(request, pk):
    products = get_object_or_404(Product, id=pk)
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    pid = str(products.id)
    if pid in cart:
        cart[pid]['quantity'] += quantity
    else:
        cart[pid] = {
            'name': products.name,
            'price': float(products.price),
            'quantity': quantity,
            'image': products.image.url
        }

    request.session['cart'] = cart
    pprint.pprint(request.session['cart'])
    messages.success(request, "Product added to cart.")
    return redirect('cart')



# this is for about
def about(request):
    return render(request, 'about-us-page.html')




def cart(request):
    session_cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for pid, item in session_cart.items():
        try:
            products = Product.objects.get(pk=pid)
            quantity = item['quantity']
            item_total = products.price * quantity
            cart_items.append({
                'pk': pid,
                'product': products,  # the actual Product object
                'quantity': quantity,
                'total_price': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            continue  # if product was deleted, skip

    context = {
        'cart': {
            'items': cart_items,
            'total': total
        },
        'cart_item_count': sum(item['quantity'] for item in session_cart.values())
    }
    return render(request, 'cart.html', context)




# ---  Update Cart ---
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for pid in cart.keys():
            qty = request.POST.get(f'quantities_{pid}')
            if qty:
                cart[pid]['quantity'] = int(qty)
        request.session['cart'] = cart
        messages.success(request, "Cart updated.")
    return redirect('cart')




# --- Remove from Cart ---
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
        messages.success(request, "Item removed.")
    return redirect('cart')

def checkout(request):
    return render(request, 'checkout.html')




# --- Process Checkout ---

def process_checkout(request):
    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        payment_method = request.POST['payment_method']
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, "Cart is empty.")
            return redirect('cart')

        total = sum(item['price'] * item['quantity'] for item in cart.values())

        # Save Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            address=address,
            payment_method=payment_method,
            total=total
        )

        # Save OrderItems
        for item in cart.values():
            product = Product.objects.get(name=item['name'])  # safer to use id if available
            OrderItem.objects.create(
                 order=order,
                 product=product,
                 product_name=item['name'],
                 price=item['price'],
                 quantity=item['quantity']
    )

        # Clear cart
        request.session['cart'] = {}
        messages.success(request, "Order placed successfully.")
        return redirect('order_confirmation')

    return redirect('checkout')




# ---  Order Confirmation ---
def order_confirmation(request):
    return render(request, 'order_confirmation.html')


#thi is to see the past orderd hestory
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'my_orders.html', {'orders': orders})

def delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('my_orders')


def product_search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'product_search.html', {'products': results, 'query': query})