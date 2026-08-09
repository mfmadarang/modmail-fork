import asyncio
import logging
import time
from types import SimpleNamespace

from discord.ext import commands

from classes.embed import Embed
from utils import tools

log = logging.getLogger(__name__)

WARN_AFTER = 24 * 60 * 60 * 1000 # ms of inactivity before a warning is posted
CLOSE_AFTER = 48*60 * 60 * 1000 # ms of inactivity before the ticket auto-closes
CHECK_INTERVAL = 30 * 60 # seconds between scans

class AutoClose(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = bot.loop.create_task(self.run())

    def cog_unload(self):
        self.task.cancel()

    async def run(self):
        while True:
            try:
                await self.check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Auto-close check failed: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

    async def check(self):
        now = int(time.time() * 1000)

        async with self.bot.pool.acquire() as conn:
            stale = await conn.fetch(
                "SELECT channel, guild, last_activity, warned FROM ticket WHERE last_activity < $1",
                now - WARN_AFTER,
            )

        for row in stale:
            channel = await self.bot.get_channel(row["channel"])

            if channel is None:
                # The channel was deleted outside of the bot (e.g. manually by a mod)
                async with self.bot.pool.acquire() as conn:
                    await conn.execute("DELETE FROM ticket WHERE channel=$1", row["channel"])
                continue

            age = now - row["last_activity"]

            if age >= CLOSE_AFTER:
                await self.auto_close(channel)
            elif not row["warned"]:
                await self.warn(channel)

    async def warn(self, channel):
        try:
            await channel.send(
                Embed(
                    "Inactivity Warning",
                    "This ticket has had no activity for 24 hours and will close automatically "
                    "after 48 hours of silence. Send a message to keep it open.",
                    timestamp=True,
                )
            )
        except Exception:
            pass

        async with self.bot.pool.acquire() as conn:
            await conn.execute("UPDATE ticket SET warned=TRUE WHERE channel=$1", channel.id)

    async def auto_close(self, channel):
        core = self.bot.cogs.get("Core")

        if core is None:
            log.error("Core cog not loaded; cannot auto-close tickets.")
            return

        # A lightweight stand-in for a command Context, just enough for close_channel to work
        ctx = SimpleNamespace(
            guild=channel.guild,
            channel=channel,
            author=self.bot.user,
            send=channel.send,
        )

        await core.close_channel(ctx, "Automatically closed due to 48 hours of inactivity .", anon=True)

        await tools.send_webhook_alert(
            self.bot,
            "Ticket Auto-Closed",
            f"{channel.mention} was automatically closed after 48 hours of inactivity.",
            colour=0xFF4500,
        )

def setup(bot):
    bot.add_cog(AutoClose(bot))