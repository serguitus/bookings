"""
accounting site models
"""
from django.template.response import TemplateResponse

from hello.models import Hello1, Hello2

from common.sites import SiteModel

from reservas.admin import bookings_site


MENU_LABEL_HELLO = 'Hello'


class Hello1SiteModel(SiteModel):
    model_order = 11010
    menu_label = MENU_LABEL_HELLO
    actions_on_top = True
    model_index_action = 'hello1_index'

    def get_model_actions(self, request):
        actions = []
        perms = self.get_model_permissions(request)
        if perms.get('view'):
            actions.append(
                {
                    'name': 'hello1_view1',
                    'label': 'View 1 (Hello 1)',
                    'url': '%s:%s_%s_hello1_index' % (
                        self.admin_site.site_namespace, self.model._meta.app_label, self.model._meta.model_name),
                }
            )
            actions.append(
                {
                    'name': 'hello1_view2',
                    'label': 'View 2 (Hello 1)',
                    'url': '%s:%s_%s_hello1_second' % (
                        self.admin_site.site_namespace, self.model._meta.app_label, self.model._meta.model_name),
                }
            )
        return actions

    def get_urls(self):

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            self.build_url(r'^$', self.hello1_index, '%s_%s_hello1_index' % info),
            self.build_url(r'^second/$', self.hello1_second, '%s_%s_hello1_second' % info),
        ]
        return urlpatterns

    def hello1_index(self, request, extra_context=None):
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return TemplateResponse(request, 'hello/hello1_index.html', context)
        
    def hello1_second(self, request, extra_context=None):
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return TemplateResponse(request, 'hello/hello1_second.html', context)
        

class Hello2SiteModel(SiteModel):
    model_order = 11020
    menu_label = MENU_LABEL_HELLO
    actions_on_top = True
    model_index_action = 'hello2_index'

    def get_model_actions(self, request):
        actions = []
        perms = self.get_model_permissions(request)
        if perms.get('view'):
            actions.append(
                {
                    'name': 'hello2_view1',
                    'label': 'View 1 (Hello 2)',
                    'url': '%s:%s_%s_hello2_index' % (
                        self.admin_site.site_namespace,
                        self.model._meta.app_label,
                        self.model._meta.model_name),
                }
            )
            actions.append(
                {
                    'name': 'hello2_view2',
                    'label': 'View 2 (Hello 2)',
                    'url': '%s:%s_%s_hello2_second' % (
                        self.admin_site.site_namespace,
                        self.model._meta.app_label,
                        self.model._meta.model_name),
                }
            )
        return actions

    def get_urls(self):
    
        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            self.build_url(r'^$', self.hello2_index, '%s_%s_hello2_index' % info),
            self.build_url(r'^second/$', self.hello2_second, '%s_%s_hello2_second' % info),
        ]
        return urlpatterns

    def hello2_index(self, request, extra_context=None):
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return TemplateResponse(request, 'hello/hello2_index.html', context)

    def hello2_second(self, request, extra_context=None):
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return TemplateResponse(request, 'hello/hello2_second.html', context)


bookings_site.register(Hello1, Hello1SiteModel)
bookings_site.register(Hello2, Hello2SiteModel)
