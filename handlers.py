# importing libraries
import json, time, os
from aiogram.types import Message, ContentTypes
from aiogram.dispatcher import FSMContext
from pytube import YouTube
from googleapiclient.errors import HttpError
# importing dispatcher and bot
from main import bot, dp
# importing predefined variables and arrays
from variables import message_ids, userids, video_categories, authorization_msg_prompt, creds
# importing memory storage. memory storage is assigned values that user gives
from fsm import Video_info, auth_token
# importing functions to upload video to youtube
from yt import get_authenticated_service, fetch_auth_code, build_credentials, initialize_upload
# importing another message handlers. these handlers only answer to commands
import commands
import watermark_compress
import moviepy.editor as mp


# this is message handler. video_download function. this function recieves link to  youtube video
# then downloads the video
# gathers info for the upload video
# then initializes upload
@dp.message_handler()
async def video_download(message: Message):
    # get user_id of user
    user_id = message.chat.id
    # get text of message 
    url = message.text
    # get message_id of message
    message_id = message.message_id
    # pass message_id to message_ids array. array is sort of storage for multiple strings
    message_ids.append(message_id)
    # check if message is link to youtube video
    if url.startswith("https://youtube.com/") or url.startswith("https://youtu.be/"):
        # send message to user
        await message.reply("Initiating download...")
        # pass path to directory of the video to be downloaded to userids array
        # example: if user_id of the user is 132456
        # path to directory for the file is:
        # 132456/yt
        userids.append(f"{user_id}/yt")
        try:
            yt = YouTube(url)
            # get highest resolution of the video
            yt = yt.streams.get_highest_resolution()
            # download the video to the directory and name the video as message_id
            yt.download(f"{user_id}/yt", f"{message_id}.mp4")
            # notify user that the video is downloaded
            await message.answer("Video downloaded successfully!🎉")
        except Exception as e:
            print(e)
            error_message = e
            # if there is error downloading the video
            # send message to user error message
            await message.reply(f"<b>ERROR OCCURED:</b> {error_message}", parse_mode="html")
        # wait for 3 seconds
        time.sleep(3)
        yt_vid_title = "What is the title of the video?🤔"
        # ask user for title of the video to be uploaded
        await message.answer(yt_vid_title)
        # prepare to set user's answer to vid_title variable (actually it is not variable, but whatever) in Video_info storage
        await Video_info.vid_title.set()
    elif commands:
        # call commands file
        # this file is called if the message user sent is command
        commands()
    else:
        # if message is niether link nor command
        # send message to user
        await message.reply("<b>Master!</b> Send me link to YouTube video or send the video itself, please <b>Master!🙏</b>", parse_mode="html")


@dp.message_handler(state=Video_info.vid_title)
async def yt_set_vid_title(message: Message, state: FSMContext):
    # get answer of the user
    title = message.text
    yt_vid_desc = "What is the description of the video?🤔"
    # set answer of the user to vid_title variable in Video_info storage
    await state.update_data(video_title=title)
    # ask user next question
    await message.answer(yt_vid_desc, parse_mode="html")
    # prepare next variable of Video_info storage
    await Video_info.vid_desc.set()


@dp.message_handler(state=Video_info.vid_desc)
async def yt_set_vid_desc(message: Message, state: FSMContext):
    description = message.text
    yt_vid_keywords = "What are the keywords of the video?🤔\nSend me the keywords in this form:\n<code>word1,word2,word3</code>"
    await state.update_data(video_description=description)
    await message.answer(yt_vid_keywords, parse_mode="html")
    await Video_info.vid_keywords.set()


@dp.message_handler(state=Video_info.vid_keywords)
async def yt_set_vid_keywords(message: Message, state: FSMContext):
    keywords = message.text
    category = "What is the category of the video?🤔\nThese are available video categories <i>(send me category id, example: <u>2</u>)</i>:"
    await state.update_data(video_keywords=keywords)
    await message.answer(f"{category}\n\n<i>{video_categories}</i>", parse_mode="html")
    await Video_info.vid_category.set()


@dp.message_handler(state=Video_info.vid_category)
async def yt_set_vid_category(message: Message, state: FSMContext):
    category = message.text
    await state.update_data(video_category=category)
    # call Video_info storage and get its contents
    yt_video_info = await state.get_data()
    # create yt_vid_info.json file and write yt_video_info in it
    with open("yt_vid_info.json", "w") as f:
        json.dump(yt_video_info, f, indent=4, ensure_ascii=False)
    # stop and delete contents of Video_info storage
    await state.finish()
    # notify user
    await message.answer("Successfully stored video data to be uploaded")
    time.sleep(3)
    await message.answer("Adding watermark and compressing the video...")
    # getting directory path and file name
    for dirname in userids:
        dirname = dirname
    for vidname in message_ids:
        vidname = vidname
    # defining full path to the video
    video_input = f"{dirname}/{vidname}.mp4"
    # creating object to to process the video
    clip_video = mp.VideoFileClip(video_input)
    # identifying video resolution
    width, height = clip_video.size
    # condition:
    # if video resolution is lower than hd
    # make it hd
    # if not hd
    # add watermark and compress
    if height < 1080:
        # calling resize_vid function to change video resolution
        await watermark_compress.resize_vid(message)
    else:
        # calling add_watermark function to add watermark to the video and compress
        await watermark_compress.add_watermark(message)
    # wait for 3 seconds
    time.sleep(3)
    await message.answer("Preparing video to upload...")
    # call get_authentication_service function's value
    # so basically it is getting the value the function is returning
    yt_auth_url = get_authenticated_service()[0]
    time.sleep(3)
    # send the value the function returned to user
    await message.answer(f"{authorization_msg_prompt}{yt_auth_url}")
    # prepare to set answer of the user to yt_auth_token variable of auth_token storage
    await auth_token.yt_auth_token.set()


@dp.message_handler(state=auth_token.yt_auth_token)
async def set_auth_token(message: Message, state: FSMContext):
    verify_auth_token = message.text
    await state.update_data(auth_token=verify_auth_token)
    yt_auth_code = await state.get_data()
    with open("yt_auth_code.json", "w") as yt_code:
        json.dump(yt_auth_code, yt_code, indent=4, ensure_ascii=False)
    await state.finish()
    time.sleep(3)
    await message.answer("Initializing upload...")
    # get the value fet_auth_code function is returning
    cred = fetch_auth_code()
    creds.append(cred)
    # get the value build_credentials function is returning
    youtube = build_credentials()
    try:
        # pass the value of build_credentials function to initialize_upload function
        await initialize_upload(youtube, message)
    except HttpError as e:
        # if there is HttpError
        # notify user
        await message.answer('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))


# message handler, specifically, video handler
@dp.message_handler(content_types=["video"])
async def download_video(message: Message):
    user_id = message.chat.id
    message_id = message.message_id
    message_ids.append(message_id)
    video_path = f"{user_id}/tg"
    userids.append(video_path)
    # get file_id of the file message
    # file message can be anything except text: video, photo, docx, ppt, pdf, etc.
    video_id = message.video.file_id
    # identifiy which video to download, the video will be downloaded by file_id
    video = await bot.get_file(video_id)
    # download the video, name the video as message_id of the message
    # and save the video in video_path
    await bot.download_file(video.file_path, f"{video_path}/{message_id}.mp4")
    await message.reply("Successfully download the video.🎉")
    time.sleep(3)
    tg_vid_title = "What is the title of the video?🤔"
    await message.answer(tg_vid_title)
    await Video_info.vid_title.set()


@dp.message_handler(state=Video_info.vid_title)
async def tg_set_vid_title(message: Message, state: FSMContext):
    title = message.text
    tg_vid_desc = "What is the description of the video?🤔"
    await state.update_data(video_title=title)
    await message.answer(tg_vid_desc, parse_mode="html")
    await Video_info.vid_desc.set()


@dp.message_handler(state=Video_info.vid_desc)
async def tg_set_vid_desc(messsage: Message, state: FSMContext):
    description = messsage.text
    tg_vid_keywords = "What are the keywords of the video?🤔\nSend me the keywords in this form:\n<code>word1,word2,word3</code>"
    await state.update_data(video_description=description)
    await messsage.answer(tg_vid_keywords, parse_mode="html")
    await Video_info.vid_keywords.set()


@dp.message_handler(state=Video_info.vid_keywords)
async def tg_set_vid_keywords(message: Message, state: FSMContext):
    keywords = message.text
    tg_vid_category = "What is the category of the video?🤔\nThese are available video categories <i>(send me category id, example: <u>2</u>)</i>:"
    await state.update_data(video_keywords=keywords)
    await message.answer(f"{tg_vid_category}\n\n<i>{video_categories}</i>", parse_mode="html")
    await Video_info.vid_category.set()


@dp.message_handler(state=Video_info.vid_category)
async def tg_set_vid_category(message: Message, state: FSMContext):
    category = message.text
    await state.update_data(video_category=category)
    tg_video_info = await state.get_data()
    with open("yt_vid_info.json", "w") as f:
        json.dump(tg_video_info, f, indent=4, ensure_ascii=False)
    await state.finish()
    await message.answer("Successfully stored video data to be uploaded")
    time.sleep(3)
    await message.answer("Preparing video to upload...")
    await message.answer("Adding watermark and compressing the video...")
    for dirname in userids:
        dirname = dirname
    for vidname in message_ids:
        vidname = vidname
    video_input = f"{dirname}/{vidname}.mp4"
    clip_video = mp.VideoFileClip(video_input)
    width, height = clip_video.size
    if height < 1080:
        await watermark_compress.resize_vid(message)
    else:
        await watermark_compress.add_watermark(message)
    tg_auth_url = get_authenticated_service()[0]
    time.sleep(3)
    await message.answer(f"{authorization_msg_prompt}{tg_auth_url}")
    await auth_token.yt_auth_token.set()


@dp.message_handler(state=auth_token.yt_auth_token)
async def tg_set_auth_token(message: Message, state: FSMContext):
    tg_verify_auth_token = message.text
    await state.update_data(auth_token=tg_verify_auth_token)
    tg_auth_code = await state.get_data()
    with open("yt_auth_code.json", "w") as yt_code:
        json.dump(tg_auth_code, yt_code, indent=4, ensure_ascii=False)
    await state.finish()
    time.sleep(3)
    await message.answer("Initializing upload...")
    cred = fetch_auth_code()
    creds.append(cred)
    youtube = build_credentials()
    try:
        await initialize_upload(youtube, message)
    except HttpError as e:
        await message.answer('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))


@dp.message_handler(content_types=ContentTypes.DOCUMENT)
async def set_watermark(message: Message):
    if document := message.document:
        await document.download(destination_file=f"watermarks_tg/1.png")
    await message.answer("Watermark downloaded successfully")











