import sqlite3
import datetime as dt
from mainapp.models import Subcategory, Category, Operation
from django.core.management.base import BaseCommand
from bot.misc import date_str_to_datetime
from openpyexcel import load_workbook


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

# cat_dict_excel1 = {
#     'B': 'еда & быт',
#     'C': 'транспорт',
#     'D': 'дом',
#     'E': 'услуги',
#     'F': 'отдых',
#     'G': 'другое',
#     'H': 'здоровье',
#     'I': 'одежда',
#     'J': 'вика',
#     'K': 'женя',
#     'L': 'доход'

#     }


cat_dict_excel1 = {
    'B': 'еда',
    'C': 'транспорт',
    'D': 'другое',
    'E': 'здоровье',
    'F': 'одежда',
    'G': 'дом',
    'H': 'еда сома',
    'I': 'другое',
    'J': 'отдых',
    }
cat_dict_excel2 = {
    'B': 'женя зарплата',
    'C': 'женя',
    'D': 'вика зарплата',
    'E': 'вика',
    'F': 'доход',
    }


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):
        filename = 'report2.xlsx'
        wb = load_workbook(filename=filename)
        day = 1
        for i, year in enumerate([2016,2017,2018]):
            wb.active = i
            sheet = wb.active
            for row in range(13,14):
                month = row - 1
                for colum in ['B', 'C', 'D', 'E', 'F']:
                    value = sheet[f'{colum}{row}'].value
                    if value:
                        amount = int(value)
                        name = cat_dict_excel2[colum]
                        # print(f'{year}-{month}-{day}', name)
                        # print(value)
                        # date = date_str_to_datetime(f'{year}-{month}-{day}')
                        # sub = Subcategory.objects.get(name=name)
                        # operation = Operation(user=sub.category.user,
                        #         category=sub.category,
                        #         subcategory=sub,
                        #         currency=sub.category.user.basic_currency,
                        #         amount=amount,
                        #         price_basic_currency=amount)
                        # operation.save()
                        # operation.created_at = date
                        # operation.save()


        # for sheet_i in range(24, 36):
        #     month = sheet_i - 23
        #     wb.active = sheet_i
        #     sheet = wb.active
        #     # print(sheet, year, month)
        #     for row in range(2, 33):
        #         day = row - 1
        #         for colum in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        #             value = sheet[f'{colum}{row}'].value
        #             if value:
        #                 amount = int(value)
        #                 name = cat_dict_excel1[colum]
        #                 # print(f'{year}-{month}-{day}')
        #                 date = date_str_to_datetime(f'{year}-{month}-{day}')
        #                 sub = Subcategory.objects.get(name=name)
        #                 operation = Operation(user=sub.category.user,
        #                         category=sub.category,
        #                         subcategory=sub,
        #                         currency=sub.category.user.basic_currency,
        #                         amount=amount,
        #                         price_basic_currency=amount)
        #                 operation.save()
        #                 operation.created_at = date
        #                 operation.save()


        # wb.save(filename = filename)
        # sheet       = wb.active
        # print(sheet['A3'])



        # db = sqlite3.connect('mainapp/finance.db')
        # cursor = db.cursor()
        # cursor.execute(f'''
        #         SELECT *
        #         FROM expense
        #     ''')
        # list_ = cursor.fetchall()

        # for _, _, name, amount, date, msg in list_:
            # name = cat_dict[name]
            # date = date_str_to_datetime(date)
            # sub = Subcategory.objects.get(name=name)
            # operation = Operation(user=sub.category.user,
            #         category=sub.category,
            #         subcategory=sub,
            #         currency=sub.category.user.basic_currency,
            #         amount=amount,
            #         price_basic_currency=amount,
            #         message=msg)
            # operation.save()
            # operation.created_at = date
            # operation.save()


        # print(len(expense_list))
        # print(expense_list)
