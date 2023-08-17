import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
import requests
import tempfile
import os

class Deep(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.API_KEY = {"xi-api-key": os.getenv("XI_API_KEY")}
        self.current_voice_id = "MRyqaq7uTJG22RJ8Eiyx"
        self.current_voice_name = "Bama"
        
    @commands.command(name="submit-training", help="Submit .mp3 for training: submit-training \{voice.mp3\}")
    async def submit_voice_sample(self, ctx):
        message = ctx.message
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename[-4:] == ".mp3" or attachment.filename[-4:] == ".wav":
                    await attachment.save(os.path.join("submission", attachment.filename))
                    await ctx.send(f"{attachment.filename} has been saved!")
        else:
            await ctx.sent(f"No file attached")

    @commands.command(name="selected", help="Gets the currents selected voice: selected")
    async def voice_selected(self, ctx):
        await ctx.send(f"Current voice: {self.current_voice_name}")

    @commands.command(name="voices", help="Select different voice: voice [cloned, premade]", )
    async def voice_selection(self, ctx, *args):
        category = None
        if len(args) > 0:
            category = args[0] 
        
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=self.API_KEY)
        voices = response.json()["voices"]
        view = View()

        async def callback(interaction):
            for voice in voices:
                if voice["voice_id"] == interaction.custom_id:
                    self.current_voice_id = voice["voice_id"]
                    self.current_voice_name = voice["name"]
                    await interaction.response.send_message(f"{voice['name']} Selected!")
        
        for voice in voices:
            if category != None: 
                if voice["category"] == category:
                    button = Button(label=voice["name"], custom_id=voice["voice_id"], style=discord.ButtonStyle.blurple)
                    button.callback = callback
                    view.add_item(button)
            else:
                button = Button(label=voice["name"], custom_id=voice["voice_id"], style=discord.ButtonStyle.blurple)
                button.callback = callback
                view.add_item(button)
                
        await ctx.send("Voices", view=view)
    
    @commands.command(name="gen", help="Generates what you tell it to: speak [string (no quotes needed)]")
    async def genorate_voice(self, ctx, *, arg):
        voice_client = None
        
        channel = ctx.author.voice.channel
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.guild:
                voice_client = vc

        if voice_client == None:
        
            # api setup
            body = {
                "text": arg,
                "voice_settings": {
                    "stability": 0,
                    "similarity_boost": 0
                }
            }

            # retreive voice binray
            print("sending request")
            response = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{self.current_voice_id}", headers=self.API_KEY, json=body)
            print(response.status_code)

            # creates a temp file and writes the binary
            with tempfile.NamedTemporaryFile(suffix=".mp3", mode="wb", delete=False) as tmp:
                tmp.write(response.content)

            # connects and waits a second
            voice_client = await channel.connect()
            await asyncio.sleep(1)
            
            # play audio
            audio = discord.FFmpegPCMAudio(tmp.name)
            voice_client.play(audio)

            # wait till audio is over then disconnects and removes tmp files
            while voice_client.is_playing():
                await asyncio.sleep(0.1)
            await voice_client.disconnect()

            os.remove(tmp.name)

    @commands.command(name="chars", help="Get the number of characters left: chars")
    async def see_current_characters(self, ctx):
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=self.API_KEY)
        response = response.json()
        current_used_chars = response["subscription"]["character_count"]
        max_chars = response["subscription"]["character_limit"]
        await ctx.send(f"Character Count: {current_used_chars} / {max_chars}")
        
    @commands.command(name="disconnect")
    async def disconnect(self, ctx):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

def setup(bot):
    bot.add_cog(Deep(bot))