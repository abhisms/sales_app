from django.contrib import admin
from .models import Lead, Opportunity, Customer  # Import your models

admin.site.register([Customer, Lead, Opportunity])
