# importing libraries
import httplib2
from http import client


# define arrays and varieables
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

public_upload = """To upload you video as public follow these instructions:
1. <i>Enter https://studio.youtube.com/</i>
2. <i>Click 'Settings'</i>
3. <i>Click 'Channel'</i>
4. <i>Click 'Advanced Settings'</i>
5. <i>Choose 'No, my channel is not for kids and there is not child content.'</i>"""

com_register_reply = "<b>Master</b>, please give me access to your <i>YT Channel</i>"

com_watermark_reply = "Please <b>Master</b>, send me image or gif as file. I will create watermark for your videos😉😝"

note_msg = """<code>NOTE✍️:</code> I can only upload 6 video per day to <b>YouTube</b>. YouTube API gives me only 10000 credits per day.
To upload a video I use 1600 credits. And I cannot upload videos longer than 15 minutes to <b>YouTube.</b>
To be able to upload videos longer than 15 minutes you have to <a href='https://www.youtube.com/verify'>verify</a> your YouTube Channel.

video tutorial is old, from version 1:
https://github.com/olmastoretgshop/YT_upload
"""

warning_msg = """<code>WARNING⚠️:</code> Right now I am having problems deleting originally downloaded videos.
For now just redeploy or manually delete the files"""

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
31 - Anime/Animation <code>Googala is saying that 31 is not recognized, so do not use it, please,</code> <b>Master</b>
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
42 - Shorts <code>Googala is saying that 42 is not recognized, so do not use it, please,</code> <b>Master</b>
43 - Shows
44 - Trailers"""

auth_code_success = """Thank you <b>Master</b>, for giving me access to your YouTube Channel. I will not fail you.😇"""

auth_code_error = """Please <b>Master</b>, give me access to your YouTube Channel.🙏🥺"""

authorization_msg_prompt = "Please visit this URL to authorize this application: "

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, client.NotConnected, client.IncompleteRead, client.ImproperConnectionState, client.CannotSendRequest, client.CannotSendHeader, client.ResponseNotReady, client.BadStatusLine)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'yt_account.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

_OOB_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
