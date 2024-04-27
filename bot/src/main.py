import asyncio
import discord
from discord.ext import commands
import os
import spacy
from lib import voicevox, blacklist
from pymongo.mongo_client import MongoClient
from tinydb import TinyDB, Query

nlp: spacy.Language = spacy.load("ja_ginza")

TOKEN = os.getenv("DISCORD_TOKEN")
DEV_SERVER_ID = os.getenv("DEV_SERVER_ID")
DEV_SERVER_CHANNEL_ID = os.getenv("DEV_SERVER_CHANNEL_ID") 
# URI = os.getenv('DB_URI') mongodbだけど使ってないのでコメントアウト

# client = MongoClient(URI)
db = TinyDB('/app/db.json')

skipped_messages = []
reading_messages = {}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
activity = discord.Streaming(name="読み上げ", url="https://www.twitch.tv/puzupuzuu")

class MyBot(commands.Bot):
    async def setup_hook(self):
	    await self.tree.sync()

bot = MyBot(command_prefix='y;', intents = intents, activity = activity)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
    if message.content.startswith('y;'):
        return
    
    for i in db.all():
        try:
            id = i['channel_id']
        except KeyError:
            continue
        if i['channel_id'] == message.channel.id:
            voicechannel = message.guild.get_channel(i['voice_channel_id'])
            break
    else:
        return
    
    if message.content == 's':
        id = reading_messages[message.guild.id][0]
        skipped_messages.append(id)
        voiceclient = message.guild.voice_client
        voiceclient.stop()
        return
    
    if message.guild.voice_client is None:
        await voicechannel.connect()
    else:
        if message.guild.voice_client.channel is None:
            await voicechannel.connect()
    voiceclient = message.guild.voice_client

    content = await blacklist.overwrite(message.content)
    id = db.search(Query().user_id == message.author.id)
    if id == []:
        id = await voicevox.get_random_speaker_id()
        db.insert({'user_id': message.author.id, 'speaker_id': id})
    else:
        id = id[0]['speaker_id']
    
    if message.attachments != []:
        files = {'image': 0, 'video': 0, 'audio': 0, 'text': 0,'other': 0}
        for i in message.attachments:
            if i.content_type.startswith('image'):
                files['image'] += 1
            elif i.content_type.startswith('video'):
                files['video'] += 1
            elif i.content_type.startswith('audio'):
                files['audio'] += 1
            elif i.content_type.startswith('text'):
                files['text'] += 1
            else:
                files['other'] += 1

        if files['image'] == len(message.attachments):
            content = f'添付画像。\n{content}'

        elif files['video'] == len(message.attachments):
            content = f'添付動画。\n{content}'

        elif files['audio'] == len(message.attachments):
            content = f'添付音声。\n{content}'

        elif files['text'] == len(message.attachments):
            content = f'添付テキスト。\n{content}'
            
        else:
            content = f'添付ファイル。\n{content}'

    if message.type == discord.MessageType.reply:
        content = f'リプライ。\n{content}'
    
    reply = await parse(content)

    try:
        test = reading_messages[message.guild.id]
    except KeyError:
        reading_messages[message.guild.id] = []

    reading_messages[message.guild.id].append(message.id)

    while reading_messages[message.guild.id][0] != message.id:
        await asyncio.sleep(0.2)

    for i in reply:
        await generate_voice_from_text(i, id)
        name = hash(i)
        while voiceclient.is_playing():
            await asyncio.sleep(0.3)
        if message.id in skipped_messages:
            reading_messages[message.guild.id].remove(message.id)
            return
        voiceclient.play(discord.FFmpegPCMAudio(f'/app/voice/{id}-{name}.wav'))
    
    reading_messages[message.guild.id].remove(message.id)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.voice_client is None:
        return
    
    if member.bot:
        return
    
    if before.channel is after.channel:
        return

    voiceclient = member.guild.voice_client
    nickname = member.nick
    if member.id == 732530817334509619:
        nickname = 'きぼひか'

    if before.channel is voiceclient.channel:
        if len(before.channel.members) == 1:
            await member.guild.voice_client.disconnect()
            return
        
        else:
            await asyncio.sleep(2)
            if member.is_timed_out():
                await generate_voice_from_text(f'{nickname}さんがタイムアウトされました')
                name = hash(f'{nickname}さんがタイムアウトされました')
                while voiceclient.is_playing():
                    await asyncio.sleep(0.3)
                voiceclient.play(discord.FFmpegPCMAudio(f'/app/voice/43-{name}.wav'))
            else:
                await generate_voice_from_text(f'{nickname}さんが退出しました')
                name = hash(f'{nickname}さんが退出しました')
                while voiceclient.is_playing():
                    await asyncio.sleep(0.3)
                voiceclient.play(discord.FFmpegPCMAudio(f'/app/voice/43-{name}.wav'))
    
    if after.channel is voiceclient.channel:
        await generate_voice_from_text(f'{nickname}さんが参加しました')
        name = hash(f'{nickname}さんが参加しました')
        while voiceclient.is_playing():
            await asyncio.sleep(0.3)
        voiceclient.play(discord.FFmpegPCMAudio(f'/app/voice/43-{name}.wav'))

@bot.hybrid_command(description="miageのレイテンシを表示します")
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)}ms')

@bot.hybrid_command(description="miageが読み上げるチャンネルを表示します")
async def list(ctx):
    embed = discord.Embed(title='読み上げチャンネル一覧')
    for i in db.all():
        try:
            id = i['guild_id']
        except KeyError:
            continue
        if i['guild_id'] == ctx.guild.id:
            try:
                text_channel = discord.utils.get(ctx.guild.text_channels, id=i['channel_id'])
                voice_channel = discord.utils.get(ctx.guild.voice_channels, id=i['voice_channel_id'])
            except AttributeError:
                continue
            text_channel = f'<#{i["channel_id"]}>'
            voice_channel = f'╰→<#{i["voice_channel_id"]}>'
            embed.add_field(name=text_channel, value=voice_channel, inline=False)
    if len(embed.fields) == 0:
        embed = discord.Embed(title='読み上げチャンネル一覧', description='読み上げチャンネルがありません')
    await ctx.send(embed=embed)

@bot.hybrid_command(description="miageが読み上げるチャンネルを設定します(チャンネル編集権限が必要です)")
@commands.has_permissions(manage_channels=True)
async def link(ctx):
    if ctx.author.voice is None:
        await ctx.send('ボイスチャンネルに参加してからコマンドを実行してください')
        return
    voice_channel = ctx.author.voice.channel
    db.insert({'guild_id': ctx.guild.id, 'channel_id': ctx.channel.id, 'voice_channel_id': voice_channel.id})
    await ctx.send(f'<#{ctx.channel.id}>の読み上げ先を<#{voice_channel.id}>に設定しました')

@bot.hybrid_command(description="miageが読み上げるチャンネルを解除します(チャンネル編集権限が必要です)")
@commands.has_permissions(manage_channels=True)
async def unlink(ctx):
    db.remove(Query().channel_id == ctx.channel.id)
    await ctx.send(f'<#{ctx.channel.id}>の読み上げ先を解除しました')

async def parse(text: str):
    reply = []
    doc = nlp(text)
    for sent in doc.sents:
        reply.append(sent.text)
    return reply

@bot.hybrid_command(description="miageの声を表示します")
async def myvoice(ctx):
    id = db.search(Query().user_id == ctx.author.id)
    if id == []:
        id = await voicevox.get_random_speaker_id()
        db.insert({'user_id': ctx.author.id, 'speaker_id': id})
    else:
        id = id[0]['speaker_id']
    name = await voicevox.get_speaker_name(id)
    await ctx.send(f'あなたの声は{name}です')

@bot.hybrid_command(description="miageの声を変更します")
async def randomizemyvoice(ctx):
    id = await voicevox.get_random_speaker_id()
    db.update({'speaker_id': id}, Query().user_id == ctx.author.id)
    name = await voicevox.get_speaker_name(id)
    await ctx.send(f'あなたの声を{name}に変更しました')

@bot.command()
async def idk(ctx):
    voiceclient = ctx.guild.voice_client
    if voiceclient is None:
        return
    await voiceclient.play(discord.FFmpegPCMAudio('/app/src/wav.wav'))

async def generate_voice_from_text(text: str, speaker: int = 43):
    name = hash(text)
    for j in os.listdir('/app/voice/'):
        if j == f'{speaker}-{name}.wav':
            return
    wav = await voicevox.generate_voice(text, speaker)
    with open(f'/app/voice/{speaker}-{name}.wav', 'wb') as f:
        try:
            f.write(wav)
        except TypeError:
            return

async def load_extension():
    for filename in os.listdir('/app/src/cogs/'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    asyncio.run(load_extension())
    bot.run(TOKEN)