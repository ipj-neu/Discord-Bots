import discord
from discord.ext import commands
from random import randint

class Monster(object):
	def __init__(self, name, health, init):
		self.name = name
		self.health = health
		self.starting_health = health
		self.init = init
		self.bloody = False
		self.updated = False

	def check_bloody(self):
		if self.health <= self.starting_health // 2:
			self.bloody = True
		return self.bloody

class Player(object):
	def __init__(self, name, init, dex_mod, ac):
		self.name = name
		self.init = init
		self.dex_mod = dex_mod
		self.ac = ac
		self.bloody = False

#Base vars
border = '> ---------------------------------------------------'
pc = {'BubbleSpike': Player('Finch Valor', None, 4, 15), 'xNoteKlix': Player('Guy Novak', None, 1, 15), 'Zonks!': Player('Theodore Bjord', None, 5, 15), 'Cobalt': Player('Maximilian Ceremdela', None, 4, 16)}
combat_list = []
initiative = []
playerready = False
dmready = False
dm_channel = 'combat'
player_channel = 'dice-roll'
player_vc = 'campaign'
general = 'gamer'
songs = ['The Elder Scrolls V - Skyrim - Combat 1', 'The Witcher 3 OST - Hunt or Be Hunted (Extended)', 'd&d Battle music', 'DOOM - HELL AWAITS US  Dark Powerful Battle Music - 1-Hour Full Mix']

def order_init():
	global initiative
	initiative = sorted(combat_list, key=lambda actor: actor.init, reverse=True)
	for actor in range(len(initiative)):
		if type(initiative[actor]) == Player:
			for actor2 in range(len(initiative[:actor])):
				if initiative[actor].init == initiative[actor2].init:
					if type(initiative[actor2]) == Monster:
						initiative.insert(actor2, initiative.pop(actor))
						break
					else:
						if initiative[actor].dex_mod > initiative[actor2].dex_mod:
							initiative.insert(actor2, initiative.pop(actor))
							break

def print_init(initiative, for_player):
	printversion = []
	printversion.append(border)
	for i in range(len(initiative)):
		printversion.append(f"> {i + 1}.   {f'***BLOODY***   ' if type(initiative[i]) is Monster and initiative[i].bloody else ''}**{initiative[i].name:}**,   {initiative[i].init}{f'   **HP:**   {initiative[i].health}' if type(initiative[i]) is Monster and not for_player else ''}{f'   **AC:**   {initiative[i].ac}' if type(initiative[i]) is Player and not for_player else ''}")
	printversion.append(border)
	printversion = '\n'.join(printversion)
	return printversion

#Bot Setup
TOKEN = 'ODA0NDU5NTA0NDIyMDkyODIw.YBMpSw.2X76PDCVFUcL7KkDTMY-_GFySVE'
GUILD = 'My Bot Testing Server'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)

#Events
@bot.event
async def on_ready():
	global dm_channel
	global player_channel
	global player_vc
	global general
	for guild in bot.guilds:
		if guild.name == GUILD:
			break

	for channel in guild.text_channels:
		if channel.name == dm_channel:
			dm_channel = channel
			break

	for channel in guild.text_channels:
		if channel.name == player_channel:
			player_channel = channel
			break

	for channel in guild.voice_channels:
		if channel.name == player_vc:
			player_vc = channel
			break
	
	for channel in guild.voice_channels:
		if channel.name == general:
			general = channel
			break

	print(f'{bot.user.name} has connected to {guild.name}!\nDM Channel: {dm_channel.name} ID: {dm_channel.id}\nPlayer Channel: {player_channel.name} ID: {player_channel.id}\nPlayer VC: {player_vc.name} ID: {player_vc.id}')

#Player Commands
@bot.command(name='p', help='Input player initiative, initiative')
@commands.has_role('player')
async def player(ctx, args: int):
	global playerready
	if pc[ctx.author.name] in combat_list:
		pc[ctx.author.name].init = args
	else:
		pc[ctx.author.name].init = args
		combat_list.append(pc[ctx.author.name])
	await player_channel.send(f'> {pc[ctx.author.name].name}: {pc[ctx.author.name].init}')
	pnum = 0
	for actor in combat_list:
		if type(actor) is Player:
			pnum += 1
			if pnum >= len(pc):
				playerready = True
	if playerready and dmready:
		order_init()
		await dm_channel.send(f' {print_init(initiative, False)}')
		await player_channel.send(f' {print_init(initiative, True)}')

#DM Commands
@bot.command(name='m', help='Monster Initiative: name, health, initiatives')
@commands.has_role('DM')
async def monster(ctx, name, health: int, *init: int):
	for i in init:
		combat_list.append(Monster(name, health, i))

@bot.command(name='r', help='DM has finished entering monsters')
@commands.has_role('DM')
async def dm_ready(ctx):
	global dmready
	dmready = True
	if playerready and dmready:
		order_init()
		await dm_channel.send(f' {print_init(initiative, False)}')
		await player_channel.send(f' {print_init(initiative, True)}')

@bot.command(name='s', help='Subtract monster health: health, list of monster numbers')
@commands.has_role('DM')
async def subtract_monster_health(ctx, amount: int, *monster: int):
	for actor in monster:
		initiative[actor - 1].health -= amount
		if initiative[actor - 1].check_bloody() and not initiative[actor - 1].updated:
			await player_channel.send(f' {print_init(initiative, True)}')
			initiative[actor - 1].updated = True
	await dm_channel.send(f' {print_init(initiative, False)}')

@bot.command(name='a', help='Add monster health: health, list of monster numbers')
@commands.has_role('DM')
async def add_monster_health(ctx, amount: int, *monster: int):
	for actor in monster:
		initiative[actor - 1].health += amount
	await dm_channel.send(f' {print_init(initiative, False)}')

@bot.command(name='dead', help='Monster no longer in combat: monster number')
@commands.has_role('DM')
async def remove_monster(ctx, monster: int):
	initiative.remove(initiative[monster - 1])
	await dm_channel.send(f' {print_init(initiative, False)}')
	await player_channel.send(f' {print_init(initiative, True)}')

@bot.command(name='l', help='Manually print combat list')
@commands.has_role('DM')
async def print_combat_list(ctx):
	order_init()
	await dm_channel.send(f' {print_init(initiative, False)}')
	await player_channel.send(f' {print_init(initiative, True)}')

@bot.command(name='new', help='Start a new combat')
@commands.has_role('DM')
async def reset(ctx):
	reset = globals()
	reset['combat_list'] = []
	reset['initiative'] = []
	reset['playerready'] = False
	reset['dmready'] = False

#Commands for everyone
@bot.command(name='playmusic', help='Start combat music')
async def start_music(ctx):
	await general.connect()
	music = discord.utils.get(bot.voice_clients, guild=ctx.guild)
	music.play(discord.FFmpegPCMAudio('music_files\\d&d Battle music.mp4'))

@bot.command(name='stopmusic', help='Ends combat music')
async def end_music(ctx):
	music = discord.utils.get(bot.voice_clients, guild=ctx.guild)
	await music.disconnect()

@bot.command(name='playnext', help='Play a different song')
async def next_song(ctx):
	music = discord.utils.get(bot.voice_clients, guild=ctx.guild)
	music.stop()
	music.play(discord.FFmpegPCMAudio(f'music_files\\{songs[randint(0, len(songs) - 1)]}.mp4'))

bot.run(TOKEN)