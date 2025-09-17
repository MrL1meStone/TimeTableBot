from os import getenv
from asyncio import run
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from database import set_group

load_dotenv("BOT_TOKEN.env")
BOT_TOKEN = getenv("BOT_TOKEN")

from aiogram import Dispatcher, Bot, F

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def edit_message(text :str, callback: CallbackQuery, keyboard: InlineKeyboardMarkup | None ) -> None:
    await bot.edit_message_text(text=text, message_id=callback.message.message_id,
                                chat_id=callback.message.chat.id,reply_markup=keyboard)

GROUPS = ['АП1-924', 'АП1-925', 'АП2-924', 'АП2-925', 'ОД-924',
          'ОД1-925', 'ОД2-924', 'ОД2-925', 'ПД2-924', 'ПД3-925',
          'ПД4-925', 'ПД5-925', 'ПК-25', 'ПК1-24', 'ПК2-24',
          'ПК3-924', 'ПК4-924', 'ТД-924', 'ТД-925', 'ТД2-924',
          'ТД2-925', 'ТП-924', 'ТП1-925', 'ТП2-925', 'ЭМД-924',
          'ЭМД1-925', 'ЭМД2-925']


@dp.message(CommandStart)
async def get_group(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=group, callback_data=group)] for group in GROUPS])
    await message.answer("Привет, чтобы получать ежедневное расписание,"
                         " пожалуйста выберите группу:", reply_markup=keyboard)


@dp.callback_query(F.data.in_(set(GROUPS)))
async def add_group(callback: CallbackQuery) -> None:
    await callback.answer(text='Отлично, группа отпределена🥳',show_alert=True)
    keyboard=InlineKeyboardMarkup(inline_keyboard=
        [[InlineKeyboardButton(text='Расписание на неделю',callback_data='turn_weekly')],
         [InlineKeyboardButton(text='Расписание на завтра',callback_data='turn_tomorrow'),
        InlineKeyboardButton(text='Расписание на сегодня',callback_data='turn_today')]])
    await edit_message('Настройки:',callback,keyboard)
    #print(str((callback.message.date+timedelta(hours=5)).time()))
    set_group(callback.from_user.id, callback.data)




async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())
