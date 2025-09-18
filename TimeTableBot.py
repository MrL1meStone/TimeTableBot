from os import getenv
from asyncio import run
from aiogram.filters import CommandStart,Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database import set_group, is_in

load_dotenv("BOT_TOKEN.env")
BOT_TOKEN = getenv("BOT_TOKEN")

from aiogram import Dispatcher, Bot, F

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

def get_settings_buttons(callback):
    statuses = ["🟢" if is_in(callback.message.chat.id, i) else "🔴" for i in ("Weekly", "Tomorrow", "Today")]
    keyboard = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text=f'Расписание на неделю {statuses[0]}',
         callback_data=f'turn_Weekly_{callback.message.chat.id}')],
    [InlineKeyboardButton(text=f'Расписание на завтра {statuses[1]}',
         callback_data=f'turn_Tomorrow_{callback.message.chat.id}'),
    InlineKeyboardButton(text=f'Расписание на сегодня {statuses[2]}',
         callback_data=f'turn_Today_{callback.message.chat.id}')]])
    return keyboard

async def edit_message(text :str, callback: CallbackQuery, keyboard: InlineKeyboardMarkup | None ) -> None:
    await bot.edit_message_text(text=text, message_id=callback.message.message_id,
                                chat_id=callback.message.chat.id,reply_markup=keyboard)

def protected(func):
    async def wrapper(callback: CallbackQuery):
        admins=[admin.user.id for admin in await bot.get_chat_administrators(callback.message.chat.id)]
        if callback.message.chat.type=="private" or callback.from_user.id in admins:
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


@dp.callback_query(F.data.in_(set(GROUPS)))
@protected
async def add_group(callback: CallbackQuery) -> None:
    #await callback.answer(text='Отлично, группа определена🥳',show_alert=True)
    keyboard = get_settings_buttons(callback)
    await edit_message('⚙️Настройки:', callback, keyboard)
    set_group(callback.from_user.id, callback.data)

@dp.callback_query(F.data.startswith("turn_"))
async def turn(callback: CallbackQuery):
    table = callback.data.replace('turn_','')

    keyboard = get_settings_buttons(callback)
    await edit_message('⚙️Настройки:', callback, keyboard)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
