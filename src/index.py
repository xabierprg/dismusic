import discord
import datetime
import re
from urllib import parse, request
from discord.ext import commands


bot = commands.Bot(command_prefix='-', description='Im a music player bot')
             
# Commands
@bot.command()
async def ping(ctx):
    await ctx.send('pong')
    
@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"DisMusic", 
                          description="Im a music player bot", 
                          timestamp=datetime.datetime.utcnow(), 
                          color=discord.Color.purple())
    
    embed.add_field(name="Server Owner", value="xabierprg#5284")
    embed.add_field(name="GitHub", value="https://github.com/xabierprg/DisMusic")
    
    await ctx.send(embed=embed)
    
@bot.command()
async def youtube(ctx, *, search):
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
    search_results = re.findall('href=\"\\/watch\\?v=(.{11})', html_content.read().decode())
    await ctx.send(search_results)
    
# Events
@bot.event
async def on_ready():
    print('My bot is ready')
    
# Read the Discord bot token and the owner id from the .properties file.
# Creates two global variables (TOKEN and OWNER_ID).
def read_properties():
    global TOKEN
    global OWNER_ID
    
    f = open("../.properties", "r")
    lines = f.readlines()   
    
    TOKEN = lines[0].replace('\n', '').replace('TOKEN=', '')
    OWNER_ID = lines[1].replace('\n', '').replace('OWNER_ID=', '')
    

read_properties()
bot.run(TOKEN)
