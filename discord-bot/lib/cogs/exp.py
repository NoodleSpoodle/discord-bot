from datetime import datetime
from typing import Optional
from random import randint

from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions, CheckFailure
from ..db import db

class Exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def proccess_xp(self,message):
        xp, lvl, xplock = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.fromisoformat(xplock) < datetime.utcnow():
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_add = randint(10,15)
        new_lvl = int(((xp+xp_add)//42 ** 0.55))

        db.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
                   xp_add, new_lvl, datetime.utcnow().isoformat(), message.author.id)

        if new_lvl > lvl:
            await self.levelup_channel.send(f"Congrats {message.author.mention} - you reached level {new_lvl:,}!")

    @command(name="level")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record("SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (None, None)

        if lvl is not None:
            await ctx.send(f"{target.display_name} is on level {lvl:,} with {xp:,} XP")

        else:
            await ctx.send("That member is unranked")

    @command(name="rank")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM exp ORDER BY XP DESC")

        try:
            await ctx.send(f"{target.display_name} is rank {ids.index(target.id)+1} with level {lvl:,} of {len(ids)} members")

        except ValueError:
            await ctx.send("That member is unranked")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.levelup_channel = self.bot.get_channel(710536416056311888)
            self.bot.cogs_ready.ready_up("exp")

    @Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.proccess_xp(message)

def setup(bot):
    bot.add_cog(Exp(bot))
