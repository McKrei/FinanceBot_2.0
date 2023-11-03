cd /home/www/FinanceBot_2.0
source venv/bin/activate
cd /home/www/FinanceBot_2.0/finance
python manage.py dumpdatautf8 --output data.json
python manage.py dump_db
