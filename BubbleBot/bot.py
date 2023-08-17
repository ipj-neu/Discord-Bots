import os
import discord
from discord.ext import commands
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="-", intents=intents)

bot_thread = Thread(target=bot.run, args=(os.getenv("DISCORD_BOT_TOKEN"),), daemon=True)

def start():
    while True:
        command_str = input('>>> ')

        command = ''

        if command_str != '':
            values = command_str.split()
            command = values[0]
            args = values[1:]

        if command == 'exit':
            break

        elif command == 'run':
            if len(args):
                for arg in args:
                    bot.load_extension(f'cogs.{arg}')
                    print(f'cogs.{args[0]} had been loaded')    
            if not bot_thread.is_alive():
                bot_thread.start()
                print('BubbleBot has booted up')
            else:
                print('Bot is already running')

        elif command == 'load':
            bot.load_extension(f'cogs.{args[0]}')
            print(f'cogs.{args[0]} had been loaded')

        elif command == 'unload':
            bot.unload_extension(f'cogs.{args[0]}')
            print(f'cogs.{args[0]} had been unloaded')

        elif command == 'reload':
            bot.unload_extension(f'cogs.{args[0]}')
            bot.load_extension(f'cogs.{args[0]}')
            print(f'cogs.{args[0]} had been reloaded')

        elif command == 'cls':
            os.system('cls')

        elif command != '':
            print('Invalid command')

if __name__ == "__main__":
    start()