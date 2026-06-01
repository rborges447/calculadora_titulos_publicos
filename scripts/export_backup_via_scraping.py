#!/usr/bin/env python
"""Exporta snapshot de mercado via scraping (operacional, requer rede).

Grava pickles em ``backup_snapshots/data=YYYY-MM-DD/`` para uso manual quando
``database/app.db`` está indisponível.

Uso:
    python scripts/export_backup_via_scraping.py --data-base 2026-05-25
"""

from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from titulospub.dados.transforms.anbimas import anbimas_from_scraping
from titulospub.dados.transforms.bmf import bmf_from_scraping
from titulospub.dados.transforms.cdi import cdi_from_scraping
from titulospub.dados.transforms.feriados import feriados_from_scraping
from titulospub.dados.transforms.vna_lft import vna_lft_from_scraping
from titulospub.utils.datas import adicionar_dias_uteis

DEFAULT_DATA_BASE = "2026-05-25"


def _session_data(data_base: pd.Timestamp) -> pd.Timestamp:
    hoje = pd.Timestamp.today().normalize()
    if data_base == hoje:
        return adicionar_dias_uteis(hoje, n_dias=-1)
    return data_base


def export_backup(data_base: str, output_root: Path) -> int:
    data_ts = pd.Timestamp(data_base).normalize()
    session = _session_data(data_ts)
    out_dir = output_root / f"data={data_ts.strftime('%Y-%m-%d')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    exports = {
        "feriados.pkl": lambda: feriados_from_scraping(),
        "cdi.pkl": lambda: cdi_from_scraping(data_ts),
        "vna_lft.pkl": lambda: vna_lft_from_scraping(data_ts),
        "anbimas.pkl": lambda: anbimas_from_scraping(session),
        "bmf.pkl": lambda: bmf_from_scraping(session),
    }

    errors: list[str] = []
    for name, fn in exports.items():
        dest = out_dir / name
        try:
            print(f"Exportando {name}...")
            value = fn()
            with open(dest, "wb") as f:
                pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"[OK] {dest}")
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            print(f"[ERRO] {name}: {exc}")

    if errors:
        print(f"\n[FALHA] {len(errors)} export(s) com erro.")
        return 1

    print(f"\n[OK] Snapshot em {out_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta backup via scraping")
    parser.add_argument("--data-base", default=DEFAULT_DATA_BASE)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "backup_snapshots",
    )
    args = parser.parse_args()
    return export_backup(args.data_base, args.output_dir.resolve())


if __name__ == "__main__":
    sys.exit(main())
