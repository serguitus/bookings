from django.conf.urls import url

from config import views

urlpatterns = [
    url(
        r'^service_book_detail_url/?',
        views.ServiceBookDetailURLView.as_view(),
        name='service_book_detail_url'),
]
