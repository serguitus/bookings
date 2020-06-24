from django.conf.urls import include, url
# from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

# router = routers.DefaultRouter()

urlpatterns = [
    # url(r'', include(router.urls)),
    url(r'api-token-auth/', obtain_jwt_token),
    url(r'api-token-refresh/', refresh_jwt_token),
    # url(r'api-auth/', include('rest_framework.urls',
    #                           namespace='rest_framework'))
]
