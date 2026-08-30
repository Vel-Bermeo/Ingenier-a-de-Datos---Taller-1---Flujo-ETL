USE puffer_source;

CREATE TABLE IF NOT EXISTS video_sent (
    `time` BIGINT NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    `index` INT NOT NULL,
    expt_id VARCHAR(100),
    channel VARCHAR(150),
    video_ts BIGINT,
    format VARCHAR(80),
    size BIGINT,
    ssim_index DOUBLE,
    cwnd BIGINT,
    in_flight BIGINT,
    min_rtt BIGINT,
    rtt BIGINT,
    delivery_rate BIGINT,
    buffer DOUBLE,
    cum_rebuf DOUBLE,
    INDEX idx_sent_stream (session_id, `index`),
    INDEX idx_sent_chunk (session_id, `index`, video_ts),
    INDEX idx_sent_format (format)
);
