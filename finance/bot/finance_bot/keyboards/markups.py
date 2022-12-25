from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



but_menu = KeyboardButton('Меню')
only_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(but_menu)

''' ######### Главное меню ######### '''
but_report_menu = KeyboardButton('Отчеты')
but_limit_menu = KeyboardButton('Лимиты')
money_menu = KeyboardButton('Деньги')
invest = KeyboardButton('Инвестиции')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(
	but_report_menu,
	but_limit_menu,
	money_menu,
	invest
	)

''' ######### Отчет ######### '''
report_menu = ReplyKeyboardMarkup(resize_keyboard=True)\
	.row(\
		# KeyboardButton('День'),
		# KeyboardButton('Неделя'),
		KeyboardButton('Месяц'),
		KeyboardButton('Год'))\
	.add(KeyboardButton('Выбрать Месяц!'))\
	.add(but_menu)

''' ######### Выбор месяцы ######### '''
choice_month_menu = ReplyKeyboardMarkup(resize_keyboard=True)\
	.row(\
		KeyboardButton('Январь'),
		KeyboardButton('Февраль'),
		KeyboardButton('Март'),
		KeyboardButton('Апрель'))\
	.row(\
		KeyboardButton('Май'),
		KeyboardButton('Июнь'),
		KeyboardButton('Июль'),
		KeyboardButton('Август'))\
	.row(\
		KeyboardButton('Сентябрь'),
		KeyboardButton('Октябрь'),
		KeyboardButton('Ноябрь'),
		KeyboardButton('Декабрь'))\
	.add(but_menu)

''' ######### Выбор года ######### '''
#TO DO
