''' Class based forms for 'recipes' application. '''

from django import forms

from core.widgets import ColorInput, DragableImageInput
from .models import Recipe, Tag


class RecipeAdminForm(forms.ModelForm):
    ''' ModelForm class for :model:'foodgram.Ingredient'. '''
    class Meta:
        model = Recipe
        widgets = {
            'image': DragableImageInput
        }
        fields = '__all__'


class TagAdminForm(forms.ModelForm):
    ''' ModelForm class for :model:'foodgram.Tag'. '''
    class Meta:
        model = Tag
        widgets = {
            'color': ColorInput
        }
        fields = '__all__'
