import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="-", intents=intents)

bot.load_extension('cogs.testing')

@bot.command(name='load')
async def load_cog(ctx, cog):
    bot.load_extension(f'cogs.{cog}')

@bot.command(name='unload')
async def unload_cog(ctx, cog):
    bot.unload_extension(f'cogs.{cog}')

@bot.command(name='reload')
async def reload_cog(ctx, cog):
    bot.unload_extension(f'cogs.{cog}')
    bot.load_extension(f'cogs.{cog}')

# TODO add run with env discord token