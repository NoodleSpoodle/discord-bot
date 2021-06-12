from random import choice, randint
from typing import Optional
from aiohttp import request
from discord import Member, embeds
from discord.errors import HTTPException
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi"])
    async def say_hello(self, ctx):
        """Say hi to cabbage bot!"""
        await ctx.send(f"{choice(('Hello','Hi','Hi there', 'Greetings', 'Hey', 'Hiya'))} {ctx.author.mention}!")

    @command(name="dice", aliases=["roll"])
    @cooldown(1,10,BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        """Roll dice with [faces]d[num of dice]"""
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <=25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
        else:
            await ctx.send("I can't roll that many dice")

    @command(name="slap", aliases=["hit"])
    @cooldown(1,10,BucketType.user)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
        """Slap someone by mentioning them"""
        await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}!")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Invalid member D:")

    @command(name="echo", aliases=["say"])
    @cooldown(1,10,BucketType.user)
    async def echo_message(self, ctx, *, message):
        """Make cabbage bot repeat what you say"""
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="fact")
    @cooldown(1,10,BucketType.guild)
    async def animal_fact(self, ctx, animal: str):
        """Get a fact for [dog,cat,panda,fox,bird,koala]"""
        if (animal := animal.lower()) in("dog", "cat","panda", "fox", "bird", "koala"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_link = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"
            async with request("GET", image_link, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                else:
                    image = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    embed = embeds.Embed(title=f"{animal.title()} fact", description=data["fact"], colour=0X00FF00)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send(f"Uh oh, API returned a {response.status} status")
        else:
            await ctx.send(f"I don't know any {animal.lower()} facts")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")

def setup(bot):
    bot.add_cog(Fun(bot))
