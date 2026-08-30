# Modelo estrella propuesto — Puffer

Grano de la tabla de hechos:
**un chunk de video enviado por Puffer a un cliente**.

Dimensiones:
1. `dim_tiempo`
2. `dim_sesion`
3. `dim_stream`
4. `dim_canal`
5. `dim_formato`
6. `dim_experimento` (dimensión adicional)

Tabla de hechos:
`fact_streaming`

```text
                         dim_tiempo
                             |
dim_sesion ----------- fact_streaming ----------- dim_formato
                             |
dim_stream -----------------+-------------------- dim_canal
                             |
                       dim_experimento
```

Medidas principales:
- `size_bytes`
- `ssim_index`
- `cwnd`
- `in_flight`
- `min_rtt_us`
- `rtt_us`
- `delivery_rate_bps`
- `buffer_seconds`
- `cum_rebuf_seconds`
- `ack_delay_ms`

`ack_delay_ms` se calcula como:

`(acked_time_ns - sent_time_ns) / 1,000,000`
