# from django.contrib import admin
from django.contrib import admin


class ReservasAdmin(admin.sites.AdminSite):
    # Anything we wish to add or override
    site_title = 'Reservas'
    site_header = 'Reservas'
    index_title = 'Main Menu'
    index_template = 'index.html'

    def has_permission(self, request):
        """
        Removed check for is_staff.
        """
        return request.user.is_active


reservas_admin = ReservasAdmin(name='reservas')
# Run user_admin_site.register() for each model we wish to register
# for our admin interface for users

# Run admin.site.register() for each model we wish to register
# with the REAL django admin!


class ExtendedModelAdmin(admin.ModelAdmin):
    site_actions = []
