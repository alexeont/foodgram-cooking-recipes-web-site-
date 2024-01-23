from django.core.management.base import BaseCommand

from recipes.load_ingridients_csv import import_ingredients


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_ingredients()
