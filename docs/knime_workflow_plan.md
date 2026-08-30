# Plan exacto del workflow en KNIME

## A. Extracción

### Fuente 1 — CSV
`CSV Reader` -> `client_buffer_sample.csv`

### Fuente 2 — MySQL
`MySQL Connector`
- Host: `127.0.0.1`
- Puerto: `3306`
- Database: `puffer_source`
- Usuario: `root`
- Password: `miclave`

Después:
`DB Table Selector` -> `video_sent` -> `DB Reader`

### Fuente 3 — PostgreSQL
`PostgreSQL Connector`
- Host: `127.0.0.1`
- Puerto: `5432`
- Database: `puffer_source`
- Usuario: `miuser`
- Password: `miclave`

Después:
`DB Table Selector` -> `video_acked` -> `DB Reader`

### Fuente 4 — MongoDB
`MongoDB Connector`
- Host: `127.0.0.1`
- Puerto: `27017`
- Database: `puffer_source`

Leer las colecciones `video_size` y `ssim`.
Convertir JSON a tabla con `JSON to Table`.

## B. Transformaciones que deben quedar visibles

Usa al menos estas, para evidenciar claramente la etapa T del ETL:

1. `Column Filter`
   - conservar únicamente columnas necesarias.

2. `Missing Value`
   - tratar faltantes de buffer, cum_rebuf u otras métricas.

3. `Column Renamer`
   - `time` de video_sent -> `sent_time_ns`
   - `time` de video_acked -> `acked_time_ns`

4. `String Manipulation`
   - crear `stream_key`:
     `join($session_id$, "-", toString($index$))`

5. `Joiner`
   - unir `video_sent` y `video_acked` por:
     `session_id`, `index`, `expt_id`, `channel`, `video_ts`

6. `Math Formula`
   - crear `ack_delay_ms`:
     `($acked_time_ns$ - $sent_time_ns$) / 1000000`

7. Conversión de tiempo
   - convertir `sent_time_ns` desde epoch nanosegundos a fecha/hora.
   - extraer fecha, año, mes, día y hora para `dim_tiempo`.

8. Formato de video
   - desde `format` (ej. 1280x720-20) extraer `width`, `height`, `crf`.
   - se puede hacer con `String Manipulation` + `Cell Splitter`.

9. `GroupBy`
   - obtener registros únicos para las dimensiones.

## C. Construcción de dimensiones

### dim_sesion
Concatenar (`Concatenate`) los `session_id` provenientes de:
- client_buffer (CSV)
- video_sent (MySQL)
- video_acked (PostgreSQL)

Después:
`GroupBy` -> session_id único.

### dim_stream
Desde client_buffer y/o video_sent:
- `session_id`
- `index`
- `stream_key`

`GroupBy` -> stream_key único.

### dim_canal
Desde video_sent:
`GroupBy` -> channel único.

### dim_formato
Desde MongoDB (`video_size` y/o `ssim`):
`GroupBy` -> format único.
Separar `format` para obtener width, height, crf.

### dim_experimento
Desde video_sent:
`GroupBy` -> expt_id único.

### dim_tiempo
Desde video_sent:
convertir `sent_time_ns` y luego `GroupBy` por fecha/hora.

## D. Destino DW

`PostgreSQL Connector`
- Host: `127.0.0.1`
- Puerto: `5433`
- Database: `puffer_dw`
- Usuario: `dwuser`
- Password: `dwclave`

Cargar con `DB Writer`:
1. dim_tiempo
2. dim_sesion
3. dim_stream
4. dim_canal
5. dim_formato
6. dim_experimento
7. fact_streaming

Las dimensiones se cargan antes de la tabla de hechos.

## E. Tabla de hechos

Partir del dataset resultante del Joiner entre `video_sent` y `video_acked`.
Luego hacer lookup/join contra cada dimensión ya cargada para obtener sus IDs.

Finalmente conservar:
- id_tiempo
- id_sesion
- id_stream
- id_canal
- id_formato
- id_experimento
- video_ts
- sent_time_ns
- acked_time_ns
- ack_delay_ms
- size_bytes
- ssim_index
- cwnd
- in_flight
- min_rtt_us
- rtt_us
- delivery_rate_bps
- buffer_seconds
- cum_rebuf_seconds

Escribir en `fact_streaming` usando `DB Writer`.
