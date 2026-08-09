CREATE TABLE ops_metrics (
    id BIGSERIAL PRIMARY KEY,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    container VARCHAR(50) NOT NULL,
    mem_pct DOUBLE PRECISION,
    cpu_pct DOUBLE PRECISION,
    queue_depth INTEGER,
    pg_connections INTEGER,
    redis_mem_bytes BIGINT,
    gateway_latency_ms DOUBLE PRECISION,
    error_count INTEGER
);

CREATE INDEX idx_ops_metrics_recorded_at ON ops_metrics (recorded_at);
CREATE INDEX idx_ops_metrics_container ON ops_metrics (container);

CREATE TABLE ops_incidents (
    id BIGSERIAL PRIMARY KEY,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    container VARCHAR(50) NOT NULL,
    exit_code INTEGER,
    reason TEXT,
    predicted BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_ops_incidents_recorded_at ON ops_incidents (recorded_at);