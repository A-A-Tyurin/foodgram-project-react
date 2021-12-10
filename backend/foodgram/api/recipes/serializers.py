''' Serializers for 'recipes' API application. '''

from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import ValidationError

from api.users.serializers import UserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class TagSerializer(serializers.ModelSerializer):
    ''' Serializer class for :model:'recipes.Tag'. '''

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeTagSerializer(serializers.ModelSerializer):
    ''' Serializer class for :model:'recipes.RecipeTag'. '''

    tag = TagSerializer()

    class Meta:
        model = RecipeTag
        fields = '__all__'

    def to_internal_value(self, data):
        if not isinstance(data, int):
            raise ValidationError(
                _('Invalid data. Expected a int type.')
            )
        try:
            tag = Tag.objects.get(id=data)
        except Tag.DoesNotExist:
            raise ValidationError(_('Invalid data. No such tag.'))
        return tag

    def to_representation(self, instance):
        representation = vars(instance.tag)
        representation.pop('_state')
        return representation


class IngredientSerializer(serializers.ModelSerializer):
    ''' Serializer class for :model:'recipes.Ingredient'. '''

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ''' Serializer class for :model:'recipes.RecipeIngredient'. '''

    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = '__all__'

    def to_internal_value(self, data):
        id = data.get('id')
        amount = data.get('amount')
        if id is None:
            raise ValidationError(
                _('''Invalid data. 'id' parameter is required.''')
            )
        if not isinstance(id, int):
            raise ValidationError(
                _('''Invalid data.'''
                  ''' 'id' parameter expected a int type.''')
            )
        try:
            ingredient = Ingredient.objects.get(id=id)
        except Ingredient.DoesNotExist:
            raise ValidationError(
                _('Invalid data. No such ingredient.')
            )
        if amount is None:
            raise ValidationError(
                _('''Invalid data. 'amount' parameter is required.''')
            )
        if not isinstance(amount, int):
            raise ValidationError(
                _('''Invalid data. 'amount' parameter'''
                  ''' expected a int type.''')
            )
        if amount < 1:
            raise ValidationError(
                _('''Invalid data. 'amount' parameter'''
                  ''' must be greate than or equal to 1.''')
            )
        return ingredient, amount

    def to_representation(self, instance):
        representation = vars(instance.ingredient)
        representation.pop('_state')
        representation['amount'] = instance.amount
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    ''' Serializer class for :model:'recipes.Recipe'. '''
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=True)
    tags = RecipeTagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('created',)

    def validate_tags(self, value):
        if len(value) == 0:
            raise ValidationError(
                _('A recipe must have at least one tag.')
            )
        tag_ids = [tag.id for tag in value]
        unique_tag_ids = set(tag_ids)
        if len(unique_tag_ids) != len(tag_ids):
            raise ValidationError(
                _('''Invalid data. Tag's list contains duplicates.''')
            )
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise ValidationError(
                _('A recipe must have at least one ingredient.')
            )
        ingredient_ids = [ingredient.id for ingredient, _ in value]
        unique_ingredient_ids = set(ingredient_ids)
        if len(unique_ingredient_ids) != len(ingredient_ids):
            raise ValidationError(
                _('''Invalid data. Ingredient's list '''
                  '''contains duplicates.''')
            )
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=recipe, tag=tag) for tag in tags]
        )
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount) for ingredient, amount in ingredients]
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)
        instance.save()
        instance.tags.all().delete()
        instance.ingredients.all().delete()
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=instance, tag=tag) for tag in tags]
        )
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=instance,
                ingredient=ingredient,
                amount=amount) for ingredient, amount in ingredients]
        )
        return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (False if user.is_anonymous else user.favorite_recipes
                                                    .filter(recipe=obj)
                                                    .exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (False if user.is_anonymous else user.shopping_cart
                                                    .filter(recipe=obj)
                                                    .exists())


class RecipeShortSerializer(serializers.ModelSerializer):
    '''
    Serializer class with short representation
    for :model:'recipes.RecipeIngredient'.
    '''

    class Meta:
        model = Recipe
        fields = read_only_fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class UserSubscriptionSerializer(UserSerializer):
    ''' Serializer class for user subscriptions. '''
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (UserSerializer.Meta.fields
                  + ('recipes', 'recipes_count',))

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = (self.context['request'].query_params
                                                .get('recipes_limit'))
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                raise ValidationError(
                    _('''Parameter 'recipes_limit' excepted a int type''')
                )
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()
