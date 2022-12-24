from asgiref.sync import sync_to_async
# from multi_key_dict import multi_key_dict
from typing import List, Tuple
from bot.finance_bot.models.operations import write_operation_callback
from bot.finance_bot.models.operations import search_by_cur_and_reuctsub
from mainapp.models import Category, Subcategory, SubcategoryReduction
from mainapp.models import User, Telegram



def get_user_categories(telegram_id: int) -> List[Category]:
    '''
    Get all categories users by telegram id (int)
    return List[Category]
    '''
    user = Telegram.objects.get(id=telegram_id).user
    return Category.objects.filter(user=user)


def get_user_categories_and_subcategories(categories: Category) -> List[Tuple[Category, Tuple[Subcategory]]]:
    '''
    Get all categories and subcategories users by categories
    return List[Tuple[Category, Tuple[Subcategory]]]
    '''
    return [(cat, tuple([subcat
            for subcat in Subcategory.objects.filter(category=cat)]))
            for cat in categories]


def get_list_cat_and_subcat(telegram_id: int,
                            type_report: str) -> list:
    '''
    В зависимости от типа отчета возвращаем списко:
    category- [категория, категория, ...]
    subcategory [(категория, [суб кат, субкат, ...]), (...)...]
    '''
    create_list_cat = lambda cats: [cat.name for cat in cats]
    create_list_catsub = lambda cat_and_sub: [
            (cat.name, [sub.name for sub in sub_list])
            for cat, sub_list in cat_and_sub
            ]

    categories = get_user_categories(telegram_id)
    cat_income = categories.filter(income_or_expense=True)
    cat_expense = categories.filter(income_or_expense=False)
    if type_report == 'category':
        income = create_list_cat(cat_income)
        expense = create_list_cat(cat_expense)
    else:
        income_cat_and_sub = get_user_categories_and_subcategories(cat_income)
        expense_cat_and_sub = get_user_categories_and_subcategories(cat_expense)
        income = create_list_catsub(income_cat_and_sub)
        expense = create_list_catsub(expense_cat_and_sub)
    return income, expense

@sync_to_async
def answer_for_user_category(telegram_id: int) -> str:
    '''
    Prepare answers for the users, upon command '/my_categories'
    answer: category and all subcategories

    TO DO возможность через дату добавлять субкатегрии и категории
    '''
    def transformation_data(data):
        return '\n'.join([
            cat.name + ':' + ''.join([f'\n    {sub.name.capitalize()}'
            for sub in sub_list])
            for cat, sub_list in data
            ])

    user = Telegram.objects.get(id=telegram_id).user
    income = get_user_categories_and_subcategories(
        Category.objects.filter(user=user, income_or_expense=True))
    expense = get_user_categories_and_subcategories(
        Category.objects.filter(user=user, income_or_expense=False))
    imc_str = transformation_data(income)
    exp_str = transformation_data(expense)
    return f'Расходы:\n{exp_str}\n\nДоходы:\n{imc_str}'


@sync_to_async
def creating_dict_for_search_category(telegram_id: int) -> Tuple[dict]:
    '''
    Формирует 2 словаря расходы и доходы необходимых для записи операции
    '''
    user = Telegram.objects.get(id=telegram_id).user
    categories = Category.objects.filter(user=user)
    data = get_user_categories_and_subcategories(categories)
    result_dict = {}
    for cat, sub_list in data:
        for sub in sub_list:
            result_dict.update({sub.name : (cat.id, sub.id)})
    return result_dict


def get_subcat_by_catid(cat_id):
    cat = Category.objects.get(id=int(cat_id))
    subcats = Subcategory.objects.filter(category=cat).values_list('id', 'name')
    return cat.name, subcats


def get_cat_by_tg(telegram_id):
    user = Telegram.objects.get(id=telegram_id).user
    cats = Category.objects.filter(
        user=user).values_list(
            'id', 'name', 'income_or_expense').order_by(
                'income_or_expense')
    return cats


def check_for_one_sub(cat_id, summa, cur_id, word):
    cat = Category.objects.get(id=cat_id)
    subcats = Subcategory.objects.filter(category=cat)
    if len(subcats) == 1:
        answer = write_operation_callback(subcats[0].id, summa, cur_id, word)

        return True, answer
    return False, None


@sync_to_async
def save_key_for_subcategory(data):
    sub_id, word = data.split('_')[1:]
    sub = Subcategory.objects.get(id=sub_id)
    result = search_by_cur_and_reuctsub([word, ], sub.category.user)
    if not result[3]:
        return f'ОШИБКА! Ключ уже используется'
    red = SubcategoryReduction(subcategory=sub, reduction=word)
    red.save()
    return f'Успешно записал новый ключ\n{word} -> {sub.name}'
