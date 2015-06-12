"""PDT forms."""
from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.translation import ugettext_lazy as _


class UserAdminAuthenticationForm(AdminAuthenticationForm):

    """Same as Django's AdminAuthenticationForm but allows to login any user who is not staff."""

    def __init__(self, *args, **kwargs):
        """Set the labels for username and password fields."""
        super(UserAdminAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = _('Your Fogbugz username')
        self.fields['password'].label = _('Your Fogbugz password. Will not be stored.')

    def confirm_login_allowed(self, user):
        """Confirm login for all active users."""
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )
