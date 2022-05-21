import discord
import datetime
from discord.ext import commands
from player import Player


bot = commands.Bot(command_prefix="-")
player = Player(bot)


@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title=f"DisMusic",
        description="Im a music player bot",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.purple(),
    )

    embed.add_field(name="Server Owner", value="xabierprg#5284", inline=False)
    embed.add_field(name="GitHub", value="https://github.com/xabierprg/DisMusic", inline=False)
    embed.add_field(name="Commands", value="paste '-commands' to see all commands", inline=False)

    await ctx.send(embed=embed)
    
    
@bot.command()
async def commands(ctx):
    embed = discord.Embed(
        title=f"Commands",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.purple()
    )
        
    embed.add_field(name="-play", value="play the song specified after the command", inline=False)
    embed.add_field(name="-add", value="add a song to the queue", inline=False)
    embed.add_field(name="-pause", value="pause the song", inline=False)
    embed.add_field(name="-resume", value="resume the paused song", inline=False)
    embed.add_field(name="-skip", value="skip a song in the queue", inline=False)
    embed.add_field(name="-shuffle", value="shuffle the queue", inline=False)
    embed.add_field(name="-show", value="show the songs in the queue", inline=False)
    embed.add_field(name="-playing", value="show the playing track name", inline=False)
    embed.add_field(name="-stop", value="stop the player and clear the queue", inline=False)
    embed.add_field(name="-clear", value="clear the queue", inline=False)
    
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print("Logged in as:\n{0.user.name}\n{0.user.id}".format(bot))    

@bot.command()
async def play(ctx,* ,song):        
    await player.play_song(ctx, song)
    
@bot.command()
async def add(ctx,* ,song):
    await player.add_to_queue(ctx, song)
    
@bot.command()
async def pause(ctx):
    await player.pause_song(ctx)
    
@bot.command()
async def resume(ctx):
    await player.resume_song(ctx)
    
@bot.command()
async def skip(ctx):
    await player.skip_song(ctx)
    
@bot.command()
async def shuffle(ctx):
    await player.shuffle_queue(ctx)
    
@bot.command()
async def show(ctx):
    await player.show_queue(ctx)
    
@bot.command()
async def playing(ctx):
    await player.show_playing_song(ctx)
    
@bot.command()
async def stop(ctx):
    await player.stop_player(ctx)
    
@bot.command()
async def clear(ctx):
    await player.clear_queue(ctx)


def read_properties():
    global TOKEN
    global OWNER_ID

    f = open("../.properties", "r")
    lines = f.readlines()

    TOKEN = lines[0].replace("\n", "").replace("TOKEN=", "")
    OWNER_ID = lines[1].replace("\n", "").replace("OWNER_ID=", "")


read_properties()
bot.run(TOKEN)
