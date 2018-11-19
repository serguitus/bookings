from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^quote-amounts/?', views.QuoteAmountsView.as_view(), name='quote_amounts'),
    url(r'^amounts/?', views.BookingServiceAmountsView.as_view(), name='booking_amounts'),
    url(r'^invoices/(?P<id>\d+)/?', views.get_invoice, name='get_invoice'),
]
