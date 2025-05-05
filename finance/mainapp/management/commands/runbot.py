import threading
import time
from datetime import datetime, time as dtime, timedelta

from django.core.management.base import BaseCommand
from django.core.management import call_command

from bot import runbot

class Command(BaseCommand):
    help = 'Запускаем телеграмм бот и делаем дампы раз в сутки!'

    def handle(self, *args, **kwargs):
        # Стартуем поток для дампов
        dump_thread = threading.Thread(target=self.dump_scheduler, daemon=True)
        dump_thread.start()

        # Запускаем бота (он будет работать в главном потоке)
        runbot()

    def dump_scheduler(self):
        """Фоновая задача: делает дампы каждый день в 00:00 UTC."""
        while True:
            now = datetime.utcnow()
            target = datetime.combine(now.date(), dtime(00, 00))

            if now >= target:
                # Уже после 12:00 — следующий день
                target += timedelta(days=1)

            wait_seconds = (target - now).total_seconds()
            print(f'Ждем {wait_seconds} секунд до следующего дампа...')

            time.sleep(wait_seconds)

            # Выполняем дампы
            self.do_dumps()

    def do_dumps(self):
        print('Создаем дамп базы данных...')
        call_command('dumpdata', format='json', output='data.json')
        print('Дамп базы данных сохранен в data.json')

        call_command('dump_db')
        print('Дамп базы отправлен в ТГ')
