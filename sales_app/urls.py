from django.urls import path
from .import views
from sales_app.views import (
    lead_form,
    lead_list,
    update_lead_status,
    opportunity_list,
    opportunities_list,
    convert_opportunity,
    customer_login,
    customer_dashboard,
    customer_logout,
    create_quotation,
    admin_home,
    view_quotations,
    update_quotation,
    cancel_quotation,
    update_quotation_status,
    admin_view_orders,
    update_order_status,
    verify_payment,
    initiate_payment,
    track_orders,
    generate_invoice,
    return_order,
    update_return_status
)

urlpatterns = [
    path("sales/lead-form/", lead_form, name="lead_form"),
    path("sales/leads/", lead_list, name="lead_list"),
    path("sales/update-lead-status/", update_lead_status, name="update_lead_status"),
    path("sales/opportunities/", opportunity_list, name="opportunity_list"),
    path("sales/opportunities_list/", opportunities_list, name="opportunities_list"),
    path("sales/convert_opportunity/<int:opportunity_id>/", convert_opportunity, name="convert_opportunity"),
    path('sales/login/', customer_login, name='customer_login'),
    path('sales/dashboard/', customer_dashboard, name='customer_dashboard'),
    path('sales/logout/', customer_logout, name='customer_logout'),
    path('create-quotation/', create_quotation, name='create_quotation'),
    path('admin_home/', admin_home, name='admin_home'),
    path('view-quotation/', view_quotations, name='view_quotations'),
    path('admin_register/', views.admin_register, name='admin_register'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('update-quotation/<int:quotation_id>/', update_quotation, name='update_quotation'),
    path('cancel_quotation/<int:quotation_id>/', cancel_quotation, name='cancel_quotation'),
    path('quotations/confirm/<int:quotation_id>/', views.confirm_quotation, name='confirm_quotation'),
    path('quotations/update/<int:quotation_id>/', update_quotation_status, name='update_quotation_status'),
    # path('update-payment/<int:order_id>/', update_payment_status, name='update_payment_status'),
    path('view-orders/', admin_view_orders, name='admin_view_orders'),
    path('update-order-status/', update_order_status, name='update_order_status'),
    path("initiate-payment/<int:order_id>/", initiate_payment, name="initiate_payment"),
    path("verify-payment/", verify_payment, name="verify_payment"),
    path('track-orders/', track_orders, name='track_orders'),
    path('download-invoice/<int:order_id>/', generate_invoice, name='download_invoice'),
    path('return-order/<int:order_id>/', return_order, name='return_order'),
    path('return_orders_list/', views.return_orders_list, name='return_orders_list'),
    path('update_return_status/<int:return_id>/', update_return_status, name='update_return_status'),
]







