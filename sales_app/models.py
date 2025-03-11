from django.db import models
from django.utils.timezone import now
import random, string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('rejected', 'Rejected'),
    ]

    id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')  # Lead status
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"


class Opportunity(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE)

    # Allow fields to be blank/null to prevent migration errors
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    converted_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Opportunity - {self.name}"


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255)  # Store hashed password
    # converted_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def __str__(self):
        return f"Customer - {self.name}"

#quotation model
class Quotation(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Quotation Sent'),
        ('confirmed', 'Quotation Confirmed'),
        ('cancelled', 'Quotation Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    def save(self, *args, **kwargs):
        # Check if the status is being changed to "Confirmed"
        if self.pk is not None:
            orig = Quotation.objects.get(pk=self.pk)
            if orig.status != 'Confirmed' and self.status == 'confirmed':
                # Create SalesOrder automatically
                from .models import SalesOrder  # Import inside to avoid circular import
                SalesOrder.objects.create(
                    quotation_id=self,
                    customer=self.customer,
                    customer_name=self.customer.name,
                    order_date=now(),
                    total_amount=self.amount * self.quantity,
                    status='Pending',
                    payment_status='Pending'
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quotation {self.id} - {self.customer.name}"
 
#admin model
class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
#sales order model
class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In-process','In-process'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    order_id = models.AutoField(primary_key=True)  # Auto-incremented order ID
    quotation_id = models.ForeignKey('Quotation', on_delete=models.CASCADE)  # Reference to Quotation
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)  # Reference to Customer
    customer_name = models.CharField(max_length=255)  # Storing customer name separately
    order_date = models.DateTimeField(default=now)  # Order confirmation date
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total order amount
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)  # Order status
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)  # Payment status

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
    
    @property
    def product_name(self):
        return self.quotation_id.product_name  # Fetch product from quotation


class Payment(models.Model):
    order = models.ForeignKey('SalesOrder', on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.status}"
    
class ReturnOrder(models.Model):
    RETURN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Refunded', 'Refunded'),
    ]

    order = models.ForeignKey('SalesOrder', on_delete=models.CASCADE, related_name='returns')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE,default=1) 
    return_reason = models.TextField()
    status = models.CharField(max_length=10, choices=RETURN_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Return for Order {self.order.order_id} - {self.status}"