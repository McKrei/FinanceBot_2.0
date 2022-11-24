import sqlite3
import datetime as dt
from mainapp.models import Subcategory, Category, Operation
from django.core.management.base import BaseCommand
from bot.misc import date_str_to_datetime

cat_dict = {
    'Food': 'еда & быт',
    'Transport': 'транспорт',
    'Home': 'дом',
    'Services': 'услуги',
    'Rest': 'отдых',
    'Other': 'другое',
    'Health': 'здоровье',
    'Clothes': 'одежда',
    'Vika': 'вика',
    'Evgeniy': 'женя',
    'Cash': 'доход'
    }
class Command(BaseCommand):
    help = ''


    def handle(self, *args, **kwargs):

        db = sqlite3.connect('mainapp/finance.db')
        cursor = db.cursor()
        cursor.execute(f'''
                SELECT *
                FROM expense
            ''')
        list_ = cursor.fetchall()

        for _, _, name, amount, date, msg in list_:
            name = cat_dict[name]
            date = date_str_to_datetime(date)
            sub = Subcategory.objects.get(name=name)
            operation = Operation(user=sub.category.user,
                    category=sub.category,
                    subcategory=sub,
                    currency=sub.category.user.basic_currency,
                    amount=amount,
                    price_basic_currency=amount,
                    message=msg)
            # operation.save()
            # operation.created_at = date
            # operation.save()
        print(len(list_))
        # print(len(Operation.objects.all())-614)

        # print(len(expense_list))
        # print(expense_list)
