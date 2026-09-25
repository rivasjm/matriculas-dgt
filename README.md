# matriculas-dgt

Datos de **matriculaciones diarias de vehículos** publicados por la Dirección General de Tráfico (DGT).

## Fuente

- Página oficial: [Matriculaciones de automóviles (diario)](https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/matriculaciones-automoviles-diario.html)
- Catálogo de datos abiertos: [Microdatos de Matriculaciones de Vehículos (diario)](https://datos.gob.es/es/catalogo/e00003801-microdatos-de-matriculaciones-de-vehiculos-diario)
- Diseño de registro: [MATRICULACIONES_MATRABA.pdf](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/matraba/MATRICULACIONES_MATRABA.pdf)

## Licencia

Los datos originales se distribuyen bajo licencia [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Autoría: Dirección General de Tráfico (Ministerio del Interior, España).

## Estructura

```
data/
├── sync_matriculaciones.py      # descarga los ZIP de la DGT y genera el CSV
└── YYYYMM/                      # p. ej. 202609
    └── YYYYMM.csv               # compilación del subdirectorio
```

## Formato de los ficheros `.txt`

Ficheros de **ancho fijo** (no delimitados), codificación **ISO-8859-1 (latin-1)**, saltos de línea **LF** y **714 caracteres por registro**.

- Primera línea: cabecera `Vehículos matriculados. Letras de la serie de la última matrícula asignada: XXX`.
- Resto: un registro por matriculación, con **69 campos** de longitud fija que suman 714 caracteres.

| # | Campo | Long. |
|---|-------|-------|
| 1 | `FEC_MATRICULA` | 8 |
| 2 | `COD_CLASE_MAT` | 1 |
| 3 | `FEC_TRAMITACION` | 8 |
| 4 | `MARCA_ITV` | 30 |
| 5 | `MODELO_ITV` | 22 |
| 6 | `COD_PROCEDENCIA_ITV` | 1 |
| 7 | `BASTIDOR_ITV` | 21 |
| 8 | `COD_TIPO` | 2 |
| 9 | `COD_PROPULSION_ITV` | 1 |
| 10 | `CILINDRADA_ITV` | 5 |
| 11 | `POTENCIA_ITV` | 6 |
| 12 | `TARA` | 6 |
| 13 | `PESO_MAX` | 6 |
| 14 | `NUM_PLAZAS` | 3 |
| 15 | `IND_PRECINTO` | 2 |
| 16 | `IND_EMBARGO` | 2 |
| 17 | `NUM_TRANSMISIONES` | 2 |
| 18 | `NUM_TITULARES` | 2 |
| 19 | `LOCALIDAD_VEHICULO` | 24 |
| 20 | `COD_PROVINCIA_VEH` | 2 |
| 21 | `COD_PROVINCIA_MAT` | 2 |
| 22 | `CLAVE_TRAMITE` | 1 |
| 23 | `FEC_TRAMITE` | 8 |
| 24 | `CODIGO_POSTAL` | 5 |
| 25 | `FEC_PRIM_MATRICULACION` | 8 |
| 26 | `IND_NUEVO_USADO` | 1 |
| 27 | `PERSONA_FISICA_JURIDICA` | 1 |
| 28 | `CODIGO_ITV` | 9 |
| 29 | `SERVICIO` | 3 |
| 30 | `COD_MUNICIPIO_INE_VEH` | 5 |
| 31 | `MUNICIPIO` | 30 |
| 32 | `KW_ITV` | 7 |
| 33 | `NUM_PLAZAS_MAX` | 3 |
| 34 | `CO2_ITV` | 5 |
| 35 | `RENTING` | 1 |
| 36 | `COD_TUTELA` | 1 |
| 37 | `COD_POSESION` | 1 |
| 38 | `IND_BAJA_DEF` | 1 |
| 39 | `IND_BAJA_TEMP` | 1 |
| 40 | `IND_SUSTRACCION` | 1 |
| 41 | `BAJA_TELEMATICA` | 11 |
| 42 | `TIPO_ITV` | 25 |
| 43 | `VARIANTE_ITV` | 25 |
| 44 | `VERSION_ITV` | 35 |
| 45 | `FABRICANTE_ITV` | 70 |
| 46 | `MASA_ORDEN_MARCHA_ITV` | 6 |
| 47 | `MASA_MAXIMA_TECNICA_ADMISIBLE_ITV` | 6 |
| 48 | `CATEGORIA_HOMOLOGACION_EUROPEA_ITV` | 4 |
| 49 | `CARROCERIA` | 4 |
| 50 | `PLAZAS_PIE` | 3 |
| 51 | `NIVEL_EMISIONES_EURO_ITV` | 8 |
| 52 | `CONSUMO_WH/KM_ITV` | 4 |
| 53 | `CLASIFICACION_REGLAMENTO_VEHICULOS_ITV` | 4 |
| 54 | `CATEGORIA_VEHICULO_ELECTRICO` | 4 |
| 55 | `AUTONOMIA_VEHICULO_ELECTRICO` | 6 |
| 56 | `MARCA_VEHICULO_BASE` | 30 |
| 57 | `FABRICANTE_VEHICULO_BASE` | 50 |
| 58 | `TIPO_VEHICULO_BASE` | 35 |
| 59 | `VARIANTE_VEHICULO_BASE` | 25 |
| 60 | `VERSION_VEHICULO_BASE` | 35 |
| 61 | `DISTANCIA_EJES_12_ITV` | 4 |
| 62 | `VIA_ANTERIOR_ITV` | 4 |
| 63 | `VIA_POSTERIOR_ITV` | 4 |
| 64 | `TIPO_ALIMENTACION_ITV` | 1 |
| 65 | `CONTRASENA_HOMOLOGACION_ITV` | 25 |
| 66 | `ECO_INNOVACION_ITV` | 1 |
| 67 | `REDUCCION_ECO_ITV` | 4 |
| 68 | `CODIGO_ECO_ITV` | 25 |
| 69 | `FEC_PROCESO` | 8 |

Las fechas usan el formato `DDMMYYYY`. El campo `BASTIDOR_ITV` solo incluye los 8 primeros caracteres del bastidor (el resto se rellena con `*`).

## Uso

El script `data/sync_matriculaciones.py`:

1. Lee el listado de la web de la DGT y obtiene los enlaces a los ZIP diarios.
2. Descarga solo los días que aún no estén en el CSV de su mes, en `data/YYYYMM/`, creando el subdirectorio si no existe.
3. Descomprime los ZIP y los elimina.
4. Añade los registros nuevos a `data/YYYYMM/YYYYMM.csv`.
5. Borra los `.txt` una vez volcados al CSV (en el repo solo queda el CSV).

```sh
python3 data/sync_matriculaciones.py            # actualiza de forma incremental
python3 data/sync_matriculaciones.py --force    # reescribe los CSV desde cero
```

Opciones: `--data-dir DIR` (por defecto `data/`) y `--url URL` (listado a consultar).
