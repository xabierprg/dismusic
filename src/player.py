import pafy
import asyncio
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
    
            
    async def play_song(self, ctx, video): 
        if ctx.author.voice is None:
            return await ctx.send("You must be in a voice channel to play a song.")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            
        if ctx.voice_client.is_playing():
            await self.pause_song(ctx)
            
        song = pafy.new(self.search_video(video))
        audio = song.getbestaudio()
        source = FFmpegPCMAudio(source=audio.url, executable="../ffmpeg.exe", **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        await self.loop(ctx)
        
        
    async def loop(self, ctx):
        try:
            while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await asyncio.sleep(3)
                    
                print("2")
                            
                if ((not ctx.voice_client.is_playing()) and (not ctx.voice_client.is_paused())):
                    print("NEXT")
                    await self.next_song(ctx)
                        
        except AttributeError:
            pass
                    
        
        
    async def next_song(self, ctx):
        if not self.song_queue.empty():
            await self.play_song(ctx, self.song_queue.get())
        else:
            await ctx.send("The queue is empty")
        
        
    async def pause_song(self, ctx):
        if not ctx.voice_client.is_playing():
            await ctx.send("The is no song playing")
        
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("The song is already paused")
            
            
    async def resume_song(self, ctx):
        if not ctx.voice_client.is_playing():
            ctx.voice_client.resume()
        else:
            await ctx.send("The song is already resumed")
            
            
    async def skip_song(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        await self.next_song(ctx)
        
            
    async def stop_player(self, ctx):
        if ctx.voice_client.is_connected():
            self.song_queue = queue.SimpleQueue()
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        
            
    async def add_to_queue(self, ctx, song):
        if ctx.voice_client.is_playing():
            self.song_queue.put(song)
        else:
            await self.play_song(ctx, song)
        
            
    async def clear_queue(self, ctx):
        self.song_queue = queue.SimpleQueue()
        await ctx.send("The queue was cleared")
        

