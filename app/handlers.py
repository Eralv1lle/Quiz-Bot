from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from time import sleep
import json
import time

from quiz import questions, profiles
from app.keyboard import main_keyboard, profiles_inline_kb, set_keyboard


router = Router()

class QuizStates(StatesGroup):
    waiting_for_answer = State()

with open(r"C:\Users\IT Academy\PycharmProjects\Quiz-Bot\data.json", 'r', encoding='utf-8') as file:
    data = json.load(file)

last_questions = {}

def save_data():
    with open(r"C:\Users\IT Academy\PycharmProjects\Quiz-Bot\data.json", 'w', encoding='utf-8') as input_file:
        json.dump(data, input_file, ensure_ascii=False, indent=2)


@router.message(CommandStart())
async def start_message(message: Message):
    if message.from_user.first_name not in data:
        data[message.from_user.first_name] = {
            'profile': '(не указано)',
            'solved_quizs': 0,
            'correct_answers': 0
        }
        data[message.from_user.first_name]['questions'] = questions[data[message.from_user.first_name]['profile']]
        save_data()
    await message.answer('Привет! Выбирай интересующую тебя тему и решай квиз!', reply_markup=main_keyboard)


@router.message(Command('help'))
async def check_cmd(message: Message):
    await message.answer('Это бот, квиз-викторина, где ты можешь проверить свои знания в разных областях!')


@router.message(F.text == 'Мой профиль')
async def get_message(message: Message):
    await message.answer(f'МОЙ ПРОФИЛЬ\n\nИмя: {message.from_user.first_name}\nID: {message.from_user.id}\n\nНаправление: {data[message.from_user.first_name]['profile']}\nРешённых тестов: {data[message.from_user.first_name]['solved_quizs']}\nКол-во правильных ответов: {data[message.from_user.first_name]['correct_answers']}')


@router.message(F.text == 'Выбор направления квиза')
async def choose_profile(message: Message):
    await message.delete()
    await message.answer('Выберите интересующее направление:', reply_markup=profiles_inline_kb)


@router.message(F.text == 'Начать квиз')
async def start_quiz(message: Message, state: FSMContext):
    data[message.from_user.first_name]['number_question'] = 0
    data[message.from_user.first_name]['score'] = 0
    data[message.from_user.first_name]['alert'] = ''
    data[message.from_user.first_name]['start_time'] = time.time()
    last_questions[message.from_user.first_name] = {'last_question': None}
    if data[message.from_user.first_name]['profile'] == '(не указано)':
        await message.answer('Пожалуйста, укажите направление квиза')
    else:
        await state.set_state(QuizStates.waiting_for_answer)
        last_questions[message.from_user.first_name]['last_question'] = await message.answer(f'{data[message.from_user.first_name]['number_question']+1} вопрос!\n\n{data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['question']}', reply_markup=set_keyboard(shuffled=True, btns=data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['options']))
    save_data()

async def process_quiz(message: Message, state: FSMContext):
    if data[message.from_user.first_name]['number_question'] == 10:
        sleep(0.5)
        await last_questions[message.from_user.first_name]['last_question'].delete()
        await message.delete()
        sleep(0.5)
        await message.answer(f'Вопрос {data[message.from_user.first_name]['number_question']}: ' + data[message.from_user.first_name]['alert'], parse_mode='markdown')
        sleep(0.5)
        await message.answer(f'Поздравляю! Вы завершили квиз!\n\nВаш результат: {data[message.from_user.first_name]['score']}/10\nВы прошли квиз за {round(time.time() - data[message.from_user.first_name]['start_time'], 2)} сек.', reply_markup=main_keyboard)
        data[message.from_user.first_name]['number_question'] = 0
        data[message.from_user.first_name]['score'] = 0
        data[message.from_user.first_name]['solved_quizs'] += 1
        del data[message.from_user.first_name]['score']
        del data[message.from_user.first_name]['number_question']
        del last_questions[message.from_user.first_name]['last_question']
        del data[message.from_user.first_name]['start_time']
        await state.clear()
    else:
        sleep(0.5)
        await last_questions[message.from_user.first_name]['last_question'].delete()
        await message.delete()
        sleep(0.5)
        await message.answer(f'Вопрос {data[message.from_user.first_name]['number_question']}: ' + data[message.from_user.first_name]['alert'], parse_mode='markdown')
        sleep(0.5)
        last_questions[message.from_user.first_name]['last_question'] = await message.answer(f'{data[message.from_user.first_name]['number_question']+1} вопрос!\n\n{data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['question']}', reply_markup=set_keyboard(shuffled=True, btns=data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['options']))
    save_data()

@router.message(QuizStates.waiting_for_answer)
async def check_answer(message: Message, state: FSMContext):
    alert = f'Неправильно ❌, верный ответ: *{data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['correct_ans']}*'
    if message.text == data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['correct_ans']:
        data[message.from_user.first_name]['score'] += 1
        data[message.from_user.first_name]['correct_answers'] += 1
        alert = f'Верно ✅, *{data[message.from_user.first_name]['questions'][data[message.from_user.first_name]['number_question']]['correct_ans']}*'
    data[message.from_user.first_name]['alert'] = alert
    data[message.from_user.first_name]['number_question'] += 1
    await process_quiz(message, state)
    save_data()

@router.callback_query()
async def change_profile(callback: CallbackQuery):
    await callback.answer(f'Вы выбрали направление {profiles[callback.data]} ✅')
    data[callback.from_user.first_name]['profile'] = profiles[callback.data]
    data[callback.from_user.first_name]['questions'] = questions[callback.data]
    await callback.message.delete()