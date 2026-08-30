CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo BIGSERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    anio SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    dia SMALLINT NOT NULL,
    hora SMALLINT NOT NULL,
    UNIQUE (fecha, hora)
);

CREATE TABLE IF NOT EXISTS dim_sesion (
    id_sesion BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_stream (
    id_stream BIGSERIAL PRIMARY KEY,
    stream_key VARCHAR(160) NOT NULL UNIQUE,
    stream_index INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_canal (
    id_canal BIGSERIAL PRIMARY KEY,
    channel VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_formato (
    id_formato BIGSERIAL PRIMARY KEY,
    format VARCHAR(80) NOT NULL UNIQUE,
    width INTEGER,
    height INTEGER,
    crf INTEGER
);

CREATE TABLE IF NOT EXISTS dim_experimento (
    id_experimento BIGSERIAL PRIMARY KEY,
    expt_id VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_streaming (
    id_fact BIGSERIAL PRIMARY KEY,
    id_tiempo BIGINT NOT NULL REFERENCES dim_tiempo(id_tiempo),
    id_sesion BIGINT NOT NULL REFERENCES dim_sesion(id_sesion),
    id_stream BIGINT NOT NULL REFERENCES dim_stream(id_stream),
    id_canal BIGINT NOT NULL REFERENCES dim_canal(id_canal),
    id_formato BIGINT NOT NULL REFERENCES dim_formato(id_formato),
    id_experimento BIGINT REFERENCES dim_experimento(id_experimento),

    video_ts BIGINT,
    sent_time_ns BIGINT NOT NULL,
    acked_time_ns BIGINT,
    ack_delay_ms DOUBLE PRECISION,

    size_bytes BIGINT,
    ssim_index DOUBLE PRECISION,
    cwnd BIGINT,
    in_flight BIGINT,
    min_rtt_us BIGINT,
    rtt_us BIGINT,
    delivery_rate_bps BIGINT,
    buffer_seconds DOUBLE PRECISION,
    cum_rebuf_seconds DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_fact_tiempo ON fact_streaming(id_tiempo);
CREATE INDEX IF NOT EXISTS idx_fact_sesion ON fact_streaming(id_sesion);
CREATE INDEX IF NOT EXISTS idx_fact_stream ON fact_streaming(id_stream);
CREATE INDEX IF NOT EXISTS idx_fact_canal ON fact_streaming(id_canal);
CREATE INDEX IF NOT EXISTS idx_fact_formato ON fact_streaming(id_formato);
CREATE INDEX IF NOT EXISTS idx_fact_experimento ON fact_streaming(id_experimento);
