from asgiref.sync import sync_to_async
from typing import List, Tuple
from mainapp.models import MoneySum
from mainapp.models import User, Telegram
from bot.misc.util import beautiful_numbers as bn
from mainapp.models import Currency
from decimal import Decimal



@sync_to_async
def answer_for_user_money(telegram_id: int) -> Tuple[str]:
    '''
    Prepare answers for the users, upon request 'Деньги'
    First answer: line-by-line output of the amount for each currency
    Second answer: if count currency > 1 summa (amount * rate) else None
    '''
    user = Telegram.objects.get(id=telegram_id).user
    money_list = MoneySum.objects.filter(user=user)

    answer = '\n'.join([
                f'{bn(obj.amount)} {obj.currency.symbol}, Курс {obj.conversion}'
                for obj in money_list])

    if len(money_list) > 1:
        summa = sum([obj.amount * obj.conversion for obj in money_list])
        answer += f'\nВсего: {bn(summa)} {user.basic_currency.symbol}'
    return answer

def account_operation_change_to_many(money: MoneySum, sum_operation: Decimal, income_or_expense: bool) -> None:
    if income_or_expense:
        money.amount = money.amount + sum_operation
    else:
        money.amount = money.amount - sum_operation
    money.save()


def conversion_change_to_many(user: User,
    price_basic_currency: Decimal,
    cur_sell: Currency, sum_sell: Decimal,
    cur_buy: Currency, sum_buy: Decimal) -> str:

    money_sell = MoneySum.objects.filter(user=user, currency=cur_sell)[0]
    money_buy = MoneySum.objects.filter(user=user, currency=cur_buy)

    money_sell.amount = money_sell.amount - sum_sell
    if money_buy:
        money_buy = money_buy[0]
        old_course = money_buy.conversion
        s = money_buy.amount
        c = money_buy.conversion
        money_buy.amount = sum_buy + s
        if not user.basic_currency == cur_buy:
            money_buy.conversion = ((s * c) + price_basic_currency) / (s + sum_buy)

    else:
        money_buy = MoneySum(user=user,
                    currency=cur_buy,
                    amount=sum_buy,
                    conversion=price_basic_currency / sum_buy)
        old_course = 0
    money_sell.save()
    money_buy.save()
    msg_sell = f'{bn(money_buy.amount)} {money_buy.currency.symbol} курс: {bn(money_buy.conversion)}'
    msg_buy = f'{bn(money_sell.amount)} {money_sell.currency.symbol} курс: {bn(money_sell.conversion)}'
    return old_course, f'Результат операции:\n{msg_sell}\n{msg_buy}'


def update_count_money(money: MoneySum, operator: str, num) -> MoneySum:
    if operator == '+':
        money.amount += Decimal(num)
    else:
        money.amount -= Decimal(num)
    money.save()
    return money
