#!/usr/bin/env python3
"""Sincroniza y compila los microdatos diarios de matriculaciones de la DGT.

El script:
  1. Lee el listado de la web de la DGT y obtiene los enlaces a los ZIP diarios.
  2. Descarga los dias que aun no esten en el CSV de su mes, guardando cada ZIP
     en `data/YYYYMM/` (se crea el subdirectorio si no existe).
  3. Descomprime los ZIP y los elimina.
  4. Anade los registros nuevos al CSV `data/YYYYMM/YYYYMM.csv` (o lo reconstruye
     con `--force`).
  5. Borra los ficheros `.txt` una vez volcados al CSV.

Los ficheros `.txt` tienen formato oficial de ancho fijo (69 campos, 714
caracteres por registro).

Uso:
    python3 data/sync_matriculaciones.py [--force] [--data-dir DIR] [--url URL]
"""

import argparse
import csv
import re
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

DEFAULT_URL = (
    "https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/"
    "matriculaciones-automoviles-diario.html?nocache=1"
)
USER_AGENT = "Mozilla/5.0 (compatible; matriculas-dgt/1.0)"
LINK_RE = re.compile(r"https?://[^\s\"'<>]+/export_mat_(\d{8})\.zip")
TXT_GLOB = "export_mat_*.txt"

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


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def find_links(html):
    """Devuelve {YYYYMMDD: url} de los ZIP de matriculaciones de la web."""
    links = {}
    for match in LINK_RE.finditer(html.decode("utf-8", errors="replace")):
        links[match.group(1)] = match.group(0)
    return links


def txt_date(txt_path):
    """Fecha YYYYMMDD a partir de `export_mat_YYYYMMDD.txt`."""
    return txt_path.stem.rsplit("_", 1)[-1]


def date_to_fec(date):
    """YYYYMMDD -> DDMMYYYY (formato del campo FEC_MATRICULA)."""
    return f"{date[6:8]}{date[4:6]}{date[0:4]}"


def parse_line(line):
    return {name: line[start:end].strip() for name, (start, end) in zip(HEADERS, OFFSETS)}


def iter_records(txt_path):
    with txt_path.open(encoding="latin-1") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if len(line) == RECORD_LEN:
                yield parse_line(line)


def existing_fec_dates(csv_path):
    """Conjunto de valores de FEC_MATRICULA (DDMMYYYY) ya presentes en el CSV."""
    dates = set()
    if not csv_path.exists():
        return dates
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return dates
        try:
            idx = header.index("FEC_MATRICULA")
        except ValueError:
            return dates
        for row in reader:
            if row:
                dates.add(row[idx])
    return dates


def append_records(csv_path, txt_paths):
    """Anade los registros de los `.txt` al CSV (creandolo con cabecera si falta)."""
    exists = csv_path.exists() and csv_path.stat().st_size > 0
    count = 0
    with csv_path.open("a" if exists else "w",
                       encoding="utf-8" if exists else "utf-8-sig",
                       newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS)
        if not exists:
            writer.writeheader()
        for txt in txt_paths:
            for record in iter_records(txt):
                writer.writerow(record)
                count += 1
    return count


def rebuild_csv(subdir):
    """Reconstruye el CSV completo del subdirectorio a partir de los `.txt`."""
    txts = sorted(subdir.glob(TXT_GLOB))
    csv_path = subdir / f"{subdir.name}.csv"
    count = 0
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS)
        writer.writeheader()
        for txt in txts:
            for record in iter_records(txt):
                writer.writerow(record)
                count += 1
    return csv_path, count


def download_zip(url, zip_path):
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = zip_path.with_suffix(".zip.part")
    tmp_path.write_bytes(fetch(url))
    tmp_path.replace(zip_path)


def download_day(date, url, subdir):
    """Descarga y descomprime un dia concreto; borra el ZIP resultante."""
    zip_path = subdir / f"export_mat_{date}.zip"
    txt_path = subdir / f"export_mat_{date}.txt"
    if txt_path.exists():
        return txt_path
    if not zip_path.exists():
        download_zip(url, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(subdir)
    zip_path.unlink()
    return txt_path


def sync(data_dir, url, force=False):
    print(f"Leyendo listado: {url}")
    links = find_links(fetch(url))
    if not links:
        print("No se han encontrado enlaces export_mat_*.zip", file=sys.stderr)
        return 1

    by_month = defaultdict(list)
    for date, link in links.items():
        by_month[date[:6]].append((date, link))

    data_dir.mkdir(parents=True, exist_ok=True)
    disk_months = {p.name for p in data_dir.iterdir() if p.is_dir() and p.name.isdigit()}
    months = sorted(set(by_month) | disk_months)

    total_downloaded = 0
    for month in months:
        subdir = data_dir / month
        csv_path = subdir / f"{month}.csv"
        known = set() if force else existing_fec_dates(csv_path)

        downloaded = 0
        for date, link in sorted(by_month.get(month, [])):
            if date_to_fec(date) in known:
                continue
            if not force and (subdir / f"export_mat_{date}.txt").exists():
                continue
            print(f"Descargando {date} -> {(subdir / f'export_mat_{date}.zip').relative_to(data_dir.parent)}")
            download_day(date, link, subdir)
            downloaded += 1
        total_downloaded += downloaded

        txts = sorted(subdir.glob(TXT_GLOB))
        if not txts:
            continue

        if force:
            out_path, count = rebuild_csv(subdir)
            print(f"Recompilado {out_path.relative_to(data_dir.parent)}: {count} registros")
        else:
            new_txts = [t for t in txts if date_to_fec(txt_date(t)) not in known]
            if new_txts:
                count = append_records(csv_path, new_txts)
                print(f"Anadidos {count} registros a {csv_path.relative_to(data_dir.parent)} "
                      f"({len(new_txts)} dias)")
            else:
                print(f"{csv_path.relative_to(data_dir.parent)} ya estaba actualizado")

        for txt in txts:
            txt.unlink()
        print(f"Borrados {len(txts)} .txt en {subdir.relative_to(data_dir.parent)}")

    print(f"Descargados {total_downloaded} ZIP nuevos")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent,
                        help="Directorio de datos (por defecto, el del script)")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL del listado de la DGT")
    parser.add_argument("--force", action="store_true",
                        help="Reescribe los CSV desde cero volviendo a descargar todo")
    args = parser.parse_args()
    return sync(args.data_dir, args.url, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
