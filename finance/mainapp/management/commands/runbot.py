from datetime import datetime

from django.core.management.base import BaseCommand

from mainapp.models import User, Category
from bot import runbot

class Command(BaseCommand):
    help = 'Запускаем телеграмм бот!'


    def handle(self, *args, **kwargs):
        runbot()
