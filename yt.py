# importing libraries
import json, time, random
from variables import _OOB_REDIRECT_URI, creds, \
    userids, message_ids, CLIENT_SECRETS_FILE, \
    SCOPES, API_SERVICE_NAME, API_VERSION, \
    RETRIABLE_STATUS_CODES, RETRIABLE_EXCEPTIONS, MAX_RETRIES
from aiogram.types import Message
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow


# generate link to authorize this bot's request to connect to your youtube channel
def get_authenticated_service(**kwargs):
    # create object
    # honestly, I don't know what this does
    # but I know it is important
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri=_OOB_REDIRECT_URI)
    kwargs.setdefault("prompt", "consent")
    url = flow.authorization_url(**kwargs)
    return url

# get authorization token and connect to the channel
def fetch_auth_code():
    # read and get data from yt_auth_code.json file
    with open("yt_auth_code.json", "r") as yt_token:
        data = json.loads(yt_token.read())
        auth_code = data['auth_token']
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri=_OOB_REDIRECT_URI)
        flow.fetch_token(code=auth_code)
        return flow.credentials

# i don't know what this code does, but it is important
# it allows this bot to upload videos to youtube
def build_credentials():
    for cred in creds:
        credentials = cred
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# prepare video and video info to upload to youtube
async def initialize_upload(youtube, message):
    with open("yt_vid_info.json", "r") as vid_data:
        vid_info = json.loads(vid_data.read())
        tags = None
        if vid_info['video_keywords']:
            tags = vid_info['video_keywords'].split(',')
        # set video info from yt_vid_info.json to body dictionary
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
        # prepare video and video info
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(f"{user_id}/{message_id}_yt.mp4", chunksize=-1, resumable=True)
        )
    # pass inesrt_request to resumable upload functino
    await resumable_upload(insert_request, message)

async def resumable_upload(request, message: Message):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            processing = "Uploading file..."
            await message.answer(processing)
            # think this is uploading video to youtube
            status, response = request.next_chunk()
            if response is not None:
                # i think this is checking if video is uploaded
                # then it notifies and sends the user link to the video
                if 'id' in response:
                    success = 'Video id https://youtu.be/%s/ was successfully uploaded.' % response['id']
                    delete = 'Please send /delete command to delete video file I downloaded to upload, <b>Master</b>'
                    await message.answer(success + "\n\n" + delete, parse_mode="html")
                else:
                    # send the user error message
                    exiting = 'The upload failed with an unexpected response: %s' % response
                    await message.answer(exiting)
        # this is something that prepares to error message if there is error
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            # send error message to user
            await message.answer(error)
            retry += 1
            if retry > MAX_RETRIES:
                # another error message
                exiting2 = 'No longer attempting to retry.'
                await message.answer(exiting2)

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            sleeping = 'Sleeping %f seconds and then retrying...' % sleep_seconds
            await message.answer(sleeping)
            time.sleep(sleep_seconds)
