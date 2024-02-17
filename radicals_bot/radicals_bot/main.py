from telebot import async_telebot, types
import dotenv
import asyncio
import json
from telebot import util
from radicals import points, Point, Profile, load_data, save_data
from icecream import ic

token = dotenv.get_key('.env', 'TELEGRAM_BOT_TOKEN')
bot = async_telebot.AsyncTeleBot(token)

repeats_count = 0
token = dotenv.get_key('.env', 'TELEGRAM_BOT_TOKEN')

start_kb = util.quick_markup({'Начать': {'callback_data': '1'}})
data: dict[str: dict[str: dict[str: str]]] = load_data()


def gen_markup(point: Point, profile_name: str):
    return util.quick_markup({
        "Пропустить": {'callback_data': f'{profile_name}_{point.number}_-1'},
        "0": {"callback_data": f'{profile_name}_{point.number}_0'},
        "1": {"callback_data": f'{profile_name}_{point.number}_1'},
        "2": {"callback_data": f'{profile_name}_{point.number}_2'},
        "3": {"callback_data": f'{profile_name}_{point.number}_3'},
    }, row_width=1)


def gen_profiles_markup(profiles: list[Profile]):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for profile in profiles:
        kb.add(types.InlineKeyboardButton(text=profile.name, callback_data=f"{profile.name}"))
    kb.add(types.InlineKeyboardButton(text='Вернуться', callback_data='back_to_start'))
    return kb


dev_bio = '''15 y.o.
Python nerd
Not a true programmer yet'''
dev_buttons = util.quick_markup({
    'github': {'url': 'https://github.com/0Slmpnv0'},
    'telegram': {'url': 'https://t.me/slmpnv'},
    'reddit': {'url': 'https://www.reddit.com/user/slmpnv'},
})

expecting = False


@bot.message_handler(commands=['start', 'help', 'get_dev'])
async def handle_bullshit(message: types.Message):
    if message.text == '/help':
        await bot.send_message(message.chat.id, 'Что-то для помощи юзеру. Сам эту хуйню мне пришли, а я добавлю в бота')
    elif message.text == '/start' and str(message.from_user.id) not in data.keys():
        data[str(message.from_user.id)] = {}
        save_data(data)
        await bot.send_message(message.chat.id, 'Добро пожаловать в конструктор психологического профиля человека. '
                                                'Чтобы начать нажмите "Начать"',
                               reply_markup=util.quick_markup({"Начать": {"callback_data": "start"}}))
    elif message.text == '/start' and str(message.from_user.id) in data.keys():
        await bot.send_message(message.chat.id, 'Снова здравствуйте! Вы хотите поглядеть сохраненные '
                                                'психологические профили или создать новый?',
                               reply_markup=util.quick_markup(
                                   {
                                       "Создать новый": {"callback_data": "start"},
                                       "Просмотреть сохраненные профили": {"callback_data": "check profiles"}
                                   }))

    else:
        await bot.send_message(message.chat.id, dev_bio, reply_markup=dev_buttons)


@bot.callback_query_handler(lambda call: True)
async def handle_call_bullshit(call: types.CallbackQuery):
    global expecting
    try:
        name, point_number, count = call.data.split('_')
        point_number = int(point_number)
        count = int(count)
        if '\n' in call.message.text:
            count_old = call.message.text.split(' ')[-1]
            if count_old != count:
                if int(count) == -1:
                    count = 'Пропустить'
                text = points[point_number - 1].question + f'\nТекущий выбор: {count}'
                if call.message.text != text:
                    await bot.edit_message_text(text, call.message.chat.id, call.message.id,
                                                reply_markup=gen_markup(points[point_number - 1], name))
                data[str(call.from_user.id)][name][point_number] = count
                save_data(data)
                return
        else:
            if int(count) == -1:
                count = 'Пропустить'
            text = points[point_number - 1].question + f'\nТекущий выбор: {count}'
            if call.message.text != text:
                await bot.edit_message_text(text, call.message.chat.id, call.message.id,
                                            reply_markup=gen_markup(points[point_number-1], name))
        if count == 'Пропустить':
            count = -1
        data[str(call.from_user.id)][name][point_number] = count
        save_data(data)
        if point_number == len(points):
            await bot.send_message(call.from_user.id,
                                   'Вы ответили на все вопросы! Хотите перейти к списку профилей, или создать еще один?',
                                   reply_markup=util.quick_markup(
                                       {
                                           "Создать новый": {"callback_data": "start"},
                                           "Просмотреть сохраненные профили": {"callback_data": "check profiles"}
                                       }))
        profile = Profile(call.data)
        profile.add_points({point_number: count})
        new_point = points[point_number]
        await bot.send_message(call.from_user.id, text=new_point.question, reply_markup=gen_markup(new_point, name))
    except ValueError:
        # handle_points
        match call.data:
            case 'back_to_start':
                await bot.send_message(call.from_user.id, 'Снова здравствуйте! Вы хотите поглядеть сохраненные '
                                                          'психологические профили или создать новый?',
                                       reply_markup=util.quick_markup(
                                           {
                                               "Создать новый": {"callback_data": "start"},
                                               "Просмотреть сохраненные профили": {"callback_data": "check profiles"}
                                           }))
            case 'start':
                await bot.send_message(call.message.chat.id, 'Введите имя человека, которого мы разбираем')
                expecting = True
            case 'check profiles':
                await bot.send_message(call.message.chat.id, text='Выберите профиль для просмотра',
                                       reply_markup=gen_profiles_markup(
                                           [Profile(prof) for prof in data[str(call.from_user.id)].keys()]))
            case _:
                profile = Profile(call.data)
                profile.add_points(data[str(call.from_user.id)][call.data])
                profile.gen_graph(call)
                images = [
                    types.InputMediaPhoto(open(f'images/total_plot_for_{call.from_user.id}_{call.data}.png', 'rb')),
                    types.InputMediaPhoto(open(f'images/beh_plot_for_{call.from_user.id}_{call.data}.png', 'rb')),
                    types.InputMediaPhoto(open(f'images/app_plot_for_{call.from_user.id}_{call.data}.png', 'rb')),
                    types.InputMediaPhoto(open(f'images/surr_plot_for_{call.from_user.id}_{call.data}.png', 'rb')),
                ]
                await bot.send_media_group(call.from_user.id, images)
                profile.rm_graph(call)
                await bot.send_message(call.from_user.id, str(profile))


@bot.message_handler()
async def handle_names_and_bullshits(message: types.Message):
    global expecting
    if expecting:
        if '_' in message.text:
            await bot.send_message(message.from_user.id,
                                   'В названии не должно быть нижних подчеркиваний. Введите другое имя:')
            return
        expecting = False
        new_prof: Profile = Profile(message.text)
        new_prof.add_points()
        data[str(message.from_user.id)][message.text] = new_prof.points
        save_data(data)
        await bot.send_message(message.from_user.id, points[0].question, reply_markup=gen_markup(points[0], new_prof.name))
    else:
        await bot.send_message(message.from_user.id, 'Ничо не понял')


asyncio.run(bot.polling(non_stop=True))
