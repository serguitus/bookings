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
from config import urls as config_urls
from config.views import (
    LocationAutocompleteView, ServiceCategoryAutocompleteView,
    RoomTypeAutocompleteView, BoardTypeAutocompleteView,
    AllotmentAutocompleteView, ProviderAllotmentAutocompleteView,
    TransferAutocompleteView, ProviderTransferAutocompleteView,
    AddonAutocompleteView,
    ExtraAutocompleteView, ProviderExtraAutocompleteView,
)
from booking import urls as booking_urls
from booking.views import (
    PackageAutocompleteView, ProviderPackageAutocompleteView,
    PickUpAutocompleteView, DropOffAutocompleteView, PlaceAutocompleteView,
    ScheduleArrivalAutocompleteView, ScheduleDepartureAutocompleteView,
    QuotePaxVariantAutocompleteView)


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
    url(r'^package-autocomplete/$',
        PackageAutocompleteView.as_view(),
        name='package-autocomplete',
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
    url(r'^servicecategory-autocomplete/$',
        ServiceCategoryAutocompleteView.as_view(),
        name='servicecategory-autocomplete',
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
    url(r'^providerpackage-autocomplete/$',
        ProviderPackageAutocompleteView.as_view(),
        name='providerpackage-autocomplete',
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
        include(booking_urls)
    ),
    url(r'^bookings/config/',
        include(config_urls)
    ),
    url(r'^pickup-autocomplete/$',
        PickUpAutocompleteView.as_view(),
        name='pickup-autocomplete',
    ),
    url(r'^dropoff-autocomplete/$',
        DropOffAutocompleteView.as_view(),
        name='dropoff-autocomplete',
    ),
    url(r'^addon-autocomplete/$',
        AddonAutocompleteView.as_view(),
        name='addon-autocomplete',
    ),
    url(r'^place-autocomplete/$',
        PlaceAutocompleteView.as_view(),
        name='place-autocomplete',
    ),
    url(r'^arrival-autocomplete/$',
        ScheduleArrivalAutocompleteView.as_view(),
        name='arrival-autocomplete',
    ),
    url(r'^departure-autocomplete/$',
        ScheduleDepartureAutocompleteView.as_view(),
        name='departure-autocomplete',
    ),
    url(r'^quotepaxvariant-autocomplete/$',
        QuotePaxVariantAutocompleteView.as_view(),
        name='quotepaxvariant-autocomplete',
    ),
]
