import datetime
from os import getenv
from asyncio import run
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from dotenv import load_dotenv

from database import set_group, remove_from, turn_notification, is_enabled, return_table, return_from, change_time

load_dotenv("BOT_TOKEN.env")
BOT_TOKEN = getenv("BOT_TOKEN")

from aiogram import Dispatcher, Bot, F

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

def get_settings_buttons(callback):
    statuses = ["🟢" if is_enabled(i,callback.message.chat.id) else "🔴" for i in ("Weekly", "Tomorrow", "Today")]
    keyboard = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text=f'Расписание на неделю {statuses[0]}',callback_data=f'turn_Weekly')],
    [InlineKeyboardButton(text=f'Расписание на завтра {statuses[1]}',callback_data=f'turn_Tomorrow')],
    [InlineKeyboardButton(text=f'Расписание на сегодня {statuses[2]}',callback_data=f'turn_Today')]])
    return keyboard

async def edit_message(text :str, message: Message, keyboard: InlineKeyboardMarkup | None ) -> None:
    if message.text!=text:
        await bot.edit_message_text(text=text, message_id=message.message_id,
                                chat_id=message.chat.id,reply_markup=keyboard)
    else:
        await bot.edit_message_reply_markup(message_id=message.message_id,
                                    chat_id=message.chat.id, reply_markup=keyboard)

def protected(func):
    async def wrapper(callback: CallbackQuery):
        if callback.message.chat.type=="private":
            return await func(callback)
        admins = [admin.user.id for admin in await bot.get_chat_administrators(callback.message.chat.id)]
        if callback.from_user.id in admins:
            return await func(callback)
        else:
            await callback.answer(f'⛔ Извини {callback.from_user.first_name}, '
                                  f'ты не можешь этого сделать',show_alert=True)
            return None
    return wrapper


GROUPS = ['АП1-924', 'АП1-925', 'АП2-924', 'АП2-925', 'ОД-924',
          'ОД1-925', 'ОД2-924', 'ОД2-925', 'ПД2-924', 'ПД3-925',
          'ПД4-925', 'ПД5-925', 'ПК-25', 'ПК1-24', 'ПК2-24',
          'ПК3-924', 'ПК4-924', 'ТД-924', 'ТД-925', 'ТД2-924',
          'ТД2-925', 'ТП-924', 'ТП1-925', 'ТП2-925', 'ЭМД-924',
          'ЭМД1-925', 'ЭМД2-925']

@dp.message(CommandStart())
@dp.message(Command('group'))
async def get_group(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=group, callback_data=group)] for group in GROUPS])
    await message.answer("Пожалуйста выберите группу:", reply_markup=keyboard)


@dp.message(Command('menu'))
async def command_menu(message: Message) -> None:
    keyboard=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋Получить расписание',callback_data='schedule')],
        [InlineKeyboardButton(text='⚙️Настройки',callback_data='settings')]])
    await message.answer(text='📋Вот меню действий',reply_markup=keyboard)

@dp.callback_query(F.data.in_(set(GROUPS)))
@protected
async def add_group(callback: CallbackQuery) -> None:
    await callback.answer(text='Отлично, группа определена🥳',show_alert=True)
    set_group(callback.from_user.id,callback.data)
    await callback_menu(callback)

@dp.callback_query(F.data.in_(set(GROUPS)))
@dp.callback_query(F.data=='back')
async def callback_menu(callback: CallbackQuery) -> None:
    keyboard=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋Получить расписание',callback_data='schedule')],
        [InlineKeyboardButton(text='⚙️Настройки',callback_data='settings')]])
    await edit_message('📋Вот меню действий', callback.message, keyboard)

@dp.callback_query(F.data=='schedule')
async def get_schedule_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text=f'🗓Расписание на неделю',callback_data=f'get_Weekly')],
     [InlineKeyboardButton(text=f'🗓Расписание на завтра',callback_data=f'get_Tomorrow')],
     [InlineKeyboardButton(text=f'🗓Расписание на сегодня',callback_data=f'get_Today')],
     [InlineKeyboardButton(text='◀️ Назад', callback_data='back')]])
    await edit_message('📋На какой промежуток времени нужно получить расписание?', callback.message, keyboard)

@dp.callback_query(F.data.startswith('get_'))
async def answer_schedule(callback: CallbackQuery) -> None:
    table=callback.data.replace("get_","")
    #get_schedule()
    #Здесь нужно будет получить расписание и вывести его в удобном формате

@dp.callback_query(F.data=='settings')
async def settings_menu(callback: CallbackQuery) -> None:
    keyboard=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⏯ Вкл/Выкл регулярные уведомления',callback_data='turn_notifications')],
        [InlineKeyboardButton(text='⏰Настроить время уведомлений', callback_data='notifications_time')],
        [InlineKeyboardButton(text='◀️ Назад', callback_data='back')]])
    await edit_message('⚙️Настройки', callback.message, keyboard)

@dp.callback_query(F.data.startswith("turn_"))
async def turn(callback: CallbackQuery):
    await callback.answer()
    chat_id=callback.message.chat.id
    table = callback.data.replace('turn_','')
    if table!='notifications':
        turn_notification(table, chat_id)
    statuses = ["🟢" if is_enabled(i, callback.message.chat.id) else "🔴" for i in ("Weekly", "Tomorrow", "Today")]
    keyboard = InlineKeyboardMarkup(inline_keyboard=
        [[InlineKeyboardButton(text=f'Расписание на неделю {statuses[0]}',callback_data=f'turn_Weekly')],
         [InlineKeyboardButton(text=f'Расписание на завтра {statuses[1]}',callback_data=f'turn_Tomorrow')],
         [InlineKeyboardButton(text=f'Расписание на сегодня {statuses[2]}',callback_data=f'turn_Today')],
         [InlineKeyboardButton(text='◀️ Назад', callback_data='back')]])
    await edit_message('⚙️Настройки:', callback.message, keyboard)

@dp.callback_query(F.data=='notifications_time')
async def notifications_time(callback: CallbackQuery) -> None:
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text='Расписание на неделю',callback_data=f'configure_Weekly')],
     [InlineKeyboardButton(text='Расписание на завтра',callback_data=f'configure_Tomorrow')],
     [InlineKeyboardButton(text='Расписание на сегодня',callback_data=f'configure_Today')],
     [InlineKeyboardButton(text='◀️ Назад', callback_data='back')]])
    await edit_message('⏱️Время какого уведомления вы хотите изменить?:', callback.message, keyboard)

@dp.callback_query(F.data.startswith('configure_'))
async def configure_notification(callback: CallbackQuery) -> None:
    table=callback.data.replace('configure_',"")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'+{i}', callback_data=f'delta_{i}_{table}') for i in (1, 15, 60)],
        [InlineKeyboardButton(text=f'{i}', callback_data=f'delta_{i}_{table}') for i in (-1, -15, -60)],
        [InlineKeyboardButton(text='◀️ Назад', callback_data='back')]])
    await edit_message('Настройте время уведомления:\n'
                       f'{return_from(table,callback.message.chat.id)["time"]}', callback.message, keyboard)

@dp.callback_query(F.data.startswith('delta_'))
async def plus_time(callback: CallbackQuery) -> None:
    await callback.answer()
    data = callback.data.replace('delta_', "")
    delta, table = data.split('_')
    delta = int(delta)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'+{i}', callback_data=f'delta_{i}_{table}') for i in (1, 15, 60)],
        [InlineKeyboardButton(text=f'{i}', callback_data=f'delta_{i}_{table}') for i in (-1, -15, -60)],
        [InlineKeyboardButton(text='◀️ Назад', callback_data='back')]])
    time = return_from(table,callback.message.chat.id)["time"]
    time = datetime.time(*list(map(int,time.split(":"))))
    change_time(table,callback.message.chat.id,
                datetime.time(hour=(time.hour+(time.minute+delta)//60)%24,minute=(time.minute+delta)%60))
    await edit_message('Настройте время уведомления:\n'
                       f'{return_from(table,callback.message.chat.id)["time"]}', callback.message, keyboard)

@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER))
async def bot_removed(event: ChatMemberUpdated):
    [remove_from(table,event.chat.id) for table in ("Groups","Weekly","Tomorrow","Today")]
    print("Бот был удален из группы")


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    run(main())