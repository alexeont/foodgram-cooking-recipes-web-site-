import csv
import sys

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open('recipes/data/ingredients.csv',
                      encoding='utf-8') as db_ingredients:
                reader = csv.reader(db_ingredients)
                for name, unit in reader:
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=unit
                    )
            sys.stdout.write('Загрузка данных завершена')
        except Exception as e:
            sys.stdout.write(f'Ошибка при загрузке данных: {e}')
