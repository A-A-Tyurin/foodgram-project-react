''' Configuration for 'recipes' application. '''

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RecipesConfig(AppConfig):
    '''
    Encapsulate config options for 'recipes' app.
    '''
    name = 'recipes'
    verbose_name = _('Recipes')
