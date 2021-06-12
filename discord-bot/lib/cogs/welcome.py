from discord.ext.commands import Cog
from discord.ext.commands import command
from ..db import db

class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
        await self.bot.get_channel(710535137875722350).send(f"Welcome {member.mention}!")
        await member.add_roles(member.guild.get_role(710536022114566214))

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
        await self.bot.get_channel(710535137875722350).send(f"User {member.display_name} has left the server :(")

def setup(bot):
    bot.add_cog(Welcome(bot))
