import glob
import logging.config
import os
import random
import xml.etree.ElementTree as ET
import moviepy.editor as mpe
from moviepy.audio.AudioClip import AudioClip



import pandas as pd
import requests
import sox
from gtts import gTTS, lang
from internetarchive import search_items, download
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.io.AudioFileClip import AudioFileClip

import settings as s

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def add_background_music(language, voice_file):
    logger.info("Adding background music")
    music_file = get_music()
    combined_file = os.path.join(s.SOUND_FOLDER, f"{language}_m.mp3")
    cbn = sox.Combiner()
    cbn.set_input_format(file_type=['mp3', 'mp3'])
    seconds = sox.file_info.duration(voice_file)
    rate = sox.file_info.sample_rate(voice_file)
    trn = sox.Transformer()
    trn.trim(0, seconds)
    trn.fade(fade_in_len=1, fade_out_len=2)
    music_file_trimmed = music_file.replace('.mp3', '_trimmed.mp3')
    trn.set_output_format(rate=rate)
    trn.build(music_file, music_file_trimmed)
    cbn.build([voice_file, music_file_trimmed], combined_file, 'mix', input_volumes=[1, 0.2])
    logger.info("Added")
    return combined_file


def text_to_speech(language, text):
    logger.info(f"Creating audio for {language}")
    voice_file = os.path.join(s.SOUND_FOLDER, f"{language}.mp3")
    tts_file = gTTS(text=text, lang=language, slow=False)
    tts_file.save(voice_file)
    return voice_file


def get_music():
    logger.info("Downloading random music")
    url = "http://ccmixter.org/api/query?f=csv&dataview=links_dl&limit=30&type=instrumentals"
    df = pd.read_csv(url)
    audio_url = df.sample(1).iloc[0]['download_url']
    payload = {}
    headers = {
        'Referer': 'http://ccmixter.org/'
    }
    filename = os.path.join(s.SOUND_FOLDER, audio_url.split("/")[-1])
    r = requests.get(audio_url, payload, headers=headers)
    open(filename, 'wb').write(r.content)
    logger.info(filename)
    return filename


def get_video():
    res = search_items('collection:(movies) AND mediatype:(movies) AND format:(mpeg4)',
                       params={"rows": 50, "page": random.randint(1, 20)},
                       fields=['identifier', 'item_size', 'downloads'])
    item = random.choice(list(res))
    download(item['identifier'], verbose=True, glob_pattern="*.mp4", destdir=s.VIDEO_FOLDER, no_directory=True)
    os.rename(glob.glob(os.path.join(s.VIDEO_FOLDER, "*.mp4"))[0], s.VIDEO_BACK_NAME)


def create_clip(language, text):
    music_file = get_music()
    voice_file = text_to_speech(language, text)
    out_clip = f"./videos/{language}.mp4"
    my_clip = mpe.VideoFileClip(s.VIDEO_BACK_NAME)
    audio_background = AudioFileClip(voice_file)
    music_background = AudioFileClip(music_file)
    audio_fadein(music_background, 1)
    audio_fadeout(music_background, 2)
    volumex(music_background, 0.2)
    music_background.duration = audio_background.duration
    logger.info(f"Clip duration: {my_clip.duration}")
    logger.info(f"Audio duration: {audio_background.duration}")
    if my_clip.duration > audio_background.duration:
        start = random.randint(0, int(my_clip.duration - audio_background.duration))
        my_clip = my_clip.subclip(start, start + audio_background.duration)
    else:
        my_clip = my_clip.loop(duration=audio_background.duration)
    my_clip.resize(width=480)
    final_audio = mpe.CompositeAudioClip([audio_background, music_background])
    final_clip = my_clip.set_audio(final_audio)
    final_clip.write_videofile(out_clip, temp_audiofile='temp-audio.m4a', codec="libx264", audio_codec="aac")
    return out_clip
