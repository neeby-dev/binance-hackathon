import re

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from config.constants import *
from config.config import telegram_token
from config.states import CheckAddress

from api import get_nft_bsc, get_nft_eth


bot = Bot(token=telegram_token)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Ethereum", callback_data="eth")
    button2 = types.InlineKeyboardButton(text="Binance", callback_data="bsc")
    keyboard.add(button1, button2)
    await message.answer(text=start_message, reply_markup=keyboard)


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(text=help_message)


@dp.message_handler(commands=["cancel"], state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer(text="Cancelled", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(text="eth")
async def get_eth_address(call: types.CallbackQuery):
    await CheckAddress.eth.set()
    await call.message.edit_text(text=enter_message)


@dp.callback_query_handler(text="bsc")
async def get_bsc_address(call: types.CallbackQuery):
    await CheckAddress.bsc.set()
    await call.message.edit_text(text=enter_message)


@dp.message_handler(regexp="^0x[a-fA-F0-9]{40}$", state=CheckAddress.eth)
async def check_eth_address(message: types.Message, state: FSMContext):
    info = await get_nft_eth(address=message.text.lower())
    text_message = "".join([f'[{key}]({value})\n' for (key, value) in info.items()])
    if text_message != "":
        await message.answer(text=f"NFTs on this address:\n\n{text_message}\nLimit: 50", parse_mode=ParseMode.MARKDOWN,
                             disable_web_page_preview=True)
    else:
        await message.answer(text="You don't have NFTs")
    await state.finish()


@dp.message_handler(regexp="^0x[a-fA-F0-9]{40}$", state=CheckAddress.bsc)
async def check_bsc_address(message: types.Message, state: FSMContext):
    info = await get_nft_bsc(address=message.text.lower())
    text_message = "".join([f'[{key}]({value})\n' for (key, value) in info.items()])
    if text_message != "":
        await message.answer(text=f"NFTs on this address:\n\n{text_message}\nLimit: 50", parse_mode=ParseMode.MARKDOWN,
                             disable_web_page_preview=True)
    else:
        await message.answer(text="You don't have NFTs")
    await state.finish()


@dp.message_handler(lambda message: not re.match("^0x[a-fA-F0-9]{40}$", message.text), state=CheckAddress.eth)
async def get_eth_invalid(message: types.Message):
    await message.answer(text=fail_eth_message)


@dp.message_handler(lambda message: not re.match("^0x[a-fA-F0-9]{40}$", message.text), state=CheckAddress.bsc)
async def get_bsc_invalid(message: types.Message):
    await message.answer(text=fail_bsc_message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
