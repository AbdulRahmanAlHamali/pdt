"""PDT admin."""
from django.contrib.admin import ModelAdmin
from adminplus.sites import AdminSitePlus

from .forms import UserAdminAuthenticationForm


# default django's list per page is quite too high
ModelAdmin.list_per_page = 25


class UserAdmin(AdminSitePlus):

    """Admin which is allowed for non-staff users."""

    login_form = UserAdminAuthenticationForm

    def has_permission(self, request):
        """Removed check for is_staff."""
        return request.user.is_active
