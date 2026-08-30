SELECT 'dim_tiempo' AS tabla, COUNT(*) AS filas FROM dim_tiempo
UNION ALL SELECT 'dim_sesion', COUNT(*) FROM dim_sesion
UNION ALL SELECT 'dim_stream', COUNT(*) FROM dim_stream
UNION ALL SELECT 'dim_canal', COUNT(*) FROM dim_canal
UNION ALL SELECT 'dim_formato', COUNT(*) FROM dim_formato
UNION ALL SELECT 'dim_experimento', COUNT(*) FROM dim_experimento
UNION ALL SELECT 'fact_streaming', COUNT(*) FROM fact_streaming;

SELECT
    c.channel,
    COUNT(*) AS chunks,
    AVG(f.ack_delay_ms) AS ack_delay_ms_prom,
    AVG(f.rtt_us) AS rtt_us_prom,
    AVG(f.buffer_seconds) AS buffer_prom
FROM fact_streaming f
JOIN dim_canal c ON c.id_canal = f.id_canal
GROUP BY c.channel
ORDER BY chunks DESC;
