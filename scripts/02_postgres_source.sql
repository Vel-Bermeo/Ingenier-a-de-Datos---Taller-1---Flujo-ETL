CREATE TABLE IF NOT EXISTS video_acked (
    "time" BIGINT NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    "index" INTEGER NOT NULL,
    expt_id VARCHAR(100),
    channel VARCHAR(150),
    video_ts BIGINT,
    buffer DOUBLE PRECISION,
    cum_rebuf DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_acked_stream
ON video_acked(session_id, "index");

CREATE INDEX IF NOT EXISTS idx_acked_chunk
ON video_acked(session_id, "index", video_ts);
