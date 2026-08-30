[README.md](https://github.com/user-attachments/files/31619772/README.md)
# Taller 1 — Parte 5 — ETL Puffer con KNIME

Este proyecto implementa la arquitectura solicitada para el taller individual 1:

- 4 fuentes:
  1. CSV: `client_buffer`
  2. MySQL: `video_sent`
  3. PostgreSQL: `video_acked`
  4. MongoDB: `video_size` + `ssim`
- Transformaciones mediante KNIME.
- Data Warehouse relacional en PostgreSQL.
- Modelo estrella con 6 dimensiones y 1 tabla de hechos.

## 1. Levantar contenedores

Desde la carpeta del proyecto:

```powershell
docker compose up -d
docker ps
```

Deben aparecer:
- taller1_mysql_source
- taller1_postgres_source
- taller1_mongodb_source
- taller1_postgres_dw

## 2. Crear tablas de origen y destino

MySQL:

```powershell
Get-Content .\scripts\01_mysql_source.sql | docker exec -i taller1_mysql_source mysql -uroot -pmiclave
```

PostgreSQL de origen:

```powershell
Get-Content .\scripts\02_postgres_source.sql | docker exec -i taller1_postgres_source psql -U miuser -d puffer_source
```

MongoDB:

```powershell
Get-Content .\scripts\04_mongo_setup.js | docker exec -i taller1_mongodb_source mongosh
```

DW:

```powershell
Get-Content .\scripts\03_dw_schema.sql | docker exec -i taller1_postgres_dw psql -U dwuser -d puffer_dw
```

## 3. Crear muestras de los CSV reales

Instalar dependencias:

```powershell
py -m pip install -r .\scripts\requirements.txt
```

Ejemplo, usando tu carpeta original:

```powershell
py .\scripts\prepare_samples.py --source "D:\Maestria Ciencia de Datos\Proyecto de Titulación\Data\Data August 8th" --rows 100000
```

Se crearán 5 archivos en `data\`.

## 4. Cargar las tres fuentes Docker

```powershell
py .\scripts\load_sources.py --only all
```

`client_buffer_sample.csv` NO se carga a una base: KNIME lo lee directamente como la cuarta fuente CSV.

## 5. Comprobar las fuentes

MySQL:

```powershell
docker exec -it taller1_mysql_source mysql -uroot -pmiclave -e "USE puffer_source; SELECT COUNT(*) FROM video_sent;"
```

PostgreSQL:

```powershell
docker exec -it taller1_postgres_source psql -U miuser -d puffer_source -c "SELECT COUNT(*) FROM video_acked;"
```

MongoDB:

```powershell
docker exec -it taller1_mongodb_source mongosh --quiet --eval "db=db.getSiblingDB('puffer_source'); print('video_size=' + db.video_size.countDocuments()); print('ssim=' + db.ssim.countDocuments())"
```

## 6. Construir el workflow KNIME

Seguir `docs/knime_workflow_plan.md`.

## 7. Validar el DW

Cuando KNIME termine de cargar:

```powershell
Get-Content .\scripts\validate_dw.sql | docker exec -i taller1_postgres_dw psql -U dwuser -d puffer_dw
```

## 8. Entrega

- workflow exportado de KNIME
- scripts y/o datos de origen
- informe ejecutivo PDF

