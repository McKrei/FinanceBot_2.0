from asgiref.sync import sync_to_async
from django.db.models import Sum

from typing import Tuple, List
from datetime import datetime
from decimal import Decimal


from bot.finance_bot.misc.util import get_words, get_number
from bot.finance_bot import keyboards as kb
from bot.finance_bot.misc.util import beautiful_numbers as bn
from bot.finance_bot.misc.util import create_detail_operation_sting
from bot.finance_bot.misc.util import beautiful_account_operation
from bot.finance_bot.models.currency import dict_currency_reduction_for_search
from mainapp.models import Category, Subcategory, SubcategoryReduction
from mainapp.models import User, Telegram
from mainapp.models import Currency, CurrencyReduction
from mainapp.models import MoneySum
from mainapp.models import Conversion, Operation

from bot.finance_bot.models.money import conversion_change_to_many
from bot.finance_bot.models.money import update_count_money
from bot.finance_bot.models.money import account_operation_change_to_many


def conversion_save(user: User,
                    currency_sell: Currency,
                    amount_sell: Decimal,
                    currency_buy: Currency,
                    amount_buy: Decimal,
                    price_basic_currency: Decimal,
                    message: str) -> int:

    conversion = Conversion(user=user,
                            currency_sell=currency_sell,
                            currency_buy=currency_buy,
                            amount_sell=amount_sell,
                            amount_buy=amount_buy,
                            price_basic_currency=price_basic_currency,
                            message=message)
    conversion.save()

    return conversion.id

def account_operation_save(user: User,
                            amount: Decimal,
                            cur: Currency,
                            cat: Category,
                            subcat: Subcategory,
                            price_bas_cur: Decimal,
                            message: str) -> int:

    operation = Operation(user=user,
                        category=cat,
                        subcategory=subcat,
                        currency=cur,
                        amount=amount,
                        price_basic_currency=price_bas_cur,
                        message=message)

    operation.save()
    return operation.id

def conversion_validator(msg: str) -> tuple:
    '''
    Проверяем сообщение, парсим его и исключаем основные ошибки.
    Если есть ошибки возвращаем False, message Error
    Если все хорошо, возвращаем True, (Currency, summa)
    '''
    try: # Проверка есть ли слова
        cur_reduction = get_words(msg)[0]
    except IndexError:
        return False, f'Укажите валюту сделки,\nтут ее нету: {msg}'
    try: # Проверка есть ли такая валюта
        cur = CurrencyReduction.objects.filter(reduction=cur_reduction)[0].currency
    except IndexError:
        return False, f'Нет такой валюты: {cur_reduction}\nпосмотреть список валют, команда: /currency_all'
    # Проверка есть ли число
    num = get_number(msg)
    if not num: return False, f'Не разобрал сумму сделки: {msg}'
    return True, (cur, Decimal(num[0]))



@sync_to_async
def conversion_operation(telegram_id: int, message: str) -> Tuple[bool, str]:
    '''
    Получаем сообщение на конверсионную операцию.
    возвращаем результат True or False and id_operation (если она есть) and message
    '''
    # Первичная валидация и парсинг данных из сообщения и преобразование к нормальному виду
    sell, buy = message.split('=')
    r_sell, t_sell = conversion_validator(sell)
    if not r_sell: return False, False, t_sell, None
    r_buy, t_buy = conversion_validator(buy)
    if not r_buy: return False, False, t_buy, None
    # Получаем остальные данные для записи операции, проверяем наличии валюты продажи у User
    user = Telegram.objects.get(id=telegram_id).user
    money = MoneySum.objects.filter(user=user, currency=t_sell[0])
    if not money: return False, False, f'У вас нету: {t_sell.name}.\nСперва нужно купить ее!', None
    price_basic_currency = money[0].conversion * t_sell[1]
    # Записываем изменения в БД
    old_course, result = conversion_change_to_many(user, price_basic_currency, *t_sell, *t_buy)
    id_operation = conversion_save(user, *t_sell, *t_buy, price_basic_currency, message)
    # Готовим итоговое сообщение
    sell = f'Продажа {bn(t_sell[1])}{t_sell[0].symbol}'
    buy = f'Покупка {bn(t_buy[1])}{t_buy[0].symbol}'
    answer = f'Записал конверсионную операцию:\n{sell}\n{buy}\n{result}'
    return True, id_operation, answer, old_course

def search_by_cur_and_reuctsub(all_words, user):

    cur = cat = subcat = None
    for i, word in enumerate(all_words):
        cur = dict_currency_reduction_for_search.get(word)
        if cur:
            all_words.pop(i)
            cur = Currency.objects.filter(name=cur)[0]
            break

    dict_subcats = dict(SubcategoryReduction.objects.filter(
        subcategory__category__user=user
        ).values_list('reduction', 'subcategory__id'))
    for i, word in enumerate(all_words):
        subcat = dict_subcats.get(word)
        if subcat:
            all_words.pop(i)
            subcat = Subcategory.objects.get(id=subcat)
            cat = subcat.category
            break

    return cur, cat, subcat, all_words


def account_operation_validator(msg: str, user: User) -> tuple:
    '''
    Валидация сообщения на операцию по счету
    Если в сообщении нет валюты берем стандартную
    Если в сообщении нет категории возвращаем False и сообщение с запросом
    Если все в порядке возвращаем True and tuple(summ, currency, category, subcategory)
    1 - нет валюты
    2 - нет субкатегории
    3 - имя субкатегории == категории
    '''

    all_numbers = get_number(msg)
    all_words = get_words(msg)
    summa_numbers = Decimal(sum(map(float, all_numbers)))

    cur, cat, subcat, all_words = search_by_cur_and_reuctsub(all_words, user)

    if not cur:
        money_user = MoneySum.objects.filter(user=user)
        if len(money_user) == 1:
            cur = money_user[0]
        else:
            return 1, (summa_numbers, subcat, money_user)

    if not cat:
        word = all_words[0] if all_words else ''
        return 2, (cur.symbol, (summa_numbers, cur.id), word)

    if cat.name == subcat.name:
        count_subcat_in_cat = len(Subcategory.objects.filter(category=cat))
        if count_subcat_in_cat > 1:
            return 3, (cur.symbol, (cat.id, summa_numbers, cur.id))

    return 0, (summa_numbers, cur, cat, subcat)


@sync_to_async
def account_operation(telegram_id: int, message: str) -> Tuple[bool, str]:
    '''
    Получаем сообщение на операцию по счету
    '''
    # Первичная валидация и парсинг данных из сообщения и преобразование к нормальному виду
    user = Telegram.objects.get(id=telegram_id).user
    result, data = account_operation_validator(message, user)

    if result:
        if result == 3: # Отработка - имя категории совпало с субкатегорией
            return {
                'text' : f'Сумма {bn(data[1][1])} {data[0]}\nВыберете подкатегорию:',
            'reply_markup':kb.inline_choice_subcategories(data[1])
                }

        elif result == 2: # Отработка - не нашел категории
            return {
                'text': f'Сумма {bn(data[1][0])} {data[0]}\nВыберете категорию:',
                'reply_markup': kb.inline_choice_categories(telegram_id, data[1], data[2])
                }
        else: # # Отработка - не нашел валюту
            return {
                'text': f'Сумма {bn(data[0])}\nВыберете валюту:',
                'reply_markup': kb.inline_choice_currency(data)
            }

    summa_numbers, cur, cat, subcat = data
    money = MoneySum.objects.filter(user=user, currency=cur)
    if not money:
        answer = f'У вас нет в наличии "{cur.name} {cur.symbol}"\nДобавьте ее с помощью конверсионной операции.'
        return {'text' : answer}
    price_bas_cur = money[0].conversion * summa_numbers
    id_operation = account_operation_save(user, *data, price_bas_cur, message)
    account_operation_change_to_many(money[0], summa_numbers, cat.income_or_expense)
    text_sub = '' if cat.name == subcat.name else f' -> {subcat.name.capitalize()}'
    answer = f'Записал {bn(summa_numbers)} {cur.symbol}\n{cat.name.capitalize()}{text_sub}\n'
    bas_cur = user.basic_currency
    if not cur == bas_cur:
        answer += f'Это {bn(price_bas_cur)}{bas_cur.symbol}'
    return {'text' : answer, 'reply_markup': kb.inline_for_operations(id_operation, 'acc')}



def get_conversion_operation(telegram_id: int, start: datetime, out: datetime) -> List[Conversion]:
    user = Telegram.objects.get(id=telegram_id).user
    return Conversion.objects.filter(
                user=user,
                created_at__gt=start,
                created_at__lt=out).order_by('created_at')



def get_account_operation(telegram_id: int, start: datetime, out: datetime) -> List[Operation]:
    user = Telegram.objects.get(id=telegram_id).user
    return Operation.objects.filter(
                user=user,
                created_at__gt=start,
                created_at__lt=out)


def get_date_first_operation(telegram_id: int):
    user = Telegram.objects.get(id=telegram_id).user

    date = Operation.objects.filter(
                user=user).order_by('created_at')[0].created_at

    return date


def сhanging_course_and_searching_operations(operation: Conversion,
                                            ode_course: str):
    money_buy = MoneySum.objects.filter(user=operation.user,
                currency=operation.currency_buy)[0]

    money_sel = MoneySum.objects.filter(user=operation.user,
                currency=operation.currency_sell)[0]
    money_buy.amount -= operation.amount_buy
    money_buy.save()
    money_sel.amount += operation.amount_sell
    money_sel.save()

    if ode_course == '1': return
    money = MoneySum.objects.filter(user=operation.user,
                currency=operation.currency_buy)[0]

    if ode_course == '0':
        money_buy.delete()
    else:
        money_buy.conversion = Decimal(ode_course)
        money_buy.save()

    oper_list = Operation.objects.filter(
                user=operation.user,
                currency=operation.currency_buy,
                created_at__gt=operation.created_at
                ).values_list(
                    'id', 'category__name', 'currency__symbol', 'amount', 'created_at'
                    )
    if not oper_list: return
    oper_str = beautiful_account_operation(oper_list)
    return f'Эти операции были записаны по ошибочному курсу конверсии\nЛучше удалите их и внесите заново\n{oper_str}'


def delete_operation(type_operation: str, operation_id: int):
    '''
    Если есть операция удаляем ее, если нет, ну и хорошо!
    '''
    if type_operation == 'acc':
        operation = Operation.objects.filter(id=operation_id)
        if operation:
            sym = '-' if operation[0].category.income_or_expense else '+'
            money = MoneySum.objects.get(
                user=operation[0].user, currency=operation[0].currency)
            update_count_money(money, sym, operation[0].amount)
            operation[0].delete()

    else:
        operation = Conversion.objects.filter(id=operation_id)
        if operation:
            answer = сhanging_course_and_searching_operations(
                                            operation[0],
                                            type_operation)
            operation[0].delete()
            return answer





def update_date_operation(type_operation: str, operation_id: int, new_date: datetime) -> bool:
    '''
    Изменяем дату операции, возвращаем ответ с результатом,
    может не быть операции (уже удалена)
    '''

    if type_operation == 'acc':
        operation = Operation.objects.filter(id=operation_id)
    else:
        operation = Conversion.objects.filter(id=operation_id)
    if not operation:
        return False
    operation[0].created_at = new_date
    operation[0].save()
    return True


def get_summa_operation(telegram_id: int, start: datetime, out: datetime):
    acc_operation = get_account_operation(telegram_id, start, out)
    if not acc_operation:
        return 0, 0

    income = acc_operation.filter(
        category__income_or_expense=True
        ).aggregate(Sum('price_basic_currency'))['price_basic_currency__sum']
    income = income if income else 0

    expense = acc_operation.filter(
        category__income_or_expense=False
        ).aggregate(Sum('price_basic_currency'))['price_basic_currency__sum']
    expense = expense if expense else 0
    return income, expense


def get_sum_for_cat(telegram_id: int,
                    date_start: datetime,
                    date_end: datetime,
                    type_report: str='category') -> List[Tuple[str, str]]:
    '''
    Возвращаем категорию и сумму
    '''
    operation = get_account_operation(telegram_id, date_start, date_end)
    return operation.values(
        f'{type_report}__name'
        ).annotate(
            sum=Sum('price_basic_currency'
            )).values_list(
                f'{type_report}__name', 'sum'
                )

@sync_to_async
def get_detail_operation_info(operation_id: int,
                              operation_type: str) -> str:
    if operation_type == 'acc':
        operation = Operation.objects.filter(
            id=operation_id
            ).values_list(
                'category__name',
                'subcategory__name',
                'currency__symbol',
                'amount',
                'price_basic_currency',
                'user__basic_currency__symbol',
                'created_at',
                'message',
                )
        if not operation: return
        answer = create_detail_operation_sting(operation_type, operation[0])

    else:
        operation = Conversion.objects.filter(
            id=operation_id
            ).values_list(
                'currency_sell__symbol',
                'currency_buy__symbol',
                'amount_sell',
                'amount_buy',
                'price_basic_currency',
                'user__basic_currency__symbol',
                'created_at',
                'message',
                )
        if not operation: return
        answer = create_detail_operation_sting(operation_type, operation[0])
    return answer



def get_sum_operations_by_days(telegram_id: int,
                            date_start: datetime,
                            date_end: datetime) -> list:
    operations = get_account_operation(telegram_id, date_start, date_end)

    return operations.values(
        'created_at__day'
        ).annotate(
            sum=Sum('price_basic_currency')
            ).order_by('created_at__day').values_list('created_at__day', 'sum', 'user__basic_currency__symbol')
# o = Operation.objects.filter(user=1)
# l = o.values('created_at__day').annotate(sum=Sum('price_basic_currency'))


# csc_{cat_id}_{osn_id}_{summa}_{cur_id}_{word}


def write_operation_callback(sub_id, summa, cur_id, word):
    sub = Subcategory.objects.get(id=int(sub_id))
    cat = sub.category
    cur = Currency.objects.get(id=int(cur_id))
    user = cat.user
    summa = Decimal(summa)

    money = MoneySum.objects.filter(user=user, currency=cur)
    if not money:
        answer = f'У вас нет в наличии "{cur.name} {cur.symbol}"\nДобавьте ее с помощью конверсионной операции.'
        return {'text' : answer}
    price_bas_cur = money[0].conversion * summa
    msg = f'{summa} {cur.name} {sub.name} {word}'
    id_operation = account_operation_save(
        user, summa, cur, cat, sub, price_bas_cur, msg
        )
    account_operation_change_to_many(money[0], summa, cat.income_or_expense)

    text_sub = '' if cat.name == sub.name else f' -> {sub.name.capitalize()}'
    mes = f'Записал {bn(summa)} {cur.symbol}\n{cat.name.capitalize()}{text_sub}\n'
    bas_cur = user.basic_currency
    if not cur == bas_cur:
        mes += f'Это {bn(price_bas_cur)}{bas_cur.symbol}'

    answers = [{'text' : mes, 'reply_markup': kb.inline_for_operations(id_operation, 'acc')}]
    if word:
        msg = f'Можно добавить ключ "{word}"\nДля быстрой записи в {sub.name.capitalize()}'
        answers += [{'text' : msg, 'reply_markup': kb.inline_key_for_subcat(sub.id, word)}]
    return answers
