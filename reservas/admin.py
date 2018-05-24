# from django.contrib import admin
from django.contrib.admin.sites import AdminSite


class ReservasAdmin(AdminSite):
    # Anything we wish to add or override
    site_title = 'Reservas'
    site_header = 'Reservas'
    index_title = 'Main Menu'

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
