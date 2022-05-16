from dis import dis
from turtle import color
import discord 
import datetime
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
    
    embed.add_field(name="Server Owner", value="xabierprg")
    embed.add_field(name="GitHub", value="https://github.com/xabierprg/DisMusic")
    
    await ctx.send(embed=embed)
    
# Events
@bot.event
async def on_ready():
    print('My bot is ready')
    

bot.run('')
