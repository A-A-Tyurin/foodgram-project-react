''' Configuration for 'users' application. '''

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    '''
    Encapsulate config options for 'users' app.
    '''
    name = 'users'
    verbose_name = _('Users')
