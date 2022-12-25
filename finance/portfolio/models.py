from env import TinkoffKey
from django.db import models
from mainapp.models import User, Telegram
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.services import InstrumentsService, MarketDataService
from tinkoff.invest.utils import now
from datetime import timedelta
from asgiref.sync import sync_to_async

'''
TODO
1 - создание портфеля
1.1 - пополнение портфеля (возможность списать со счета)
2 - добавление акций
3 - показать что есть в портфеле
4 - удаление акций
2) как будем обновлять фиги и добавлять цену за сегодня?

'''


class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, verbose_name='Название портфеля')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Стоимость портфеля')

    @sync_to_async
    def create(self, name, user=None, tgid=None):
        if not user:
            user = Telegram.objects.filter(id=tgid)
            if not user:
                return False, 'Пользователь не найден'
            else:
                user = user[0].user
        if Portfolio.objects.filter(user=user, name=name):
            return False, 'Уже есть портфель с таким именем'
        p = Portfolio(user=user, name=name)
        p.save()
        return True, f'Портфель {name} создан'



class Asset(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, verbose_name='Имя актива')
    ticker = models.CharField(max_length=64, verbose_name='ticker актива')
    figi = models.CharField(max_length=32, verbose_name='FIGI')
    type = models.CharField(max_length=32, verbose_name='Тип актива')
    currency = models.CharField(max_length=16, verbose_name='валюта')
    first_candle_date = models.DateTimeField(verbose_name='дата начала истории продаж')

    def get_data(self):
        with Client(TinkoffKey.TOKEN) as cl:
            instruments: InstrumentsService = cl.instruments
            market_data: MarketDataService = cl.market_data
            l = []
            for method in ['shares', 'bonds', 'etfs', 'currencies']: #, 'futures']:
                for item in getattr(instruments, method)().instruments:
                    asset = Asset.objects.filter(ticker=item.ticker, type=method)
                    if asset:
                        asset = asset[0]
                        asset.figi = item.figi
                    else:
                        asset = Asset(name=item.name,
                        ticker=item.ticker,
                        figi=item.figi,
                        type=method,
                        currency=item.currency,
                        first_candle_date=item.first_1day_candle_date)
                    asset.save()


class UserAsset(models.Model):
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date_buy = models.DateField(verbose_name='дата операции')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Сумма сделки')
    count = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Количество')


class HistoryPriceAsset(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='дата операции')
    closed = models.DecimalField(max_digits=12, decimal_places=4, verbose_name='цена закрытия')
    open_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name='цена открытия')
    low = models.DecimalField(max_digits=12, decimal_places=4, verbose_name='минимальная цена за день')
    high = models.DecimalField(max_digits=12, decimal_places=4, verbose_name='максимальная цена за день')
    volume = models.IntegerField(verbose_name='объем торгов')

    def _get_candles(self, asset, start, end):
        to_float = lambda x: float(f'{x.units}.{x.nano}')
        with Client(TinkoffKey.TOKEN) as client:
            for candle in client.get_all_candles(
                        figi=asset.figi,
                        from_=start,
                        to=end,
                        interval=CandleInterval.CANDLE_INTERVAL_DAY):
                hpa = HistoryPriceAsset.objects.filter(asset=asset, date=candle.time)
                if hpa:
                    continue
                hpa = HistoryPriceAsset(
                    asset=asset,
                    date=candle.time,
                    closed=to_float(candle.close),
                    open_price=to_float(candle.open),
                    low=to_float(candle.low),
                    high=to_float(candle.high),
                    volume=candle.volume
                    )
                hpa.save()


    def validate_history(self, asset: Asset, date: tuple):
        hpa = HistoryPriceAsset.objects.filter(asset=asset).order_by('date')
        data_end = now()
        date_start = data_end.replace(
            year=date[0], month=date[1], day=date[2]) - timedelta(days=1)
        if hpa:
            hpa_date_start = hpa[0].date.date()
            if hpa_date_start > date_start:
                data_end = hpa_date_start - timedelta(days=1)
            else: return

        self._get_candles(asset, date_start, data_end)
