from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^quote-amounts/?', views.QuoteAmountsView.as_view(), name='quote_amounts'),
    url(r'^quoteallotment-amounts/?', views.QuoteAllotmentAmountsView.as_view(), name='quoteallotment_amounts'),
    url(r'^quotetransfer-amounts/?', views.QuoteTransferAmountsView.as_view(), name='quotetransfer_amounts'),
    url(r'^quoteextra-amounts/?', views.QuoteExtraAmountsView.as_view(), name='quoteextra_amounts'),
    url(r'^quotepackage-amounts/?', views.QuotePackageAmountsView.as_view(), name='quotepackage_amounts'),
    url(r'^quotepackageallotment-amounts/?', views.QuotePackageAllotmentAmountsView.as_view(), name='quotepackageallotment_amounts'),
    url(r'^quotepackagetransfer-amounts/?', views.QuotePackageTransferAmountsView.as_view(), name='quotepackagetransfer_amounts'),
    url(r'^quotepackageextra-amounts/?', views.QuotePackageExtraAmountsView.as_view(), name='quotepackageextra_amounts'),

    url(r'^booking-amounts/?', views.BookingAmountsView.as_view(), name='booking_amounts'),
    url(r'^bookingallotment-amounts/?', views.BookingAllotmentAmountsView.as_view(), name='bookingallotment_amounts'),
    url(r'^bookingtransfer-amounts/?', views.BookingTransferAmountsView.as_view(), name='bookingtransfer_amounts'),
    url(r'^bookingextra-amounts/?', views.BookingExtraAmountsView.as_view(), name='bookingextra_amounts'),
    url(r'^bookingpackage-amounts/?', views.BookingPackageAmountsView.as_view(), name='bookingpackage_amounts'),
    url(r'^bookingpackageallotment-amounts/?', views.BookingPackageAllotmentAmountsView.as_view(), name='bookingpackageallotment_amounts'),
    url(r'^bookingpackagetransfer-amounts/?', views.BookingPackageTransferAmountsView.as_view(), name='bookingpackagetransfer_amounts'),
    url(r'^bookingpackageextra-amounts/?', views.BookingPackageExtraAmountsView.as_view(), name='bookingpackageextra_amounts'),

    url(r'^bookingtransfer-time/?', views.BookingTransferTimeView.as_view(), name='bookingtransfer_time'),
    url(r'^bookingtransfer-schedule-from/?', views.BookingTransferScheduleFromView.as_view(), name='bookingtransfer_schedule_from'),
    url(r'^bookingtransfer-schedule-to/?', views.BookingTransferScheduleToView.as_view(), name='bookingtransfer_schedule_to'),

    # url(r'^voucher/(?P<id>\d+)/print/?', views.build_voucher, name='build_voucher'),
    # url(r'^actions/(?P<id>\d+)/?', views.booking_actions, name='exec_action'),
    # url(r'^requests/(?P<id>\d+)/?', views.send_service_request, name='send_service_request'),
    url(r'^requests/(?P<id>\d+)/?', views.EmailProviderView.as_view(), name='send_service_request'),
    url(r'^package_service_requests/(?P<id>\d+)/?', views.EmailProviderPackageServiceView.as_view(), name='send_package_service_request'),
    url(r'^confirm/(?P<id>\d+)/?', views.EmailConfirmationView.as_view(), name='send_booking_confirmation'),
    url(r'^invoice/(?P<id>\d+)/?', views.BookingInvoiceView.as_view(), name='booking_invoice'),
    url(r'^invoice/pdf/(?P<id>\d+)/?', views.BookingInvoicePDFView.as_view(), name='booking_invoice_pdf'),
    url(r'^invoice/cancel/(?P<id>\d+)/?', views.BookingInvoiceCancelView.as_view(), name='booking_invoice_cancel'),

    url(r'^updateservices/(?P<id>\d+)/?', views.BookingServiceUpdateView.as_view(), name='bookingservice_update'),

    url(r'^bookingallotment-providers-costs/?', views.BookingAllotmentProvidersCostsView.as_view(), name='bookingallotment_providers_costs'),
    url(r'^bookingtransfer-providers-costs/?', views.BookingTransferProvidersCostsView.as_view(), name='bookingtransfer_providers_costs'),
    url(r'^bookingextra-providers-costs/?', views.BookingExtraProvidersCostsView.as_view(), name='bookingextra_providers_costs'),
    url(r'^bookingpackageallotment-providers-costs/?', views.BookingPackageAllotmentProvidersCostsView.as_view(), name='bookingpackageallotment_providers_costs'),
    url(r'^bookingpackagetransfer-providers-costs/?', views.BookingPackageTransferProvidersCostsView.as_view(), name='bookingpackagetransfer_providers_costs'),
    url(r'^bookingpackageextra-providers-costs/?', views.BookingPackageExtraProvidersCostsView.as_view(), name='bookingpackageextra_providers_costs'),
]
