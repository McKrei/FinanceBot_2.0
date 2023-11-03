from django.contrib import admin

from mainapp.models import Currency
from mainapp.models import User
from mainapp.models import Telegram
from mainapp.models import CurrencyReduction
from mainapp.models import Category
from mainapp.models import Subcategory
from mainapp.models import SubcategoryReduction
from mainapp.models import MoneySum
from mainapp.models import Investment
from mainapp.models import HistoryPriceInvestment

from mainapp.models import LimitNow
from mainapp.models import LimitInMonth
from mainapp.models import LimitStartMonth

from mainapp.models import Conversion
from mainapp.models import Operation


admin.site.register(Currency)
admin.site.register(User)
admin.site.register(Telegram)
admin.site.register(CurrencyReduction)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(SubcategoryReduction)
admin.site.register(MoneySum)
admin.site.register(Investment)
admin.site.register(HistoryPriceInvestment)

# admin.site.register(LimitNow)
# admin.site.register(LimitInMonth)
# admin.site.register(LimitStartMonth)

admin.site.register(Conversion)
admin.site.register(Operation)
