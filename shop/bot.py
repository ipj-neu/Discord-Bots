import discord
from discord.ext import commands
from discord.ui import View, Button
import json

def read_shops():
    with open('shops.json', 'r') as file:
        return json.load(file)

shops = read_shops()

def printable_shop(shop):
    printable = '-' * 50
    printable += f"\n {shop['name']}\n"
    for i in shop['items']:
        printable += f" Name:  {i['iname']}  Price:  {i['iprice']}  Quantity:  {i['iquantity']}\n"
    printable += '-' * 50
    return printable

def shop_buttons():
    view = View()

    async def button_callback(interaction):
        for shop in shops:
            if shop['name'] == interaction.custom_id:
                await interaction.response.send_message(printable_shop(shop))

    for shop in shops:
        button = Button(label=shop['name'], custom_id=shop['name'])
        button.callback = button_callback
        view.add_item(button)

    return view

intent = discord.Intents.default()
intent.message_content = True

bot = commands.Bot(command_prefix="-", intents=intent)

@bot.command(name='print', help='prints shop: print [shop name]')
async def print_shop(ctx, shop_name):
    for shop in shops:
        if shop['name'] == shop_name:
            await ctx.send(printable_shop(shop))

@bot.command(name='reload', help='Reloads the JSON file')
async def reload_shops(ctx):
    global shops
    shops = read_shops()
    print(shops)

@bot.command(name='shops')
async def interactive_shops(ctx):
    await ctx.send('Shops', view=shop_buttons())

# TODO add run with env of discord token