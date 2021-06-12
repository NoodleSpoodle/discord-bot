from discord import Intents
from datetime import datetime
from asyncio import sleep
from glob import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import embeds
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown
from ..db import db

PREFIX = "-"
OWNER_IDS = [437539709934370816]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingRequiredArgument)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler()
        db.autosave(self.scheduler)

        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=Intents.all())

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN= tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def proceess_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send("Please wait a few seconds.")

    async def on_connect(self):
        print(" bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong :(")

        await self.stdout.send("An error occured uh oh")

        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Some requirments are missing")

        elif isinstance(exc, HTTPException):
            await ctx.send("Unable to send message")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"Please wait {exc.retry_after:,.2f} secs.")

        elif hasattr(exc,"original"):
            if isinstance(exc, Forbidden):
                await ctx.send("I don't have permission to do that")
            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(710535137452097599)
            self.stdout = self.get_channel(801181416977072188)
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            embed = embeds.Embed(title="Now Online!", description="Cabbage bot has awakened", colour=0x00FF00, timestamp=datetime.utcnow())
            icon_for_auth = "https://cdn.discordapp.com/avatars/806885835181260800/ed34a9b2eb6db3ee67d65db2a24982e2.png?size=128"
            embed.set_author(name="Cabbage bot", icon_url=icon_for_auth)
            embed.set_footer(text="Coded by NoodleSpoodle#2399")
            embed.set_thumbnail(url=icon_for_auth)
            await self.stdout.send(embed=embed)

            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self,message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()
