from django.db import models
from django.contrib.auth.models import AbstractUser


class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, verbose_name='Название валюты')
    symbol = models.CharField(max_length=8, verbose_name='Символ обозначения валюты')

    def __str__(self) -> str:
        return f'{self.name} < {self.symbol}>'

    @property
    def get():
        return 'test'

class User(AbstractUser):
    basic_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default=1)


class Telegram(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.username},  Telegram ID: {self.id}'


class CurrencyReduction(models.Model):
    id = models.AutoField(primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    reduction = models.CharField(max_length=64, verbose_name='Название валюты')

    def __str__(self) -> str:
        return f'{self.currency.name} : {self.reduction}'


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, verbose_name='Название категории')
    income_or_expense = models.BooleanField(default=True, verbose_name='True Доход')

    def __str__(self) -> str:
        first = f'{self.user.username} : {self.name} : '
        second = 'Доход' if self.income_or_expense else 'Расход'
        return first + second


class Subcategory(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, verbose_name='Название категории')

    def __str__(self) -> str:
        return f'{self.user.username} : {self.category.name} : {self.name}'


class SubcategoryReduction(models.Model):
    id = models.AutoField(primary_key=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    reduction = models.CharField(max_length=64, verbose_name='Сокращение категории')

    def __str__(self) -> str:
        return f'{self.subcategory.name} : {self.reduction}'


class MoneySum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,	decimal_places=2, default=0, verbose_name='Сумма валюты у пользователя')
    conversion = models.DecimalField(max_digits=10,	decimal_places=2, default=1, verbose_name='Конверсия к стандартной валюте пользователя')

    def __str__(self) -> str:
        return f'{self.user} {self.currency} {self.amount}'


class HistoryMoneyAllSum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,	decimal_places=2, default=0, verbose_name='Сумма Денег в стандартной валюте')
    created_at = models.DateField(verbose_name='Дата создания')

    def __str__(self) -> str:
        return f'{self.user} {self.amount} {self.created_at}'


class LimitNow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField()

    def __str__(self) -> str:
        return f'{self.user.username} : {self.category.name} : {self.amount}'


class LimitInMonth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.CharField(max_length=64, verbose_name='Месяц в формате MM.YYYY')
    amount = models.PositiveBigIntegerField()

    def __str__(self) -> str:
        return f'{self.user.username} : {self.category.name} : {self.month} : {self.amount}'


class LimitStartMonth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.CharField(max_length=64, verbose_name='Месяц в формате MM.YYYY')
    amount = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.user.username} : {self.category.name} : {self.month} : {self.amount}'


class Conversion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_sell = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='+')
    currency_buy = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='+')
    amount_sell = models.DecimalField(max_digits=10,	decimal_places=2, verbose_name='Сколько продал')
    amount_buy = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сколько купил')
    price_basic_currency = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сколько вышло в стандартной валюте')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время операции', blank=True)
    message = models.CharField(max_length=256, verbose_name='Запрос')

    def __str__(self) -> str:
        return self.message


class Operation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    price_basic_currency = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сколько вышло в стандартной валюте')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время операции', blank=True)
    message = models.CharField(max_length=256, verbose_name='Запрос')


class Investment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', blank=True)
    name = models.CharField(max_length=64, verbose_name='Название инвестиции')
    amount = models.DecimalField(max_digits=10,	decimal_places=2, default=0, verbose_name='Сумма вложения')
    price_now = models.DecimalField(max_digits=10,	decimal_places=2, default=0, verbose_name='Текщая стоимость')
    conversion_price_now = models.DecimalField(max_digits=10,	decimal_places=2, default=1, verbose_name='Конверсия к стандартной валюте текущей стоимости')
    conversion_amount = models.DecimalField(max_digits=10,	decimal_places=2, default=1, verbose_name='Конверсия к стандартной валюте вложений')


class HistoryPriceInvestment(models.Model):
    id = models.AutoField(primary_key=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', blank=True)
    amount = models.DecimalField(max_digits=10,	decimal_places=2, default=0, verbose_name='Сумма вложения')
    price_now = models.DecimalField(max_digits=10,	decimal_places=2, default=0, verbose_name='Текщая стоимость')
    conversion_price_now = models.DecimalField(max_digits=10,	decimal_places=2, default=1, verbose_name='Конверсия к стандартной валюте текущей стоимости')
    conversion_amount = models.DecimalField(max_digits=10,	decimal_places=2, default=1, verbose_name='Конверсия к стандартной валюте вложений')


    def __str__(self) -> str:
        return self.message
