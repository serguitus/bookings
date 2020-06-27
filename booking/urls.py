from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^quote-amounts/?', views.QuoteAmountsView.as_view(), name='quote_amounts'),
    url(r'^quoteallotment-amounts/?', views.NewQuoteAllotmentAmountsView.as_view(), name='quoteallotment_amounts'),
    url(r'^quotetransfer-amounts/?', views.NewQuoteTransferAmountsView.as_view(), name='quotetransfer_amounts'),
    url(r'^quoteextra-amounts/?', views.NewQuoteExtraAmountsView.as_view(), name='quoteextra_amounts'),
    url(r'^quotepackage-amounts/?', views.QuoteExtraPackageAmountsView.as_view(), name='quotepackage_amounts'),

    url(r'^booking-amounts/?', views.BookingAmountsView.as_view(), name='booking_amounts'),
    url(r'^bookingallotment-amounts/?', views.BookingProvidedAllotmentAmountsView.as_view(), name='bookingallotment_amounts'),
    url(r'^bookingtransfer-amounts/?', views.BookingProvidedTransferAmountsView.as_view(), name='bookingtransfer_amounts'),
    url(r'^bookingextra-amounts/?', views.BookingProvidedExtraAmountsView.as_view(), name='bookingextra_amounts'),
    url(r'^bookingpackage-amounts/?', views.BookingExtraPackageAmountsView.as_view(), name='bookingpackage_amounts'),

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

    url(r'^bookingallotment-providers-costs/?', views.BookingProvidedAllotmentProvidersCostsView.as_view(), name='bookingallotment_providers_costs'),
    url(r'^bookingtransfer-providers-costs/?', views.BookingProvidedTransferProvidersCostsView.as_view(), name='bookingtransfer_providers_costs'),
    url(r'^bookingextra-providers-costs/?', views.BookingProvidedExtraProvidersCostsView.as_view(), name='bookingextra_providers_costs'),

    url(r'^quoteallotment-providers-costs/?', views.NewQuoteAllotmentProvidersCostsView.as_view(), name='quoteallotment_providers_costs'),
    url(r'^quotetransfer-providers-costs/?', views.NewQuoteTransferProvidersCostsView.as_view(), name='quotetransfer_providers_costs'),
    url(r'^quoteextra-providers-costs/?', views.NewQuoteExtraProvidersCostsView.as_view(), name='quoteextra_providers_costs'),

    url(r'^extra-service-details/?', views.ExtraServiceDetailsView.as_view(), name='extra-service-details'),
    url(r'^transfer-service-details/?', views.TransferServiceDetailsView.as_view(), name='transfer-service-details'),

    url(
        r'^quote_book_detail_url/?',
        views.NewQuoteServiceBookDetailURLView.as_view(),
        name='quote_book_detail_url'),
    url(
        r'^booking_book_detail_url/?',
        views.BookingBookDetailURLView.as_view(),
        name='booking_book_detail_url'),
    url(
        r'^booking_add_service/?',
        views.BookingAddServiceView.as_view(),
        name='booking_add_service'),
    url(
        r'^quote_add_service/?',
        views.QuoteAddServiceView.as_view(),
        name='quote_add_service'),
    url(
        r'^quote_add_package_service/?',
        views.QuoteAddPackageServiceView.as_view(),
        name='quote_add_package_service'),
    url(
        r'^booking_add_package_service/?',
        views.BookingAddPackageServiceView.as_view(),
        name='booking_add_package_service'),
]
