### dump db to json
python -Xutf8 manage.py dumpdata > data.json
python -Xutf8 ./manage.py dumpdata --exclude auth.permission --exclude contenttypes > db.json
## loaddata
python manage.py loaddata data.json

### Ошибка при установке библиотек
pip install --upgrade wheel
