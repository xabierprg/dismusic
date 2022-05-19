import discord
import datetime
from discord.ext import commands
from player import Player


bot = commands.Bot(command_prefix="-", description="Im a music player bot")
player = Player(bot)

# Commands
@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title=f"DisMusic",
        description="Im a music player bot",
        timestamp=datetime.datetime.utcnow(),
        color=discord.Color.purple(),
    )

    embed.add_field(name="Server Owner", value="xabierprg#5284")
    embed.add_field(name="GitHub", value="https://github.com/xabierprg/DisMusic")

    await ctx.send(embed=embed)


@bot.command()
async def play(ctx,* ,song):        
    await player.play_song(ctx, song)
    
@bot.command()
async def add(ctx,* ,song):
    await player.add_song(ctx, song)
    
@bot.command()
async def pause(ctx):
    await player.pause_song(ctx)

# Events
@bot.event
async def on_ready():
    print("Logged in as:\n{0.user.name}\n{0.user.id}".format(bot))


# Read the Discord bot token and the owner id from the .properties file.
# Creates two global variables (TOKEN and OWNER_ID).
def read_properties():
    global TOKEN
    global OWNER_ID

    f = open("../.properties", "r")
    lines = f.readlines()

    TOKEN = lines[0].replace("\n", "").replace("TOKEN=", "")
    OWNER_ID = lines[1].replace("\n", "").replace("OWNER_ID=", "")


read_properties()
bot.run(TOKEN)
