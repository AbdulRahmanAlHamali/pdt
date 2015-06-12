"""PDT admin."""
from adminplus.sites import AdminSitePlus

from .forms import UserAdminAuthenticationForm


class UserAdmin(AdminSitePlus):

    """Admin which is allowed for non-staff users."""

    login_form = UserAdminAuthenticationForm

    def has_permission(self, request):
        """Removed check for is_staff."""
        return request.user.is_active
