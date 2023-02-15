# importing libraries
import os
from variables import userids, message_ids
import moviepy.editor as mp
from aiogram.types import Message


# get watermark
watermark = "watermarks_tg/1.png"


async def add_watermark(message: Message):
    await message.answer("Adding watermark to the video")
    for dirname in userids:
        dirname=dirname
    for vidname in message_ids:
        vidname=vidname
    # full path to the video to be edited
    vidpath = f"{dirname}/{vidname}.mp4"
    video_clip = mp.VideoFileClip(vidpath)
    # position watermark
    img_watermark = (mp.ImageClip(watermark).set_duration(video_clip.duration).resize(height=300).set_pos('bottom'))
    # add watermark to the video
    vid_watermark = mp.CompositeVideoClip([video_clip, img_watermark])
    # output name of the edited video
    video_watermark = f"{vidpath[:-4]}_watermark.mp4"
    # create the video itself
    vid_watermark.subclip(0).write_videofile(video_watermark)
    # pass the video name to compress_vid function
    await compress_vid(video_watermark, message)

async def compress_vid(video_watermark, message: Message):
    await message.answer("Please be patient\nCompressing the video before upload...")
    # create object to compress the video with watermark
    vid_watermark = mp.VideoFileClip(video_watermark)
    # set video resolution
    vid_compress = vid_watermark.resize(height=1080)
    for dirname in userids:
        dirname=dirname
    for vidname in message_ids:
        video_compress = f"{dirname}/{vidname}_yt.mp4"
    vid_compress.write_videofile(video_compress)
    await message.answer("Video compressed successfully!")
    # delete the video with watermark
    os.remove(video_watermark)


async def add_watermark_2(video_resize, message: Message):
    await message.answer("Adding watermark to the video")
    vid_resize = mp.VideoFileClip(video_resize)
    img_watermark_2 = (mp.ImageClip(watermark).set_duration(vid_resize.duration).resize(height=300).set_pos('bottom'))
    vid_watermark_2 = mp.CompositeVideoClip([vid_resize, img_watermark_2])
    video_watermark_2 = f"{video_resize[:-4]}_watermark.mp4"
    vid_watermark_2.subclip(0).write_videofile(video_watermark_2)
    await compress_vid_2(video_watermark_2, video_resize, message)

async def compress_vid_2(video_watermark_2, video_resize, message: Message):
    await message.answer("Please be patient\nCompressing the video before upload...")
    vid_watermark = mp.VideoFileClip(video_watermark_2)
    vid_compress_2 = vid_watermark.resize(height=1080)
    for dirname in userids:
        dirname=dirname
    for vidname in message_ids:
        video_compress_2 = f"{dirname}/{vidname}_yt.mp4"
    vid_compress_2.write_videofile(video_compress_2)
    await message.answer("Video compressed successfully!")
    os.remove(video_watermark_2)
    os.remove(video_resize)

async def resize_vid(message: Message):
    await message.answer("Changing video resolution")
    for dirname in userids:
        dirname=dirname
    for vidname in message_ids:
        vidname=vidname
    vidpath = f"{dirname}/{vidname}.mp4"
    video_clip = mp.VideoFileClip(vidpath)
    vid_resize = video_clip.resize(height=1080)
    video_resize = f"{vidpath[:-4]}_resized.mp4"
    vid_resize.write_videofile(video_resize)
    await add_watermark_2(video_resize, message)









