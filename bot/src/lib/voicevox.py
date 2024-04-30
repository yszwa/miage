import aiohttp
import random
endpoint = 'http://voicevox:50021/'

async def generate_voice(text: str, speaker: str):
    headers = {'Content-Type': 'application/json'}
    url = endpoint + 'audio_query?' + 'text=' + text + '&speaker=' + str(speaker)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as response:
            if response.status != 200:
                print('Error:', response.status)
                return
            else:
                query = await response.json()

    url = endpoint + f'synthesis?speaker={speaker}&enable_interrogative_upspeak=true'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=query) as response:
            if response.status != 200:
                print('Error:', response.status)
                return
            else:
                # ここでDiscord用の音声ファイルに変換
                wav = await response.read()
                return wav

async def get_speakers():
    url = endpoint + 'speakers'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print('Error:', response.status)
                return
            else:
                speakers = await response.json()
                return speakers

async def get_speaker_name(speaker_id: int):
    speakers = await get_speakers()
    for speaker in speakers:
        for style in speaker['styles']:
            if style['id'] == speaker_id:
                return speaker['name']

async def get_random_speaker_id():
    speakers = await get_speakers()
    return random.choice(speakers)['styles'][0]['id']