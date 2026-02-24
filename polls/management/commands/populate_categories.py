from typing import Any
from polls.models import Category
from django.core.management.base import BaseCommand



class Command(BaseCommand):  
        help = "this commands inserts post data"

        def handle(self, *args, **options):
            Category.objects.all().delete()
              
            categories = ['Sports','Technology','Science','Art','Food']

            for category_name in categories:
                Category.objects.create(name=category_name)
            
            self.stdout.write(self.style.SUCCESS("Completed inserting Data!"))