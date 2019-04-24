from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^quote-amounts/?', views.QuoteAmountsView.as_view(), name='quote_amounts'),

    url(r'^bookingallotment-amounts/?', views.BookingAllotmentAmountsView.as_view(), name='bookingallotment_amounts'),
    url(r'^bookingtransfer-amounts/?', views.BookingTransferAmountsView.as_view(), name='bookingtransfer_amounts'),
    url(r'^bookingextra-amounts/?', views.BookingExtraAmountsView.as_view(), name='bookingextra_amounts'),
    url(r'^bookingpackage-amounts/?', views.BookingPackageAmountsView.as_view(), name='bookingpackage_amounts'),
    url(r'^bookingpackageallotment-amounts/?', views.BookingPackageAllotmentAmountsView.as_view(), name='bookingpackageallotment_amounts'),
    url(r'^bookingpackagetransfer-amounts/?', views.BookingPackageTransferAmountsView.as_view(), name='bookingpackagetransfer_amounts'),
    url(r'^bookingpackageextra-amounts/?', views.BookingPackageExtraAmountsView.as_view(), name='bookingpackageextra_amounts'),

    url(r'^bookingtransfer-time/?', views.BookingTransferTimeView.as_view(), name='bookingtransfer_time'),

    url(r'^invoices/(?P<id>\d+)/print/?', views.get_invoice, name='get_invoice'),
    url(r'^voucher/(?P<id>\d+)/print/?', views.build_voucher, name='build_voucher'),
    # url(r'^actions/(?P<id>\d+)/?', views.booking_actions, name='exec_action'),
    # url(r'^requests/(?P<id>\d+)/?', views.send_service_request, name='send_service_request'),
    url(r'^requests/(?P<id>\d+)/?', views.EmailProviderView.as_view(), name='send_service_request'),
    url(r'^confirm/(?P<id>\d+)/?', views.EmailConfirmationView.as_view(), name='send_booking_confirmation'),
]
