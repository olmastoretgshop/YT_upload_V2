# importing libraries
from aiogram.dispatcher.filters.state import State, StatesGroup


# all of these are memory storages
class YT_ACC(StatesGroup):
    yt_client_id = State()
    yt_client_secret = State()


class Video_info(StatesGroup):
    vid_title = State()
    vid_desc = State()
    vid_keywords = State()
    vid_category = State()


class auth_token(StatesGroup):
    yt_auth_token = State()
