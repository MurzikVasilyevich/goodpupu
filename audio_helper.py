import os

import pandas as pd
import requests
import sox
from deep_translator import GoogleTranslator
from gtts import gTTS
import moviepy.editor as mpe
from internetarchive import search_items, download
import random
import glob

import settings as s
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def add_background_music(lang, voice_file):
    logger.info("Adding background music")
    music_file = get_music()
    combined_file = os.path.join(s.SOUND_FOLDER, f"{lang}_m.mp3")
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


def text_to_speech(lang, text):
    logger.info(f"Creating audio for {lang}")
    voice_file = os.path.join(s.SOUND_FOLDER, f"{lang}.mp3")
    tts_file = gTTS(text=text, lang=lang, slow=False)
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
    res = search_items('collection:(moviesandfilms) AND mediatype:(movies) AND format:(mpeg4)',
                       params={"rows": 500, "page": 1},
                       fields=['identifier', 'item_size', 'downloads'])
    item = random.choice(list(filter(lambda x: x["item_size"] < 10000000000, res)))
    logger.info(item)
    download(item["identifier"], glob_pattern="*.mp4", no_directory=True, verbose=True, destdir="videos", checksum=True, formats="MPEG4")
    video_file = glob.glob("./videos/*.mp4")[0]
    return video_file


def create_clip(lang, audio_file):
    video_file = get_video()
    out_clip = f"./videos/{lang}.mp4"
    my_clip = mpe.VideoFileClip(video_file)
    audio_background = mpe.AudioFileClip(audio_file)
    logger.info(f"Clip duration: {my_clip.duration}")
    logger.info(f"Audio duration: {audio_background.duration}")
    if my_clip.duration > audio_background.duration:
        start = random(0, int(my_clip.duration - audio_background.duration))
        my_clip = my_clip.subclip(start, start+audio_background.duration)
    else:
        my_clip = my_clip.loop(duration=audio_background.duration)
    my_clip.resize(width=480)
    final_audio = mpe.CompositeAudioClip([audio_background])
    final_clip = my_clip.set_audio(final_audio)
    final_clip.write_videofile(out_clip, codec='mpeg4')
    return out_clip


