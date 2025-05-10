from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from random import shuffle


main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='Мой профиль')],
    [KeyboardButton(text='Выбор направления квиза'), KeyboardButton(text='Начать квиз')]
])

profiles_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Программирование', callback_data='prog')],
    [InlineKeyboardButton(text='ФИЗМААТ', callback_data='fizmat')],
    [InlineKeyboardButton(text='Г-г-гумаанитарии', callback_data='humanitarian')],
    [InlineKeyboardButton(text='Спорт', callback_data='sport')],
])

def set_keyboard(btns, shuffled=False):
    if shuffled:
        shuffle(btns)
    markup = ReplyKeyboardBuilder()
    for btn in btns:
        markup.add(KeyboardButton(text=btn))
    markup.adjust(2)
    return markup.as_markup(resize_keyboard=True, one_time_keyboard=True)