import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open(f'{Path(BASE_DIR.parent.parent)}/data/tags.csv',
                      encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    Tag.objects.get_or_create(
                        name=row[0],
                        color=row[1],
                        slug=row[2]
                    )
            print('Загрузка данных завершена')
        except Exception as e:
            print(f'Ошибка при загрузке данных: {e}')
