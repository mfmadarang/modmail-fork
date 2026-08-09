import os
from datetime import datetime, timedelta
from typing import Optional

import asyncpg
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Modmail Ops API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

pool: Optional[asyncpg.Pool] = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], min_size=1, max_size=3)

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

@app.get("/metrics/latest")
async def latest_metrics():
    rows = await pool.fetch("""
        SELECT DISTINCT ON (container) *
        FROM ops_metrics
        ORDER BY container, recorded_at DESC
    """)
    return [dict(r) for r in rows]

@app.get("/metrics/history")
async def metrics_history(container: Optional[str] = None, minutes: int = Query(60, le=1440)):
    since = datetime.utcnow() - timedelta(minutes=minutes)
    if container:
        rows = await pool.fetch(
            "SELECT * FROM ops_metrics WHERE container = $1 AND recorded_at >= $2 ORDER BY recorded_at ASC",
            container, since,
        )
    else:
        rows = await pool.fetch(
            "SELECT * FROM ops_metrics WHERE recorded_at >= $1 ORDER BY recorded_at ASC", since,
        )
    return [dict(r) for r in rows]