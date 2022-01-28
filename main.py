import discord
import os
from dotenv import load_dotenv
import urllib.parse, urllib.request, re
from discord.ext import commands
from discord.utils import get
from discord import FFmpegAudio
from discord import TextChannel
from youtube_dl import YoutubeDL

#loading env variable for privacy
load_dotenv()

#initialize the client
client = commands.Bot(command_prefix='!')

#lets dev know if the bot is ready
@client.event
async def on_ready():
    print("bot ready!")

@client.command()
async def play(ctx, *, url):
    #options for YDL and FFMPEG
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'
    }
    #Used to be part of a join command that was removed because of redundancy. 
    #when user issues play command the bot will automatically join whatever voice channel the user is in.
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    #initializes voice
    voice = get(client.voice_clients, guild=ctx.guild)

    #searches youtube using urllib and finds the first url
    query_string = urllib.parse.urlencode({
        'search_query': url
    })
    html_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
    await ctx.send('http://www.youtube.com/watch?v=' + search_results[0])
    

    #downloads the url that was searched and converts it into an mp3 using FFmpeg
    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info('http://www.youtube.com/watch?v=' + search_results[0], download=False)
            URL = info['url']
            voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            voice.is_playing()
            await ctx.send('Bot is playing')
    else:
        await ctx.send("Bot is already playing")
        return

#STOP command to stop the bot from playing music. 
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    #checks to see if the bot is playing any music, if it is the bot will leave the chat
    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')

#PAUSE command that pauses the song
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    #checks if the bot is playing any music, if it is the bot will pause
    if voice.is_playing():
        voice.pause()
        await ctx.send("Bot has been paused")

#RESUME command that resumes the song at current position
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    #checks if the bot is playing any music, if it is the bot will resume from initial position
    if not voice.is_playing():
        voice.resume()
        await ctx.send("Bot is resuming")

client.run(os.environ['TOKEN'])
