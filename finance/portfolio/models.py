from env import TinkoffKey
from django.db import models
from mainapp.models import User
from tinkoff.invest import Client
from tinkoff.invest.services import InstrumentsService, MarketDataService



class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, verbose_name='Название портфеля')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Стоимость портфеля')


class Asset(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, verbose_name='Имя актива')
    ticker = models.CharField(max_length=64, verbose_name='ticker актива')
    figi = models.CharField(max_length=32, verbose_name='FIGI')
    type = models.CharField(max_length=32, verbose_name='Тип актива')
    currency = models.CharField(max_length=16, verbose_name='валюта')


    def get_data(self):
        with Client(TinkoffKey.TOKEN) as cl:
            instruments: InstrumentsService = cl.instruments
            market_data: MarketDataService = cl.market_data
            l = []
            for method in ['shares', 'bonds', 'etfs', 'currencies']: #, 'futures']:
                for item in getattr(instruments, method)().instruments:

                    asset = Asset.objects.filter(ticker=item.ticker, type=method)
                    if asset:
                        asset[0].figi = item.figi
                    else:
                        new_asset = Asset(name=item.name,
                        ticker=item.ticker,
                        figi=item.figi,
                        type=method,
                        currency=item.currency)
                        new_asset.save()



class UsersAssets(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date_buy = models.DateField(verbose_name='дата операции')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Сумма сделки')
    count = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Количество')


class HistoryUsersAssets(models.Model):
    users_assets = models.ForeignKey(UsersAssets, on_delete=models.CASCADE)
    data = models.DateField(verbose_name='дата операции')
    closed = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='цена закрытия')
    low = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='минимальная цена за день')
    hight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='максимальная цена за день')
