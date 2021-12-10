# Generated by Django 2.2.6 on 2021-12-02 22:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Favorite recipe',
                'verbose_name_plural': 'Favorite recipes',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="The ingredient's name", max_length=150, unique=True, verbose_name='Name')),
                ('measurement_unit', models.CharField(help_text="The ingredient's measurement unit", max_length=25, verbose_name='Measurement unit')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="The recipe's name", max_length=200, verbose_name='Name')),
                ('text', models.TextField(help_text="The recipe's description", verbose_name='Description')),
                ('cooking_time', models.PositiveSmallIntegerField(default=1, help_text="The recipe's cooking time", validators=[django.core.validators.MinValueValidator(1)], verbose_name='Cooking time')),
                ('image', models.ImageField(blank=True, help_text="The recipe's image", null=True, upload_to='recipes/', verbose_name='Image')),
                ('created', models.DateTimeField(auto_now_add=True, help_text="The recipe's publication date", verbose_name='Publication date')),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=1, help_text='The ingredient amount', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Amount')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="The tag's name", max_length=150, unique=True, verbose_name='Name')),
                ('color', models.CharField(help_text="The tag's color", max_length=7, unique=True, verbose_name='Color')),
                ('slug', models.SlugField(help_text="The tag's slug", max_length=150, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='recipes.Recipe', verbose_name='Recipe')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='recipes.Tag', verbose_name='Tag')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='RecipeShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='recipes.Recipe', verbose_name='Recipe')),
            ],
            options={
                'verbose_name': 'Shopping cart',
                'verbose_name_plural': 'Shopping cart',
            },
        ),
    ]
