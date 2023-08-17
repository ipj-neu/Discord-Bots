import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import asyncio

class Sound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add-sound")
    async def add_sound(self, ctx):
        message = ctx.message
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename[-4:] == ".mp3":
                    await attachment.save(os.path.join("sounds", attachment.filename))
                    await ctx.send(f"{attachment.filename} has been saved!")
                else:
                    await ctx.send(f"{attachment.filename} is not an mp3")
        else:
            await ctx.sent(f"No file attached")

    @commands.command(name="soundboard")
    async def soundboard(self, ctx):
        view = View()

        async def callback(interaction):
            vc = await ctx.author.voice.channel.connect()
            await asyncio.sleep(1)
            await interaction.response.send_message(f"Playing {interaction.custom_id[:-4]}!")
            
            audio = discord.FFmpegPCMAudio(os.path.join("sounds", interaction.custom_id))
            vc.play(audio)

            while vc.is_playing():
                await asyncio.sleep(0.1)
            await vc.disconnect()
        
        for file in os.listdir("sounds"):
            button = Button(label=file[:-4], custom_id=file)
            button.callback = callback
            view.add_item(button)
        
        await ctx.send("Sounds", view=view)
        
    @commands.command()
    async def disconnect(self, ctx):
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.guild:
                await vc.disconnect()

def setup(bot):
    bot.add_cog(Sound(bot))