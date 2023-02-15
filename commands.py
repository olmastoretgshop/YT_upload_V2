# importing libraries
import json, os
from main import bot, dp
from config import tutorial
from aiogram.types import Message, MediaGroup, InputFile
from aiogram.dispatcher import FSMContext
from variables import com_start_reply, com_obey_reply, note_msg, com_register_reply, userids, message_ids, \
    public_upload, warning_msg, com_watermark_reply
from fsm import YT_ACC


# message hander, spacifically, command handler
@dp.message_handler(commands="start")
async def bot_start(messsage: Message):
    await messsage.reply(f"{com_start_reply}", parse_mode="html")


@dp.message_handler(commands="obey")
async def bot_obey(messsage: Message):
    # MediaGroup is for group photos
    public_vid = MediaGroup()
    # this one is attaching photos and writing caption
    public_vid.attach_photo(InputFile('images/studio.jpg'), public_upload, parse_mode="html")
    public_vid.attach_photo(InputFile('images/studio_channel.jpg'))
    await messsage.reply_video(tutorial, caption=f"{com_obey_reply}\n\n{note_msg}\n\n{warning_msg}", parse_mode="html")
    # sending photos as group
    await messsage.answer_media_group(public_vid)


# message handler to gather information to be able to connect this bot to your youtube channel
@dp.message_handler(commands="login")
async def yt_bot_register(message: Message):
    email_request = "What is your 📧client id?"
    await message.reply(f"{com_register_reply}\n\n{email_request}", parse_mode="html")
    await YT_ACC.yt_client_id.set()


@dp.message_handler(state=YT_ACC.yt_client_id)
async def set_email(message: Message, state: FSMContext):
    email = message.text
    password_request = "What is your 👀client secret?"
    await state.update_data(yt_client_id=email)
    await message.answer(password_request)
    await YT_ACC.yt_client_secret.set()


@dp.message_handler(state=YT_ACC.yt_client_secret)
async def set_password(message: Message, state: FSMContext):
    password = message.text
    await state.update_data(yt_client_secret=password)
    yt_account_data = await state.get_data()
    client_secret = {
        "web": {
            "client_id": yt_account_data['yt_client_id'],
            "client_secret": yt_account_data['yt_client_secret'],
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    with open("yt_account.json", "w") as f:
        json.dump(client_secret, f, indent=4, ensure_ascii=False)
    await state.finish()
    await message.answer("Successfully stored you account data!🎉")


# message handler to delete the video it downloaded and already uploaded to youtube
# recommended to delete the video
@dp.message_handler(commands="delete")
async def delete_vid_file(message: Message):
    for dir_name in userids:
        dir_name = dir_name
    for file_name in message_ids:
        os.remove(f"{dir_name}/{file_name}_yt.mp4")
    await message.reply("Videos deleted successfully!")


@dp.message_handler(commands="watermark")
async def set_watermark(message: Message):
    await message.reply(com_watermark_reply)


