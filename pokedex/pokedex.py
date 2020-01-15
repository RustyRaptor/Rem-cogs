import discord
import dhash
import imagehash
import json
import io
import aiohttp
import asyncio
import pathlib
from PIL import Image
import sys, os
from redbot.core import Config
from redbot.core import commands
from redbot.core import checks
from redbot.core.data_manager import cog_data_path
from typing import Any

Cog: Any = getattr(commands, "Cog", object)

def getdHash(img):
    io = Image.open(img)
    hashd = imagehash.dhash(io)
    return hashd

with open ('/home/notamp/rem/pokedex/Lists/dhash.json') as dd:
    ddata = json.load(dd)

with open ('/home/notamp/rem/pokedex/Lists/lemy.json') as lm:
    lemy = json.load(lm)

with open ('/home/notamp/rem/pokedex/Lists/ulbt.json') as ub:
    ulbt = json.load(ub)

class Pokedex(Cog):
    """
    This cog will detect and output pokemon names from Pokecord
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=789)
        default_guild = {
            "idch": 0,
            "spamch": 0,
            "pkrole": ""
        }
        default_member = {
            "lfp": []
        }
        self._ready = asyncio.Event()
        self.config.register_member(**default_member)
        self.config.register_guild(**default_guild)

    @commands.group(invoke_without_command=False)
    async def pokedex(self, ctx):
        """
        Choose a subcommand below
        """
        if ctx.invoked_subcommand is None:
            pass

    @pokedex.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def setidchannel(self, ctx, idchannel: int):
        """
        Sets the identification channel where the bot will output to.
        """
        await self.config.guild(ctx.guild).idch.set(idchannel)
        await ctx.send('The bot will now send the identification to: ' + '<#' + str(idchannel) + '>')
    
    @pokedex.command()
    @checks.is_owner()
    async def setspamstop(self, ctx:commands.Context, spamchannel: int):
        """
        Sets the spam channel stop (owner only)
        """
        await self.config.guild(ctx.guild).spamch.set(spamchannel)
        await ctx.send('The bot will now send the stop message to: ' + '<#' + str(spamchannel)+ '>')
    
    @pokedex.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def setrole(self, ctx:commands.Context, role: str):
        """
        Sets the role to mention when a Legendary, Alolan or Mythical Pokémon is spawned.
        """
        await self.config.guild(ctx.guild).pkrole.set(role)
        await ctx.send('The bot will now notify this role: ' + role + '!')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.id == 365975655608745985):
            idpk = self.bot.get_channel(await self.config.guild(message.guild).idch())
            spm = self.bot.get_channel(await self.config.guild(message.guild).spamch())
            try:
                url = message.embeds[0].image.url
            except IndexError:
                return
            openimg = io.BytesIO()
            try:
                if 'PokecordSpawn' not in url:
                    return
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as res:
                        if res.status==200:
                            openimg.write(await res.read())
                            print ('Processing Image!')
                        else:
                            raise Exception('Image didn\'t return 200')
                rdhash = getdHash(openimg)
                dummy = 100
                pkid = None
                for line in ddata:
                    compare_hex = int(str(rdhash), 16)
                    compare_file = int(ddata[line], 16)
                    diff = dhash.get_num_bits_different(compare_hex,compare_file)
                    if(diff < dummy):
                        dummy = diff
                        pkid = line
                else:
                    pkem = discord.Embed(title = 'It\'s '  + pkid + '!' , color=0xff80ff)
                    pkem.description = f"\n\n[Click to view message]({message.jump_url})"
                    pkem.set_footer(text="p!catch " + pkid)
                    pkem.set_author(name = 'Pokémon Identified!')
                    pkem.set_thumbnail(url = "https://i.imgur.com/D5s4Bx3.jpg")
                    if pkid in lemy:
                        await idpk.send(await self.config.guild(message.guild).role() + ' a Legendary or Mythical has spawned!')
                        await spm.send('yuiplsstop')
                    if pkid in ulbt:
                        await idpk.send(await self.config.guild(message.guild).role() + ' an Ultra Beast has spawned!')
                        await spm.send('yuiplsstop')
                    if 'Alolan' in pkid:
                        await idpk.send(await self.config.guild(message.guild).role() + ' an Alolan has spawned!')
                        await spm.send('yuiplsstop')
                await idpk.send(embed = pkem)
            except TypeError:
                return