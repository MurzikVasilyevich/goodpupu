import codecs
import glob
import logging.config
import random
import re
from datetime import timedelta

import ffmpeg
import moviepy.editor as mpe
import pandas as pd
import requests
import sox
from google.cloud.texttospeech_v1beta1 import VoiceSelectionParams, AudioConfig, AudioEncoding, \
    SynthesizeSpeechRequest, SynthesisInput, TextToSpeechClient, SsmlVoiceGender
from gtts import gTTS
from internetarchive import search_items, download
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import *
from srt import Subtitle, compose

import settings as s

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app.py')


def text_to_ssml(t):
    text_split = re.findall(r'[\w\s\'\-\,]+', t)
    ret = {"text": text_split}
    text_ssml = []
    for i in range(len(text_split)):
        text_ssml.append(f"<mark name=\"{i}\"/>{text_split[i]}")
    text_joined = f"<speak>{'.'.join(text_ssml)}.<mark name=\"{i + 1}\"/></speak>"
    ret['ssml'] = text_joined
    return ret


def create_voice_srt(language, t):
    logger.info(f"Creating audio for {language}")
    voice_file = os.path.join(s.SOUND_FOLDER, f"{language}.mp3")
    srt_file = os.path.join(s.VIDEO_FOLDER, f"{language}.srt")
    en_srt = os.path.join(s.VIDEO_FOLDER, f"en.srt")
    language_codes = {"en": "en-US", "uk": "uk-UA", "ru": "ru-RU"}

    client = TextToSpeechClient()
    tex = text_to_ssml(t)
    synthesis_input = SynthesisInput(ssml=tex["ssml"])
    voice = VoiceSelectionParams(language_code=language_codes[language],
                                 ssml_gender=random.choice(list(SsmlVoiceGender)))
    audio_config = AudioConfig(audio_encoding=AudioEncoding.MP3)
    request = SynthesizeSpeechRequest(input=synthesis_input, voice=voice, audio_config=audio_config,
                                      enable_time_pointing=[SynthesizeSpeechRequest.TimepointType.SSML_MARK])
    response = client.synthesize_speech(request=request)
    time_points = list(response.timepoints)
    with open(voice_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{voice_file}"')
    subs = []
    for i in range(len(time_points) - 1):
        point = time_points[i]
        point_next = time_points[i + 1]
        subs.append(Subtitle(
            index=int(point.mark_name),
            start=timedelta(seconds=point.time_seconds + s.AUDIO_START),
            end=timedelta(seconds=point_next.time_seconds - 0.2 + s.AUDIO_START),
            content=tex['text'][i]
        ))
    composed = compose(subs)
    with codecs.open(srt_file, "w", "utf-8") as out:
        out.write(composed)
        print(f'Subtitles written to file {srt_file}')
    return voice_file, srt_file, en_srt


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
    offs = random.randint(1, 100)
    url = f"http://ccmixter.org/api/query?f=csv&dataview=links_dl&limit=30&offset={offs}&type=instrumentals"
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
                       params={"rows": 50, "page": random.randint(1, 200)},
                       fields=['identifier', 'item_size', 'downloads'])
    item = random.choice(list(res))
    download(item['identifier'], verbose=True, glob_pattern="*.mp4", destdir=s.VIDEO_FOLDER, no_directory=True)
    os.rename(glob.glob(os.path.join(s.VIDEO_FOLDER, "*.mp4"))[0], s.VIDEO_BACK_NAME)


def create_clip(language, text):
    music_file = get_music()
    voice_file, srt_file, en_srt = create_voice_srt(language, text)
    print(f"Creating clip for {language}")

    out_clip = f"./videos/{language}.mp4"
    srt_out_clip = f"./videos/{language}_srt.mp4"
    my_clip = mpe.VideoFileClip(s.VIDEO_BACK_NAME)
    audio_background = AudioFileClip(voice_file)
    music_background = AudioFileClip(music_file)
    music_background = audio_normalize(music_background)
    music_background = audio_fadein(music_background, 1)
    music_background = audio_fadeout(music_background, 2)
    music_background = volumex(music_background, 0.2)
    music_background.duration = audio_background.duration + 3
    logger.info(f"Clip duration: {my_clip.duration}")
    logger.info(f"Audio duration: {audio_background.duration}")
    if my_clip.duration > audio_background.duration:
        start = random.randint(0, int(my_clip.duration - audio_background.duration))
        my_clip = my_clip.subclip(start, start + audio_background.duration)
    else:
        my_clip = my_clip.loop(duration=audio_background.duration)
    my_clip.resize(width=480)

    final_audio = mpe.CompositeAudioClip([audio_background.set_start(s.AUDIO_START), music_background])
    final_audio.duration = audio_background.duration + 3
    final_clip = my_clip.set_audio(final_audio)
    final_clip.duration = audio_background.duration + 3
    final_clip.write_videofile(out_clip, temp_audiofile='temp-audio.m4a', remove_temp=True,
                               codec="libx264", audio_codec="aac")
    video = ffmpeg.input(out_clip)
    audio = video.audio
    ffmpeg.concat(video.filter("subtitles", en_srt), audio, v=1, a=1).output(srt_out_clip).run(overwrite_output=True)
    return srt_out_clip
