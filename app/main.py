"""StoreOps API - tracks health of a fleet of retail store servers."""
import os
from datetime import datetime, timezone

import psycopg
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Gauge, make_asgi_app

DB_URL = os.getenv("DATABASE_URL", "postgresql://storeops:storeops@localhost:5432/storeops")

app = FastAPI(title="StoreOps API", version="0.1.0")

# Prometheus metrics (Phase 5 will scrape these)
HEARTBEATS = Counter("storeops_heartbeats_total", "Heartbeats received", ["store_id"])
STORES_ONLINE = Gauge("storeops_stores_online", "Stores online (heartbeat in last 5 min)")

app.mount("/metrics", make_asgi_app())


def get_conn():
    return psycopg.connect(DB_URL)


@app.on_event("startup")
def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                id        TEXT PRIMARY KEY,
                name      TEXT NOT NULL,
                region    TEXT NOT NULL,
                last_seen TIMESTAMPTZ
            )
        """)
        conn.execute("""
            INSERT INTO stores (id, name, region) VALUES
                ('S001', 'London Central', 'UK-South'),
                ('S002', 'Manchester Arndale', 'UK-North'),
                ('S003', 'Kolkata Salt Lake', 'IN-East'),
                ('S004', 'Birmingham Bullring', 'UK-Mid')
            ON CONFLICT (id) DO NOTHING
        """)


@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "db": "up"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db down: {e}")


@app.get("/stores")
def list_stores():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, region, last_seen FROM stores ORDER BY id").fetchall()
    now = datetime.now(timezone.utc)
    result = []
    online = 0
    for sid, name, region, last_seen in rows:
        is_online = last_seen is not None and (now - last_seen).total_seconds() < 300
        online += is_online
        result.append({
            "id": sid, "name": name, "region": region,
            "last_seen": last_seen.isoformat() if last_seen else None,
            "online": is_online,
        })
    STORES_ONLINE.set(online)
    return result


@app.post("/stores/{store_id}/heartbeat")
def heartbeat(store_id: str):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE stores SET last_seen = NOW() WHERE id = %s RETURNING id", (store_id,)
        )
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="store not found")
    HEARTBEATS.labels(store_id=store_id).inc()
    return {"store_id": store_id, "status": "alive"}
