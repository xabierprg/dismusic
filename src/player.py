import pafy
import asyncio
import queue
import spotipy
import discord
import datetime
from random import shuffle
from spotipy.oauth2 import SpotifyClientCredentials
from discord import FFmpegPCMAudio
import os
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch


"""Music player manager"""
class Player:
    
    def __init__(self, bot):
        self.bot = bot  # bot main object
        self.playing = ""  # current playing song
        self.song_queue = queue.SimpleQueue()  # song queue variable
        self.SPOTIFY_CLIENT_ID = ""
        self.SPOTIFY_CLIENT_SECRET = ""
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}  # ffmpeg options
        

    """Search the video url from the input field"""
    def search_video(self, search):
        videos_search = VideosSearch(search, limit=1)
        link = videos_search.result().get('result')[0].get('link')
        self.playing = videos_search.result().get('result')[0].get('title')
        return link
            
    
    """Make a list with the names of the songs from the playlist"""
    @staticmethod
    def search_playlist(uri):
        load_dotenv()
        SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        playlist_URI = uri.split("/")[-1].split("?")[0]
        
        song_list = []
        for track in sp.playlist_items(playlist_URI)["items"]:
            track_name = track["track"]["name"]
            artist_name = track["track"]["artists"][0]["name"]
            song_list.append(artist_name + " - " + track_name)
        return song_list
    
    
    """Loop that detects when the player isn't playing a song and has no paused songs"""
    async def loop(self, ctx):
        try:
            while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await asyncio.sleep(3)

                if (not ctx.voice_client.is_playing()) and (not ctx.voice_client.is_paused()):
                    await self.next_song(ctx)
                    return   
        except AttributeError:
            pass
    
            
    """Play the song from the input field"""
    async def play_song(self, ctx, video): 
        if ctx.author.voice is None:
            return await ctx.send("*You must be in a voice channel to play a song.*")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            
        if ctx.voice_client.is_playing():
            await self.pause_song(ctx)
            
        if "https://open.spotify.com/playlist/" in video:
            song_list = self.search_playlist(video)
            for s in song_list:
                self.song_queue.put(s)
            await self.next_song(ctx)

        song = pafy.new(self.search_video(video))
        audio = song.getbestaudio()
        source = FFmpegPCMAudio(source=audio.url, before_options=self.FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        await self.loop(ctx)
                    
        
    """Skip the current song detecting if the queue is empty"""
    async def next_song(self, ctx):
        if not self.song_queue.empty():
            await self.play_song(ctx, self.song_queue.get())
        else:
            self.playing = ""
            
        
    """Pause the current song"""
    @staticmethod
    async def pause_song(ctx):
        if not ctx.voice_client.is_playing():
            await ctx.send("*There is no song playing*")
        
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send("*The song is already paused*")
            
    
    """Resume the paused song"""
    @staticmethod
    async def resume_song(ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            await ctx.send("*The song is already resumed*")


    """Skip the current song detecting if the song is playing or the queue is empty"""
    async def skip_song(self, ctx):
        if self.song_queue.empty():
            await ctx.send("*The queue is empty*")
            return
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        await self.next_song(ctx)
        
            
    """Stop the player and disconnects the bot"""
    async def stop_player(self, ctx):
        self.song_queue = queue.SimpleQueue()
        self.playing = ""

        if ctx.voice_client.is_connected():
            await self.pause_song(ctx)
            await ctx.voice_client.disconnect()
        
    
    """Add a song or a playlist to the queue"""
    async def add_to_queue(self, ctx, song):
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
                
        if ctx.voice_client.is_playing():
            if "https://open.spotify.com/playlist/" in song:
                song_list = self.search_playlist(song)
                for s in song_list:
                    self.song_queue.put(s)
                return
            else:
                videos_search = VideosSearch(song, limit=1)
                self.song_queue.put(videos_search.result().get('result')[0].get('title'))
        else:
            if "https://open.spotify.com/playlist/" in song:
                song_list = self.search_playlist(song)
                for s in song_list:
                    self.song_queue.put(s)
                await self.next_song(ctx)
            else:
                await self.play_song(ctx, song)
        
        
    """Shuffle the current queue"""
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
        
        
    """Show the current playing song"""
    async def show_playing_song(self, ctx):
        await ctx.send("**Playing:**  " + self.playing)
        
    
    """Show the current queue and playing song"""
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
        
        if not len(songs) == 0:
            for i in range(25):
                song_list += songs[i] + "\n"
                
                if i+1 == len(songs):
                    oversize = False
                    break
                
        else:
            song_list = "No track in queue"    
            oversize = False
            
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
        
    
    """Clear the current song queue"""
    async def clear_queue(self, ctx):
        self.song_queue = queue.SimpleQueue()
        await ctx.send("*The queue was cleared*")
        
        