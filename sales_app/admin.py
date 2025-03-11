from django.contrib import admin
from .models import Lead, Opportunity, Customer,Quotation,Admin,SalesOrder,Payment,ReturnOrder  # Import your models

admin.site.register([Customer, Lead, Opportunity,Quotation,Admin,SalesOrder,Payment,ReturnOrder])
