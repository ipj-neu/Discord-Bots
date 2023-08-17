import discord
from discord.ext import commands
from discord.ui import View, Button
import json

def read_shops():
    with open('shops.json', 'r') as file:
        return json.load(file)

def printable_shop(shop):
    printable = '-' * 50
    printable += f"\n {shop['name']}\n"
    for i in shop['items']:
        printable += f" Name:  {i['iname']}  Price:  {i['iprice']}  Quantity:  {i['iquantity']}\n"
    printable += '-' * 50
    return printable

async def shop_buttons(shops):
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

class Shops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shops = read_shops()

    @commands.command(name='print', help='Prints shop: print [shop name]')
    async def print_shop(self, ctx, shop_name):
        for shop in self.shops:
            if shop['name'] == shop_name:
                await ctx.send(printable_shop(self.shop))

    @commands.command(name='reload', help='Reloads the JSON file')
    async def reload_shops(self, ctx):
        self.shops = read_shops()

    @commands.command(name='shops', help='Interactive shop menu')
    async def interactive_shops(self, ctx):
        await ctx.send('Shops', view=await shop_buttons(self.shops))

def setup(bot):
    bot.add_cog(Shops(bot))