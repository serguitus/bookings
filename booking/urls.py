from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^quote-amounts/?', views.QuoteAmountsView.as_view(), name='quote_amounts'),
    url(r'^bookingservice-amounts/?', views.BookingServiceAmountsView.as_view(), name='booking_amounts'),
    url(r'^bookingtransfer-times/?', views.BookingTransferTimesView.as_view(), name='bookingtransfer_times'),
    url(r'^invoices/(?P<id>\d+)/?', views.get_invoice, name='get_invoice'),
    # url(r'^requests/(?P<id>\d+)/?', views.send_service_request, name='send_service_request'),
    url(r'^requests/(?P<id>\d+)/?', views.EmailProviderView.as_view(), name='send_service_request'),
]
