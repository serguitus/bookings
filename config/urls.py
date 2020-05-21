from django.conf.urls import url

from config import views

urlpatterns = [
    url(
        r'^book_detail_url/?',
        views.ServiceBookDetailURLView.as_view(),
        name='book_detail_url'),
]
