import csv
import sys

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open('recipes/data/tags.csv',
                      encoding='utf-8') as file:
                reader = csv.reader(file)
                for name, color, slug in reader:
                    Tag.objects.get_or_create(
                        name=name,
                        color=color,
                        slug=slug
                    )
            sys.stdout.write('Загрузка данных завершена')
        except Exception as e:
            sys.stdout.write(f'Ошибка при загрузке данных: {e}')
