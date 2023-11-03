from asgiref.sync import sync_to_async

from mainapp import models
from .operations import search_by_cur_and_reuctsub
from bot.finance_bot.misc.util import beautiful_numbers
from .money import account_operation_change_to_many
from bot.finance_bot.reports.main import create_table_invest


@sync_to_async
def start_investment(symb, name, amount, cur, user_id):
    user = models.Telegram.objects.get(id=user_id).user
    cur, _, _, _ = search_by_cur_and_reuctsub([cur], user)
    if not cur:
        return 'Валюта не найдена'
    investment = models.Investment.objects.filter(name=name)
    if not investment and symb != '+':
        return 'Инвестиция не найдена'
    investment = investment[0] if investment else None
    money = models.MoneySum.objects.filter(user=user, currency=cur)
    if not money:
        return f'У вас нет в наличии "{cur.name} {cur.symbol}"\nДобавьте ее с помощью конверсионной операции.'
    money = money[0]
    price_bas_cur = money.conversion * amount
    mes = ''

    if '+' == symb:
        if not investment:
            investment = models.Investment.objects.create(
                user=user,
                name=name,
                amount=amount,
                currency=cur,
                price_now=amount,
                conversion_price_now=price_bas_cur,
                conversion_amount=price_bas_cur,
            )
        else:
            investment.amount += amount
            investment.price_now += amount
            investment.conversion_price_now = money.conversion * investment.price_now
            investment.conversion_amount = money.conversion * investment.amount
        account_operation_change_to_many(money, amount, False)
    if '-' == symb:
        investment.amount -= amount
        investment.price_now -= amount
        investment.conversion_price_now = money.conversion * investment.price_now
        investment.conversion_amount = money.conversion * investment.amount
        account_operation_change_to_many(money, amount, True)

    if '=' == symb:
        last_price = investment.conversion_price_now
        investment.price_now = amount
        investment.conversion_price_now = money.conversion * investment.price_now
        investment.conversion_amount = money.conversion * investment.amount
        mes = f'Цена инвестиции "{investment.name}" успешно обновлена, изменение на {investment.conversion_price_now / last_price - 1:.2%}'

    investment.save()
    add_history_price_investment(investment)
    
    mes = mes if mes else f'Инвестиция "{investment.name}", успешно обновлена'\
            f'\n{investment.amount} {investment.currency.symbol} = {investment.price_now} {investment.currency.symbol}'\
            f'\n{investment.conversion_amount} = {investment.conversion_price_now} '
    return mes



@sync_to_async
def get_investment_list(user_id, comand=False):
    user = models.Telegram.objects.get(id=user_id).user
    investments = models.Investment.objects.filter(user=user)
    mes = ''
    if not investments:
        mes = 'У вас нет инвестиций'
    elif comand:
        mes = '\n'.join([f'инвестиции = {i.name} {int(i.price_now)} {i.currency.symbol}' for i in investments])
    else:
        title = 'Инвестиции в миллионах руб.'
        answer = create_table_invest(investments)
        mes = f'{title}\n{answer}'
    return mes


@sync_to_async
def delete_investment(name, user_id):
    user = models.Telegram.objects.get(id=user_id).user
    investment = models.Investment.objects.filter(user=user, name=name)
    if not investment:
        return 'Инвестиция не найдена'
    investment = investment[0]
    investment.delete()
    add_history_price_investment(investment)

    return f'Инвестиция "{name}", успешно удалена'


def add_history_price_investment(investment):
    obj = models.HistoryPriceInvestment.objects.create(
        investment=investment,
        currency=investment.currency,
        amount=investment.amount,
        price_now=investment.price_now,
        conversion_price_now=investment.conversion_price_now,
        conversion_amount=investment.conversion_amount,
    )
    obj.save()
