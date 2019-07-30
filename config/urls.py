from django.conf.urls import url

from config import views

urlpatterns = [

    url(r'^service-prices/pdf/?', views.PricesPDFView.as_view(), name='service_prices_pdf'),
]
