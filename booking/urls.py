from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^quote-amounts/?', views.QuoteAmountsView.as_view(), name='quote_amounts'),
    url(r'^bookingallotment-amounts/?', views.BookingAllotmentAmountsView.as_view(), name='bookingallotment_amounts'),
    url(r'^bookingtransfer-amounts/?', views.BookingTransferAmountsView.as_view(), name='bookingtransfer_amounts'),
    url(r'^bookingextra-amounts/?', views.BookingExtraAmountsView.as_view(), name='bookingextra_amounts'),
    url(r'^bookingtransfer-time/?', views.BookingTransferTimeView.as_view(), name='bookingtransfer_time'),
    url(r'^invoices/(?P<id>\d+)/?', views.get_invoice, name='get_invoice'),
    url(r'^voucher/(?P<id>\d+)/?', views.build_voucher, name='build_voucher'),
    # url(r'^requests/(?P<id>\d+)/?', views.send_service_request, name='send_service_request'),
    url(r'^requests/(?P<id>\d+)/?', views.EmailProviderView.as_view(), name='send_service_request'),
]
