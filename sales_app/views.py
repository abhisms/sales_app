from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import random
import string
from django.http import HttpResponse
from .models import Lead, Opportunity, Customer, Quotation
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import authenticate, login, logout
from .forms import QuotationForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import Admin, SalesOrder, Payment, ReturnOrder
from django.contrib import messages
from django.utils import timezone
import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

#admin home
def admin_home(request):
    return render(request, 'sales/admin_home.html')


def lead_form(request):
    success = False  # Default no message

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        company = request.POST.get("company")
        location = request.POST.get("location")

        # Save lead to database
        Lead.objects.create(name=name, email=email, phone=phone, company=company, location=location)

        success = True  # Form submitted successfully

    return render(request, "sales/lead_form.html", {"success": success})

def lead_list(request):
    leads = Lead.objects.all()  # Fetch all leads
    return render(request, "sales/lead_list.html", {"leads": leads})

def update_lead_status(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        new_status = request.POST.get("new_status")

        lead = get_object_or_404(Lead, id=lead_id)
        lead.status = new_status
        lead.save()

        # If converted, copy data to Opportunity table
        if new_status == "converted":
            Opportunity.objects.get_or_create(
                lead=lead,
                defaults={
                    "name": lead.name,
                    "email": lead.email,
                    "phone": lead.phone,
                    "company": lead.company,
                    "location": lead.location,
                    "converted_at": now(),
                }
            )

        return JsonResponse({
            "message": "Status updated successfully!",
            "new_status": new_status
        })
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def opportunity_list(request):
    opportunities = Opportunity.objects.all()
    return render(request, "sales/opportunity_list.html", {"opportunities": opportunities})

def opportunities_list(request):
    opportunities = Opportunity.objects.all()
    converted_customers = Customer.objects.values_list('email', flat=True)  # Get emails of converted customers
    return render(request, 'sales/opportunity_list.html', {'opportunities': opportunities, 'converted_customers': converted_customers})

def generate_random_password(length=8):
    """Generate a random password with letters, digits, and special characters."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))

def convert_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)

    # Check if the opportunity is already converted by checking in Customer table
    if Customer.objects.filter(email=opportunity.email).exists():
        return HttpResponse("Already converted", status=400)

    # Generate a random password
    password = generate_random_password()

    # Create a new customer from the opportunity details with the generated password
    customer = Customer.objects.create(
        name=opportunity.name,
        email=opportunity.email,
        phone=opportunity.phone,
        company=opportunity.company,
        location=opportunity.location,
        password=make_password(password),  # Assuming your Customer model has a 'password' field
        # converted_at=now()
    )

    # Send an email notification with the password
   # Send an email notification only to the receiver (opportunity.email)
      # Send login credentials via email
    send_mail(
    subject="Welcome to Our Company!",
    message=f"""Dear {opportunity.name},

Your opportunity has been successfully converted into a customer account!

Here are your login credentials:

🔹 **Username**: {opportunity.email}  
🔹 **Password**: {password}  

You can log in to your customer portal here:  
🔗 [Login Now](http://127.0.0.1:8000/sales/login/)

Best regards,  
Your Company Team
""",
    from_email="yourcompany@example.com",
    recipient_list=[opportunity.email],  
    fail_silently=False,
)


    return redirect('opportunities_list')  # Redirect back to the opportunities page

 #customer login function
def customer_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                request.session['customer_id'] = customer.id  # Store session
                return redirect('customer_dashboard')
            else:
                return render(request, "sales/login.html", {"error": "Invalid password"})
        except Customer.DoesNotExist:
            return render(request, "sales/login.html", {"error": "User not found"})

    return render(request, "sales/login.html")

#customer dashboard
def customer_dashboard(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)
    returns = ReturnOrder.objects.filter(customer=customer)
    quotations = Quotation.objects.filter(customer=customer)  # Fetch quotations for logged-in customer
    orders = SalesOrder.objects.filter(customer_id=customer,quotation_id__status="confirmed")# Corrected customer filter

   
    return render(request, "sales/customer_dash.html", {
        "customer": customer,
        "quotations": quotations,
        "orders": orders,
        "returns":returns
    })

#customer logout
def customer_logout(request):
    request.session.flush()
    return redirect('customer_login')


#quotation view admin
def view_quotations(request):
    quotations = Quotation.objects.all()  # Fetch all quotations
    return render(request, 'sales/view_quotation.html', {'quotations': quotations})

#create quotation
def create_quotation(request):
    customers = Customer.objects.all()  # Fetch all customers for dropdown

    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            quotation = form.save()  # Save the form and get the quotation instance

            # Send email to the customer
            send_quotation_email(quotation)

            messages.success(request, "Quotation submitted successfully!")
            return redirect('admin_home')  # Redirect after submission

    else:
        form = QuotationForm()

    return render(request, 'sales/quotation.html', {'form': form, 'customers': customers})


def send_quotation_email(quotation):
    """Sends an email to the customer when a quotation is created."""
    customer_email = quotation.customer.email  # Assuming the Customer model has an 'email' field
    subject = "New Quotation Created - Action Required"
    message = f"""
    Dear {quotation.customer.name},

    A new quotation has been created for you.

    **Quotation Details:**
    - Product: {quotation.product_name}
    - Quantity: {quotation.quantity}
    - Price: {quotation.amount}
    - Expiry Date: {quotation.expiry_date}

    You can confirm or cancel the quotation by logging in to your customer portal.

    🔗 [Login Now](http://127.0.0.1:8000/sales/login/)

    Best regards,  
    Your Sales Team
    """

    send_mail(
        subject,
        message,
        "abhism574@gmail.com", 
        [customer_email],
        fail_silently=False,
    )


#update quotation in customer dashboard
def update_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)

    # Check if the quotation is expired
    if quotation.expiry_date and quotation.expiry_date < now().date():
        # print(now().date())
        quotation.status = "cancelled"
        quotation.save()
        return redirect("customer_dashboard")  # Redirect without confirming

    if request.method == "POST":
        # Update status to 'confirmed' when Yes is clicked, only if not expired
        quotation.status = "confirmed"
        quotation.save()

    return redirect("customer_dashboard")

#cancel quotation
def cancel_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    quotation.status = 'cancelled'
    quotation.save()
    return redirect('customer_dashboard')  # Redirect after cancellation

#confirm quotation
def confirm_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)

    # Check if the quotation has expired
    if quotation.expiry_date < timezone.now().date():
        quotation.status = 'cancelled'  # Auto-cancel if expired
        quotation.save()
        return redirect('customer_dashboard')

    # If not expired, confirm the quotation
    quotation.status = 'confirmed'
    quotation.save()

    # # Check if a SalesOrder already exists for this quotation
    # if not SalesOrder.objects.filter(quotation_id=quotation).exists():
    #     # Create a new SalesOrder
    #     SalesOrder.objects.create(
    #         order_id=f"ORD{quotation.id}",  # Generate unique order ID
    #         customer_id=quotation.customer,
    #         quotation_id=quotation,
    #         total_amount=quotation.amount * quotation.quantity,
    #         status='Pending',
    #         payment_status='Pending'
    #     )

    return redirect('customer_dashboard')  # Redirect after processing

#create sales order
def create_sales_order(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id, status='Confirmed')
    
    # Creating a new sales order
    sales_order = SalesOrder.objects.create(
        quotation_id=quotation,
        customer_id=quotation.customer_id,
        customer_name=quotation.customer_id.name,  # Assuming customer model has a 'name' field
        order_date=now(),
        total_amount=quotation.amount * quotation.quantity,  # Assuming amount is per unit
        status='Pending',
        payment_status='Pending'
    )
    
    return redirect('customer_dashboard')  # Redirecting to customer dashboard after order creation

#update_quotation_status by admin
def update_quotation_status(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)

    if request.method == "POST":
        quotation.status = request.POST.get("status")
        quotation.save()
    
    return redirect('view_quotations')

# admin user model, login, registration, dashboard
# Admin Registration
def admin_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        
        if Admin.objects.filter(email=email).exists():
            return render(request, 'sales/admin_register.html', {'error': 'Email already exists'})

        hashed_password = make_password(password)
        Admin.objects.create(name=name, email=email, password=hashed_password)
        return redirect('admin_login')

    return render(request, 'sales/admin_register.html')

# Admin Login
def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        admin = Admin.objects.filter(email=email).first()
        if admin and check_password(password, admin.password):
            request.session['admin_id'] = admin.id  # Store session
            return redirect('admin_dashboard')
        
        return render(request, 'sales/admin_login.html', {'error': 'Invalid credentials'})

    return render(request, 'sales/admin_login.html')

# Admin Dashboard
def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    return render(request, 'sales/admin_home.html')

# Admin Logout
def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')

#update payment status
# def update_payment_status(request, order_id):
#     order = get_object_or_404(SalesOrder, order_id=order_id)
#     if request.method == "POST":
#         order.payment_status = "Pending"  # Change status to pending after clicking 'Done'
#         order.save()
#         messages.success(request, "Payment marked as Pending. Admin will verify it soon.")
#     return redirect('customer_dashboard')

#admin view sales order
def admin_view_orders(request):
    orders = SalesOrder.objects.all()
    return render(request, "sales/view_sales_order.html", {"orders": orders})

#admin update sales and payment status

def update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")

        # Ensure required data is present
        if not order_id or not new_status:
            return HttpResponseBadRequest("Invalid request: Missing order_id or status")

        # Fetch the order and update the status
        order = get_object_or_404(SalesOrder, order_id=order_id)
        order.status = new_status
        order.save()

        return redirect('admin_view_orders')  # Ensure this matches your URL name

    return HttpResponseBadRequest("Invalid request method")

#razor pay integration functions

#initiate payment
def initiate_payment(request, order_id):
    order = get_object_or_404(SalesOrder, order_id=order_id)


    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment_data = {
        "amount": int(order.total_amount * 100),  # Convert to paise
        "currency": "INR",
        "receipt": f"order_{order.order_id}",
        "payment_capture": "1"
    }
    
    razorpay_order = client.order.create(data=payment_data)

    payment = Payment.objects.create(
        order=order,
        razorpay_order_id=razorpay_order['id'],
        amount=order.total_amount
    )

    # Ensure values are sent to template
    return render(request, "sales/payment_page.html", {
        "order": order,
        "payment": payment,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID
    })

#verify payment
@csrf_exempt
def verify_payment(request):
    import json
    if request.method == "POST":
        data = json.loads(request.body)
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature(data)

            # Update payment status
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "Paid"
            payment.save()

            # Update order payment status
            payment.order.payment_status = "Paid"
            payment.order.save()

            return JsonResponse({"status": "success"})
        except Payment.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "Payment not found"})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "failed", "error": "Invalid signature"})
        except Exception as e:
            return JsonResponse({"status": "failed", "error": str(e)})


#Track orders
def track_orders(request):
    user_email = request.user.email  # Get logged-in user's email

    try:
        # Get the Customer object that matches the logged-in user's email
        customer = Customer.objects.get(email=user_email)  

        # Fetch only the orders where this customer is linked and payment status is "Paid"
        orders = SalesOrder.objects.filter(customer=customer, payment_status="Paid")

        status_steps = ["Pending", "In-process", "Shipped", "Delivered", "Cancelled"]

        for order in orders:
            if order.status == 'Pending':
                order.progress_percentage = 25
            elif order.status == 'Processing':
                order.progress_percentage = 50
            elif order.status == 'Shipped':
                order.progress_percentage = 75
            elif order.status == 'Delivered':
                order.progress_percentage = 100
            else:
                order.progress_percentage = 0  # Default case


    except Customer.DoesNotExist:
        # If no matching customer is found, return no orders
        orders = []

    return render(request, 'sales/customer_dash.html', {
        'orders': orders,
        "status_steps": status_steps,
        
        })


#download invoice
def generate_invoice(request, order_id):
    order = get_object_or_404(SalesOrder, order_id=order_id)
    payment = Payment.objects.filter(order=order).first()  # Get related payment details

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Invoice Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Invoice")

    # Order Details
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Order ID: {order.order_id}")
    p.drawString(50, height - 120, f"Customer: {order.customer_name}")
    p.drawString(50, height - 140, f"Order Date: {order.order_date.strftime('%Y-%m-%d')}")
    p.drawString(50, height - 160, f"Status: {order.status}")

    # Payment Details
    if payment:
        p.drawString(50, height - 200, f"Payment Status: {payment.status}")
        p.drawString(50, height - 220, f"Paid Amount: Rs.{payment.amount}")
        p.drawString(50, height - 240, f"Transaction ID: {payment.razorpay_payment_id or 'N/A'}")

    # Total Amount
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 280, f"Total Amount: Rs.{order.total_amount}")

    p.showPage()
    p.save()

    return response

#return order
def return_order(request, order_id):
    order = get_object_or_404(SalesOrder, order_id=order_id)

    if order.status == "Delivered":  # Ensure only delivered orders can be returned
        # Update order status to Cancelled
        order.status = "Cancelled"
        order.save()

        # Create a new row in the ReturnOrder model
        ReturnOrder.objects.create(
            order=order,  # Assuming there is a ForeignKey to SalesOrder
            customer=order.customer,
            return_reason="Customer requested return",  # Modify as needed
            status="Pending",  # Initial status of return request
            created_at=now()
        )

        messages.success(request, "Your return request has been submitted successfully.")
    else:
        messages.error(request, "Only delivered orders can be returned.")

    return redirect('customer_dashboard')

def return_orders_list(request):
    returns = ReturnOrder.objects.all()  # Fetch all return orders
    return render(request, 'sales/return_orders.html', {'returns': returns})

def update_return_status(request, return_id):
    if request.method == "POST":
        return_order = get_object_or_404(ReturnOrder, id=return_id)
        new_status = request.POST.get("status")

        # Update the return order status
        return_order.status = new_status
        return_order.save()

        messages.success(request, "Return order status updated successfully!")
    
    return redirect('return_orders_list')


