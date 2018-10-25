from django.conf.urls import url

from booking import views

urlpatterns = [
    url(r'^amounts/?', views.BookingServiceAmountsView.as_view(), name='booking_amounts'),
]
