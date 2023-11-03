from asgiref.sync import sync_to_async

from mainapp import models
from .operations import search_by_cur_and_reuctsub


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
        money.amount -= amount
    if '-' == symb:
        investment.amount -= amount
        investment.price_now -= amount
        investment.conversion_price_now = money.conversion * investment.price_now
        investment.conversion_amount = money.conversion * investment.amount
        money.amount += amount

    if '=' == symb:
        investment.price_now = amount
        investment.conversion_price_now = money.conversion * investment.price_now
        investment.conversion_amount = money.conversion * investment.amount

    investment.save()
    money.save()
    add_history_price_investment(investment)

    return f'Инвестиция "{investment.name}", успешно обновлена'\
            f'\n{investment.amount} {investment.currency.symbol} = {investment.price_now} {investment.currency.symbol}'\
            f'\n{investment.conversion_amount} = {investment.conversion_price_now} '



@sync_to_async
def get_investment_list(user_id):
    user = models.Telegram.objects.get(id=user_id).user
    investments = models.Investment.objects.filter(user=user)
    if not investments:
        return 'У вас нет инвестиций'
    answer = '\n'.join([f'{investment.name}: {investment.amount} {investment.currency.symbol} = {investment.price_now} {investment.currency.symbol}'
                        for investment in investments])
    return answer


@sync_to_async
def delete_investment(name, user_id):
    user = models.Telegram.objects.get(id=user_id).user
    investment = models.Investment.objects.filter(user=user, name=name)
    if not investment:
        return 'Инвестиция не найдена'
    investment = investment[0]
    # money = models.MoneySum.objects.filter(user=user, currency=investment.currency)
    # if not money:
    #     return f'У вас нет в наличии "{investment.currency.name} {investment.currency.symbol}"\nДобавьте ее с помощью конверсионной операции.'
    # money = money[0]
    # money.amount += investment.amount
    # money.save()
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
