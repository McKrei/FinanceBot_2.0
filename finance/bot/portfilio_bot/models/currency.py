from asgiref.sync import sync_to_async
from multi_key_dict import multi_key_dict

from mainapp.models import Currency
from mainapp.models import CurrencyReduction




def get_dict_currency_reduction() -> dict:
    '''
    get list currency and all reduction keys
    {'Рубль': ['руб', 'р', 'r', 'rub'], ...}
    '''
    return {cur.name : [key.reduction
            for key in CurrencyReduction.objects.filter(currency=cur)]
            for cur in Currency.objects.all()}




''' variables be used '''
dict_currency_reduction = get_dict_currency_reduction()
dict_currency_reduction_for_search = multi_key_dict()

for value, key_list in dict_currency_reduction.items():
    dict_currency_reduction_for_search[key_list] = value
