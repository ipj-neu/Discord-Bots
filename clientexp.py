import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
	for guild in client.guilds:
		if guild.name == GUILD:
			break
	print(f'Connected to {guild.name}...')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if 'are you alive' in message.content.lower():
		await message.channel.send('I think so')

client.run(TOKEN)