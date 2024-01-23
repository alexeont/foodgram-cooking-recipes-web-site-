import csv
from pathlib import Path
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


def import_ingredients():
    try:
        with open(f'{Path(BASE_DIR.parent.parent)}/data/ingredients.csv',
                  encoding='utf-8') as db_ingredients:
            reader = csv.reader(db_ingredients)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
        print('Загрузка данных завершена')
    except Exception as e:
        print(f'Ошибка при загрузке данных: {e}')