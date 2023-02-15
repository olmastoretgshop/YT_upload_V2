# importing libraries
import logging
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# this is storage. it stores data that user gives.
storage = MemoryStorage()
# i don't know what this is. i guess this is how bots are structured
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


# this is logging. it simply prints information in terminal
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)


# this function imports message handlers and starts the bot.
if __name__ == "__main__":
    from handlers import dp
    executor.start_polling(dp)
