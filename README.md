### dump db to json
python manage.py dumpdatautf8 --output data.json
## loaddata
python manage.py loaddatautf8 data.json

### Ошибка при установке библиотек **Пунки 2**
pip install --upgrade wheel


### Ошибка при загрузки данных **Пунки 6**
```
django.db.utils.IntegrityError: Problem installing fixture '/root/projects/FinanceBot_2.0/finance/data.json': Could not load contenttypes.ContentType(pk=19): duplicate key value violates unique constraint "django_content_type_app_label_model_76bd3d3b_uniq"
DETAIL:  Key (app_label, model)=(portfolio, asset) already exists.
```
**Решение**
1. `python manage.py shell`
```
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
```



# Запуск с нуля на новом сервере. **python version 3.10**
1. Нужно подключение к постгрес
2. Устанавливаем зависимости
3. Создать файл `.env` в `/finance/` заполнить поля из кофига
4. Миграции `python manage.py migrate`
5. Добавляем дамп в корень `/finance/`
6. Загружаем данные `python manage.py loaddatautf8 data.json`
7. Запуск приложения `python manage.py runbot`
8. Если все работает запускаем в скрине `screen`


# Создаем задачу на ежедневный дамп
1. Изменяем пути на актуальные в файле `auto_dump.sh`
2. Тестируем скрипт `source /root/projects/FinanceBot_2.0/auto_dump.sh` - Старт пути `/root/projects/` может быть другим замени
3. В крон `crontab -e` добавляем строку активации скрипта `0 0 * * * source /root/projects/FinanceBot_2.0/auto_dump.sh`
    - 0 0: минута 0 и час 0 (полночь).
