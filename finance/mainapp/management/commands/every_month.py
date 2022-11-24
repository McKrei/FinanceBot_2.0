from datetime import datetime

from django.core.management.base import BaseCommand

# from mainapp.models import User, Category, LimitNow, LimitInMonth, LimitStartMonth
from mainapp.models import Subcategory, SubcategoryReduction

class Command(BaseCommand):
    help = 'Обновляет данные с лимитами.'


    def handle(self, *args, **kwargs):
        # all_sub = Subcategory.objects.all()
        # for sub in all_sub:
        #     sr = SubcategoryReduction(subcategory=sub,reduction=sub.name)
        #     sr.save()

        date = datetime.now()
        month = f'{date.month}.{date.year}'

        # user_id_list = User.objects.all().values_list('id')
        users = User.objects.all()
        for user in users:
            categories = Category.objects.filter(user=user)
            for category in categories:
                limit = LimitNow.objects.get(user=user, category=category)
                obj, create = LimitInMonth.objects.update_or_create(
                    user=user,
                    category=category,
                    month=month,
                    defaults={'amount': limit.amount})
                print(created)
                if not created:
                    break
