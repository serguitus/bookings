"""reservas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from reservas.admin import reservas_admin
from reservas.admin import bookings_site

from booking.views import (
    BookingPaxAutocompleteView,
)
from finance.views import (
    AccountAutocompleteView, LoanEntityAutocompleteView, LoanAccountAutocompleteView,
    AgencyAutocompleteView, ProviderAutocompleteView,
)
from config.views import (
    LocationAutocompleteView, RoomTypeAutocompleteView, BoardTypeAutocompleteView,
    AllotmentAutocompleteView, ProviderAllotmentAutocompleteView,
    TransferAutocompleteView, ProviderTransferAutocompleteView,
    ExtraAutocompleteView, ProviderExtraAutocompleteView,
)
from booking import urls as booking_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^reservas/', reservas_admin.urls),

    url(r'^%s/' % (bookings_site.name), bookings_site.urls),

    url(r'^account-autocomplete/$',
        AccountAutocompleteView.as_view(),
        name='account-autocomplete',
    ),
    url(r'^agency-autocomplete/$',
        AgencyAutocompleteView.as_view(),
        name='agency-autocomplete',
    ),
    url(r'^allotment-autocomplete/$',
        AllotmentAutocompleteView.as_view(),
        name='allotment-autocomplete',
    ),
    url(r'^boardtype-autocomplete/$',
        BoardTypeAutocompleteView.as_view(),
        name='boardtype-autocomplete',
    ),
    url(r'^bookingpax-autocomplete/$',
        BookingPaxAutocompleteView.as_view(),
        name='bookingpax-autocomplete',
    ),
    url(r'^extra-autocomplete/$',
        ExtraAutocompleteView.as_view(),
        name='extra-autocomplete',
    ),
    url(r'^loanentity-autocomplete/$',
        LoanEntityAutocompleteView.as_view(),
        name='loanentity-autocomplete',
    ),
    url(r'^loanaccount-autocomplete/$',
        LoanAccountAutocompleteView.as_view(),
        name='loanaccount-autocomplete',
    ),
    url(r'^location-autocomplete/$',
        LocationAutocompleteView.as_view(),
        name='location-autocomplete',
    ),
    url(r'^provider-autocomplete/$',
        ProviderAutocompleteView.as_view(),
        name='provider-autocomplete',
    ),
    url(r'^providerallotment-autocomplete/$',
        ProviderAllotmentAutocompleteView.as_view(),
        name='providerallotment-autocomplete',
    ),
    url(r'^providertransfer-autocomplete/$',
        ProviderTransferAutocompleteView.as_view(),
        name='providertransfer-autocomplete',
    ),
    url(r'^providerextra-autocomplete/$',
        ProviderExtraAutocompleteView.as_view(),
        name='providerextra-autocomplete',
    ),
    url(r'^roomtype-autocomplete/$',
        RoomTypeAutocompleteView.as_view(),
        name='roomtype-autocomplete',
    ),
    url(r'^transfer-autocomplete/$',
        TransferAutocompleteView.as_view(),
        name='transfer-autocomplete',
    ),
    url(r'^bookings/booking/',
        include(booking_urls)),
]
