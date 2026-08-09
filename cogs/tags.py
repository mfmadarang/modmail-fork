import logging

from discord.ext import commands

from classes.embed import Embed, ErrorEmbed
from utils import checks, tools

log = logging.getLogger(__name__)

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_modmail_channel()
    @checks.in_database()
    @checks.is_mod()
    @commands.guild_only()
    @commands.command(
        description="Tag this ticket, or view its current tag.",
        usage="tag [name]",
        aliases=["t"],
    )
    async def tag(self, ctx, *, name: str = None):
        if name is None:
            ticket = await tools.get_ticket(self.bot, ctx.channel.id)

            if not ticket or not ticket["tag"]:
                await ctx.send(Embed("Ticket Tag", "This ticket has no tag set."))
            else:
                await ctx.send(Embed("Ticket Tag", f"This ticket is tagged `{ticket['tag']}`."))

            return

        name = name.lower().strip()

        if len(name) > 32:
            await ctx.send(ErrorEmbed("Tag names must be 32 characters or fewer."))
            return

        await tools.set_ticket_tag(self.bot, ctx.channel.id, ctx.guild.id, name)
        await tools.send_webhook_alert(
            self.bot,
            "Ticket Tagged",
            f"{ctx.channel.mention} was tagged `{name}` by **{ctx.author.name}**.",
        )
        await ctx.send(Embed("Ticket Tagged", f"This ticket is now tagged `{name}`."))

    @checks.is_modmail_channel()
    @checks.in_database()
    @checks.is_mod()
    @commands.guild_only()
    @commands.command(description="Remove this ticket's tag.", usage="untag")
    async def untag(self, ctx):
        await tools.set_ticket_tag(self.bot, ctx.channel.id, ctx.guild.id, None)
        await ctx.send(Embed("Ticket Untagged", "This ticket's tag has been removed."))

    @checks.in_database()
    @checks.is_mod()
    @commands.guild_only()
    @commands.command(description="List open tickets, grouped by tag.", usage="tags")
    async def tags(self, ctx):
        async with self.bot.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT channel, tag FROM ticket WHERE guild=$1 ORDER BY tag NULLS LAST",
                ctx.guild.id,
            )

        if not rows: 
            await ctx.send(Embed("Tickets", "There are no open tickets."))
            return

        grouped = {}
        for row in rows:
            grouped.setdefault(row["tag"] or "*untagged", []).append(row["channel"])

        embed = Embed("Open Tickets", timestamp=True)

        for tag, channels in grouped.items():
            embed.add_field(tag, " ".join(f"<#{c}>" for c in channels), False)

        await ctx.send(embed)

def setup(bot):
    bot.add_cog(Tags(bot))