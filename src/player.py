import pafy
import queue
from discord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

class Player():
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = queue.SimpleQueue()
            
            
    def search_video(self, search):
        videosSearch = VideosSearch(search, limit = 1)
        link = videosSearch.result().get('result')[0].get('link')
        return link
    
    
    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice.client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id[0]])
            self.song_queue[ctx.guild.id].pop(0)
            
            
    async def play_song(self, ctx, video): 
        if ctx.author.voice is None:
            return await ctx.send("You must be in a voice channel to play a song.")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        
        pafy._dislikes = 0
        song = pafy.new(self.search_video(video))
        audio = song.getbestaudio()
        source = FFmpegPCMAudio(source=audio.url, executable="../ffmpeg.exe", **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        
        
    async def next_song(self, ctx):
        if queue.qsize() != 0:
            self.play_song(ctx, queue.get())
        
        
    async def pause_song(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("The song is already paused")
            
            
    async def add_to_queue(self, ctx, song):
        if ctx.voice_client.is_playing():
            self.song_queue.append(song)
        else:
            self.play_song(ctx, song)
            
    async def leave_voice_channel(self, ctx):
        ctx.voice_client.disconnect()
