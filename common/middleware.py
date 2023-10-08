from django.conf import settings
from django.contrib import auth
from django.contrib.auth import load_backend
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

import logging, threading;

logger = logging.getLogger(__name__)


def set_current_organization(organization):
    threading.local().middleware_organization = organization


def get_current_organization():
    if hasattr(threading.local(), "middleware_organization"):
        return threading.local().middleware_organization
    return None


class SetOrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'user'), (
            "This middleware requires authentication middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.auth.middleware.AuthenticationMiddleware' before "
            "'common.middleware.SetOrganizationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        self.__set_organization__(request)


    def __set_organization__(self, request):
        organization = None
        if request.user.is_authenticated and hasattr(request.user, 'vinculation'):
            organization = request.user.vinculation.organization
        set_current_organization(organization)
