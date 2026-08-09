import logging

from discord.ext import commands, tasks

from cogs.error_handler import ErrorHandler

log = logging.getLogger(__name__)

class OpsMetrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.report_metrics.start()

    def cog_unload(self):
        self.report_metrics.cancel()

    @tasks.loop(seconds=30)
    async def report_metrics(self):
        await self.bot.wait_until_ready()

        latency_ms = round(self.bot.latency * 1000, 2)
        error_count = ErrorHandler.pop_error_count()

        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ops_metrics (container, gateway_latency_ms, error_count)
                VALUES ($1, $2, $3)
                """,
                "bot",
                latency_ms,
                error_count,
            )

def setup(bot):
    bot.add_cog(OpsMetrics(bot))