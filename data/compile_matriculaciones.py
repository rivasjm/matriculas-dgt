#!/usr/bin/env python3
"""Compila los ficheros de matriculaciones (ancho fijo) de cada subdirectorio
de data/ en un unico CSV por subdirectorio.

Cada subdirectorio debe contener ficheros export_mat_YYYYMMDD.txt con el
formato oficial de la DGT (69 campos, 714 caracteres por registro).

Uso:
    python3 data/compile_matriculaciones.py
"""

import csv
import sys
from pathlib import Path

FIELDS = [
    ("FEC_MATRICULA", 8),
    ("COD_CLASE_MAT", 1),
    ("FEC_TRAMITACION", 8),
    ("MARCA_ITV", 30),
    ("MODELO_ITV", 22),
    ("COD_PROCEDENCIA_ITV", 1),
    ("BASTIDOR_ITV", 21),
    ("COD_TIPO", 2),
    ("COD_PROPULSION_ITV", 1),
    ("CILINDRADA_ITV", 5),
    ("POTENCIA_ITV", 6),
    ("TARA", 6),
    ("PESO_MAX", 6),
    ("NUM_PLAZAS", 3),
    ("IND_PRECINTO", 2),
    ("IND_EMBARGO", 2),
    ("NUM_TRANSMISIONES", 2),
    ("NUM_TITULARES", 2),
    ("LOCALIDAD_VEHICULO", 24),
    ("COD_PROVINCIA_VEH", 2),
    ("COD_PROVINCIA_MAT", 2),
    ("CLAVE_TRAMITE", 1),
    ("FEC_TRAMITE", 8),
    ("CODIGO_POSTAL", 5),
    ("FEC_PRIM_MATRICULACION", 8),
    ("IND_NUEVO_USADO", 1),
    ("PERSONA_FISICA_JURIDICA", 1),
    ("CODIGO_ITV", 9),
    ("SERVICIO", 3),
    ("COD_MUNICIPIO_INE_VEH", 5),
    ("MUNICIPIO", 30),
    ("KW_ITV", 7),
    ("NUM_PLAZAS_MAX", 3),
    ("CO2_ITV", 5),
    ("RENTING", 1),
    ("COD_TUTELA", 1),
    ("COD_POSESION", 1),
    ("IND_BAJA_DEF", 1),
    ("IND_BAJA_TEMP", 1),
    ("IND_SUSTRACCION", 1),
    ("BAJA_TELEMATICA", 11),
    ("TIPO_ITV", 25),
    ("VARIANTE_ITV", 25),
    ("VERSION_ITV", 35),
    ("FABRICANTE_ITV", 70),
    ("MASA_ORDEN_MARCHA_ITV", 6),
    ("MASA_MAXIMA_TECNICA_ADMISIBLE_ITV", 6),
    ("CATEGORIA_HOMOLOGACION_EUROPEA_ITV", 4),
    ("CARROCERIA", 4),
    ("PLAZAS_PIE", 3),
    ("NIVEL_EMISIONES_EURO_ITV", 8),
    ("CONSUMO_WH_KM_ITV", 4),
    ("CLASIFICACION_REGLAMENTO_VEHICULOS_ITV", 4),
    ("CATEGORIA_VEHICULO_ELECTRICO", 4),
    ("AUTONOMIA_VEHICULO_ELECTRICO", 6),
    ("MARCA_VEHICULO_BASE", 30),
    ("FABRICANTE_VEHICULO_BASE", 50),
    ("TIPO_VEHICULO_BASE", 35),
    ("VARIANTE_VEHICULO_BASE", 25),
    ("VERSION_VEHICULO_BASE", 35),
    ("DISTANCIA_EJES_12_ITV", 4),
    ("VIA_ANTERIOR_ITV", 4),
    ("VIA_POSTERIOR_ITV", 4),
    ("TIPO_ALIMENTACION_ITV", 1),
    ("CONTRASENA_HOMOLOGACION_ITV", 25),
    ("ECO_INNOVACION_ITV", 1),
    ("REDUCCION_ECO_ITV", 4),
    ("CODIGO_ECO_ITV", 25),
    ("FEC_PROCESO", 8),
]

HEADERS = [name for name, _ in FIELDS]
RECORD_LEN = sum(width for _, width in FIELDS)
OFFSETS = []
_pos = 0
for _name, _width in FIELDS:
    OFFSETS.append((_pos, _pos + _width))
    _pos += _width


def parse_line(line):
    return {name: line[start:end].strip() for name, (start, end) in zip(HEADERS, OFFSETS)}


def iter_records(txt_path):
    with txt_path.open(encoding="latin-1") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if len(line) == RECORD_LEN:
                yield parse_line(line)


def compile_subdir(subdir):
    txts = sorted(subdir.glob("export_mat_*.txt"))
    if not txts:
        return None
    out_path = subdir / f"{subdir.name}.csv"
    count = 0
    with out_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS)
        writer.writeheader()
        for txt in txts:
            for record in iter_records(txt):
                writer.writerow(record)
                count += 1
    return out_path, count


def main():
    data_dir = Path(__file__).resolve().parent
    subdirs = sorted(p for p in data_dir.iterdir() if p.is_dir())
    if not subdirs:
        print(f"No hay subdirectorios en {data_dir}", file=sys.stderr)
        return 1
    for subdir in subdirs:
        result = compile_subdir(subdir)
        if result is None:
            print(f"{subdir.name}: sin ficheros export_mat_*.txt, se omite")
            continue
        out_path, count = result
        print(f"{out_path}: {count} registros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
