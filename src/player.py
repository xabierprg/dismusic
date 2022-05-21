import pafy
import asyncio
import queue
import spotipy
import discord
import datetime
from random import shuffle
from spotipy.oauth2 import SpotifyClientCredentials
from discord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

class Player():
    def __init__(self, bot):
        self.bot = bot
        self.playing = ""
        self.song_queue = queue.SimpleQueue()
        
    def read_properties(self):
        global CLIENT_ID
        global CLIENT_SECRET

        f = open("../.properties", "r")
        lines = f.readlines()

        CLIENT_ID = lines[2].replace("\n", "").replace("SPOTIFY_CLIENT_ID=", "")
        CLIENT_SECRET = lines[3].replace("\n", "").replace("SPOTIFY_CLIENT_SECRET=", "")
        
            
    def search_video(self, search):
        self.playing = search
        videosSearch = VideosSearch(search, limit = 1)
        link = videosSearch.result().get('result')[0].get('link')
        return link
    
    def search_playlist(self, uri):
        self.read_properties()
        client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
        playlist_URI = uri.split("/")[-1].split("?")[0]
        
        songlist = []
        for track in sp.playlist_tracks(playlist_URI)["items"]:
            track_name = track["track"]["name"]
            artist_name = track["track"]["artists"][0]["name"]
            songlist.append(artist_name + " " + track_name)
        return songlist
    
    
    async def loop(self, ctx):
        try:
            while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await asyncio.sleep(3)

                if ((not ctx.voice_client.is_playing()) and (not ctx.voice_client.is_paused())):
                    print("NEXT")
                    await self.next_song(ctx)
                    return   
        except AttributeError:
            pass
    
            
    async def play_song(self, ctx, video): 
        if ctx.author.voice is None:
            return await ctx.send("You must be in a voice channel to play a song.")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            
        if ctx.voice_client.is_playing():
            await self.pause_song(ctx)
            
        if "https://open.spotify.com/playlist/" in video:
            songlist = self.search_playlist(video)
            for s in songlist:
                self.song_queue.put(s)
            await self.next_song(ctx)

            
            
        song = pafy.new(self.search_video(video))
        audio = song.getbestaudio()
        source = FFmpegPCMAudio(source=audio.url, executable="../ffmpeg.exe", **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        await self.loop(ctx)
                    
        
    async def next_song(self, ctx):
        if not self.song_queue.empty():
            await self.play_song(ctx, self.song_queue.get())
        else:
            await ctx.send("*The queue is empty*")
        
        
    async def pause_song(self, ctx):
        if not ctx.voice_client.is_playing():
            await ctx.send("*There is no song playing*")
        
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("*The song is already paused*")
            
            
    async def resume_song(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.send("*The song is already resumed*")
            
            
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
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
                
        if ctx.voice_client.is_playing():
            if "https://open.spotify.com/playlist/" in song:
                songlist = self.search_playlist(song)
                for s in songlist:
                    self.song_queue.put(s)
                return
        else:
            if "https://open.spotify.com/playlist/" in song:
                songlist = self.search_playlist(song)
                for s in songlist:
                    self.song_queue.put(s)
                await self.next_song(ctx)
            else:
                await self.play_song(ctx, song)
        
        
    async def shuffle_queue(self, ctx):
        song_list = []
        
        while True:
            if self.song_queue.qsize() == 0:
                break
            song_list.append(self.song_queue.get())            
        
        shuffle(song_list)
        self.song_queue = queue.SimpleQueue()
        [self.song_queue.put(i) for i in song_list]
        await ctx.send("*The queue was shuffled*")
        

    async def show_playing_song(self, ctx):
        await ctx.send("**Playing:** " + self.playing)
        
        
    async def show_queue(self, ctx):
        song_list = ""
        songs = []
        oversize = True
        
        while True:
            if self.song_queue.qsize() == 0:
                break
            
            songs.append(self.song_queue.get())

        self.song_queue = queue.SimpleQueue()
        [self.song_queue.put(i) for i in songs]
        
        for i in range(25):
            if songs == len(songs):
                oversize = False
                break
            song_list += songs[i]  + "\n"      
            
        songs.clear()
        
        embed = discord.Embed(
            title=f"Tracks from queue",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Playing", value=self.playing, inline=False)
        
        if oversize:
            embed.add_field(name="In queue", value=song_list + "\n...", inline=False)
        else:
            embed.add_field(name="In queue", value=song_list, inline=False)
        
        await ctx.send(embed=embed)
        
            
    async def clear_queue(self, ctx):
        self.song_queue = queue.SimpleQueue()
        await ctx.send("*The queue was cleared*")
        
        