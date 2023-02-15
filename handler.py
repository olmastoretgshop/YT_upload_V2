import os, requests, json, time, httplib2, random, subprocess
from main import bot, dp
from aiogram.types import Message
from pytube import YouTube, exceptions
from pytube.exceptions import VideoUnavailable
from bs4 import BeautifulSoup
from urllib.request import urlopen
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from http import client
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from shlex import split


httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, client.NotConnected, client.IncompleteRead, client.ImproperConnectionState, client.CannotSendRequest, client.CannotSendHeader, client.ResponseNotReady, client.BadStatusLine)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'yt_account.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


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


userids = []
message_ids = []
creds = []

com_start_reply = """Hello, <b>Master!</b>

I am you <i>servant😇</i> and I will obey you, <b>Master!</b>
Please allow me to upload videos to your YouTube channel, <b>Master🥺🙏</b>"""
com_obey_reply = """Yes, Master! I will!
🫴
🫳
Please send me a link to any YouTube video or send me the video itself. I will upload it to your YouTube channel."""
com_register_reply = "<b>Master</b>, please give me access to your <i>YT Channel</i>"
note_msg = """<code>NOTE✍️:</code> I can only upload 6 video per day to <b>YouTube</b>. YouTube API gives me only 10000 credits per day.
To upload a video I use 1600 credits. And I cannot upload videos longer than 15 minutes to <b>YouTube.</b>
To be able to upload videos longer than 15 minutes you have to <a href='https://www.youtube.com/verify'>verify</a> your YouTube Channel."""
video_categories =  """1 - Film & Animation
2 - Autos & Vehicles
10 - Music
15 - Pets & Animals
17 - Sports
18 - Short Movies
19 - Travel & Events
20 - Gaming
21 - Videoblogging
22 - People & Blogs
23 - Comedy
24 - Entertainment
25 - News & Politics
26 - Howto & Style
27 - Education
28 - Science & Technology
29 - Nonprofits & Activism
30 - Movies
31 - Anime/Animation
32 - Action/Adventure
33 - Classics
34 - Comedy
35 - Documentary
36 - Drama
37 - Family
38 - Foreign
39 - Horror
40 - Sci-Fi/Fantasy
41 - Thriller
42 - Shorts
43 - Shows
44 - Trailers"""
auth_code_success = """Thank you <b>Master</b>, for giving me access to your YouTube Channel. I will not fail you.😇"""
auth_code_error = """Please <b>Master</b>, give me access to your YouTube Channel.🙏🥺"""
authorization_msg_prompt = "Please visit this URL to authorize this application: "


_OOB_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def get_authenticated_service(**kwargs):
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri=_OOB_REDIRECT_URI)
    kwargs.setdefault("prompt", "consent")
    url = flow.authorization_url(**kwargs)
    return url

def fetch_auth_code():
    with open("yt_auth_code.json", "r") as yt_token:
        data = json.loads(yt_token.read())
        auth_code = data['auth_token']
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri=_OOB_REDIRECT_URI)
        flow.fetch_token(code=auth_code)
        return flow.credentials

def build_credentials():
    for cred in creds:
        credentials = cred
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

async def initialize_upload(youtube, message):
    with open("yt_vid_info.json", "r") as vid_data:
        vid_info = json.loads(vid_data.read())
        tags = None
        if vid_info['video_keywords']:
            tags = vid_info['video_keywords'].split(',')

        body=dict(
            snippet=dict(
                title=vid_info['video_title'],
                description=vid_info['video_description'],
                tags=tags,
                categoryId=vid_info['video_category']
            ),
            status=dict(
                privacyStatus='public'
            )
        )
    for value in userids:
        user_id = value
    for message_id in message_ids:
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(f"{user_id}/{message_id}.mp4", chunksize=-1, resumable=True)
        )

    await resumable_upload(insert_request, message)

async def resumable_upload(request, message: Message):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            processing = "Uploading file..."
            await message.answer(processing)
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    success = 'Video id https://youtu.be/%s/ was successfully uploaded.' % response['id']
                    await message.answer(success)
                else:
                    exiting = 'The upload failed with an unexpected response: %s' % response
                    await message.answer(exiting)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            await message.answer(error)
            retry += 1
            if retry > MAX_RETRIES:
                exiting2 = 'No longer attempting to retry.'
                await message.answer(exiting2)

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            sleeping = 'Sleeping %f seconds and then retrying...' % sleep_seconds
            await message.answer(sleeping)
            time.sleep(sleep_seconds)
    for value in userids:
        user_id = value
    for message_id in message_ids:
        os.remove(f"{user_id}/{message_id}.mp4")  # this should delete video from directory


@dp.message_handler(commands="start")
async def bot_start(messsage: Message):
    await messsage.reply(f"{com_start_reply}", parse_mode="html")


@dp.message_handler(commands="obey")
async def bot_obey(messsage: Message):
    await messsage.reply(f"{com_obey_reply}\n\n{note_msg}", parse_mode="html")


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


@dp.message_handler()
async def video_download(message: Message):
    user_id = message.chat.id
    url = message.text
    message_id = message.message_id
    message_ids.append(message_id)
    if url.startswith("https://youtube.com/") or url.startswith("https://youtu.be/"):
        await message.reply("Initiating download...")
        userids.append(f"{user_id}/yt")
        try:
            yt = YouTube(url)
            yt = yt.streams.get_highest_resolution()
            yt.download(f"{user_id}/yt", f"{message_id}.mp4")
            await message.answer("Video downloaded successfully!🎉")
        except Exception as e:
            print(e)
            error_message = e
            await message.reply(f"<b>ERROR OCCURED:</b> {error_message}", parse_mode="html")
        
        time.sleep(3)
        yt_vid_title = "What is the title of the video?🤔"
        await message.answer(yt_vid_title)
        await Video_info.vid_title.set()
    else:
        await message.reply("<b>Master!</b> Send me link to YouTube video or send the video itself, please <b>Master!🙏</b>", parse_mode="html")


@dp.message_handler(state=Video_info.vid_title)
async def yt_set_vid_title(message: Message, state: FSMContext):
    title = message.text
    yt_vid_desc = "What is the description of the video?🤔"
    await state.update_data(video_title=title)
    await message.answer(yt_vid_desc, parse_mode="html")
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
    yt_video_info = await state.get_data()
    with open("yt_vid_info.json", "w") as f:
        json.dump(yt_video_info, f, indent=4, ensure_ascii=False)
    await state.finish()
    await message.answer("Successfully stored video data to be uploaded")
    time.sleep(3)
    await message.answer("Preparing video to upload...")
    yt_auth_url = get_authenticated_service()[0]
    time.sleep(3)
    await message.answer(f"{authorization_msg_prompt}{yt_auth_url}")
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
    cred = fetch_auth_code()
    creds.append(cred)
    youtube = build_credentials()
    try:
        await initialize_upload(youtube, message)
    except HttpError as e:
        await message.answer('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))


@dp.message_handler(content_types=["video"])
async def download_video(message: Message):
    user_id = message.chat.id
    message_id = message.message_id
    message_ids.append(message_id)
    video_path = f"{user_id}/tg"
    userids.append(video_path)
    video_id = message.video.file_id
    video = await bot.get_file(video_id)
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





