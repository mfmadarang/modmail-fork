import asyncio
import logging
import os

import aiohttp
import asyncpg
import docker
import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("watchdog")

POLL_INTERVAL = int(os.environ.get("WATCHDOG INTERVAL", 30))
DATABASE_URL = os.environ["DATABASE_URL"]
RABBITMQ_MGMT_URL = os.environ["RABBITMQ_MGMT_URL"]
REDIS_URL = os.environ["REDIS_URL"]

# rule-based thresholds

THRESHOLDS = {
    "mem_pct": 85.0,
    "cpu_pct": 90.0,
    "queue_depth": 500,
    "pg_connections": 18,
}

WATCHED_CONTAINERS = ["bot", "dispatch", "postgres", "redis", "rabbitmq"]

class Watchdog:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.pool = None
        self.redis = None
        self.http = None

    async def setup(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        self.redis = await aioredis.from_url(REDIS_URL)
        self.http = aiohttp.ClientSession()

    async def collect_docker_stats(self):
        results = {}
        for name in WATCHED_CONTAINERS:
            try:
                container = self.docker_client.containers.get(name)
                stats = container.stats(stream=False)
                mem_usage = stats["memory_stats"].get("usage", 0)
                mem_limit = stats["memory_stats"].get("limit", 1)
                mem_pct = (mem_usage / mem_limit) * 100

                cpu_delta = (
                    stats["cpu_stats"]["cpu_usage"]["total_usage"]
                    - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                )
                system_delta = (
                    stats["cpu_stats"]["system_cpu_usage"]
                    - stats["precpu_stats"]["system_cpu_usage"]
                )
                cpu_pct = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0.0

                results[name] = {"mem_pct": mem_pct, "cpu_pct": cpu_pct}
            except docker.errors.NotFound:
                log.warning(f"Container {name} not found")
        return results

    async def collect_queue_depth(self):
        try:
            async with self.http.get(RABBITMQ_MGMT_URL) as resp:
                data = await resp.json()
                return sum(q.get("messages", 0) for q in data)
        except Exception as e:
            log.error(f"RabbitMQ collection failed: {e}")
            return None

    async def collect_pg_connections(self):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT count(*) FROM pg_stat_activity")
            return row["count"]

    async def collect_redis_mem(self):
        info = await self.redis.info("memory")
        return info.get("used_memory", 0)

    async def check_thresholds(self, container, metrics):
        for key, limit in THRESHOLDS.items():
            value = metrics.get(key)
            if value is not None and value > limit:
                await self.log_incident(container, reason=f"{key}={value} exceeded threshold {limit}")

    async def log_incident(self, container, reason, exit_code=None):
        log.warning(f"INCIDENT [{container}]: {reason}")
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ops_incidents (container, exit_code, reason, predicted)
                VALUES ($1, $2, $3, true)
                """,
                container,
                exit_code,
                reason,
            )

    async def record_metrics(self, container, **metrics):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ops_metrics (container, mem_pct, cpu_pct, queue_depth, pg_connections, redis_mem)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                container,
                metrics.get("mem_pct"),
                metrics.get("cpu_pct"),
                metrics.get("queue_depth"),
                metrics.get("pg_connections"),
                metrics.get("redis_mem_bytes"),
            )

    async def poll_once(self):
        docker_stats = await self.collect_docker_stats()
        queue_depth = await self.collect_queue_depth()
        pg_connections = await self.collect_pg_connections()
        redis_mem = await self.collect_redis_mem()

        for container, stats in docker_stats.items():
            merged = dict(stats)
            if container =="rabbitmq":
                merged["queue_depth"] = queue_depth
            if container =="postgres":
                merged["pg_connections"] = pg_connections
            if container =="redis":
                merged["redis_mem_bytes"] = redis_mem

            await self.record_metrics(container, **merged)
            await self.check_thresholds(container, merged)

    async def run(self):
        await self.setup()
        log.info("Watchdog started")
        while True:
            try:
                await self.poll_once()
            except Exception as e:
                log.error(f"Poll cycle failed: {e}")
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(Watchdog().run())