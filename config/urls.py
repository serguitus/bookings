from django.conf.urls import url

from config import views

urlpatterns = [
    url(r'^service_detail_url/?', views.ServiceDetailURLView.as_view(), name='service_detail_url'),
]
