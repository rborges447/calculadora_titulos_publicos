#!/usr/bin/env python
"""Exporta golden JSON de cenarios de calculo (Spec 001, Fase 4).

Uso one-shot (offline via fixtures):
    python scripts/export_golden_calculos.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from conftest import (  # noqa: E402
    DATA_BASE_FIXA,
    VariaveisMercadoFixture,
    load_fixture,
    patch_variaveis_mercado_io,
)
from titulospub.core import LFT, LTN, NTNB, NTNF  # noqa: E402
from titulospub.core.equivalencia import equivalencia  # noqa: E402
from titulospub.dados.vencimentos import (  # noqa: E402
    get_codigos_di_disponiveis,
    get_todos_vencimentos,
    get_vencimentos_lft,
    get_vencimentos_ltn,
    get_vencimentos_ntnb,
    get_vencimentos_ntnf,
)

DEFAULT_OUTPUT_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"
DATA_BASE = DATA_BASE_FIXA


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return pd.Timestamp(value).strftime("%Y-%m-%d")
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, float):
        return float(value)
    if isinstance(value, int):
        return int(value)
    return value


def _save_golden(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _build_ltn_golden(vm: VariaveisMercadoFixture) -> dict:
    feriados = vm.get_feriados()
    cdi = vm.get_cdi()
    ltn = LTN(
        data_vencimento_titulo="2027-07-01",
        data_base=DATA_BASE,
        taxa=12.5,
        quantidade=50000,
        variaveis_mercado=vm,
        feriados=feriados,
        cdi=cdi,
    )
    return {
        "data_base": DATA_BASE,
        "data_vencimento": "2027-07-01",
        "taxa": 12.5,
        "quantidade": 50000,
        "dias_liquidacao": 1,
        "outputs": {
            "pu_d0": _json_value(ltn.pu_d0),
            "pu_termo": _json_value(ltn.pu_termo),
            "pu_carregado": _json_value(ltn.pu_carregado),
            "dv01": _json_value(ltn.dv01),
            "hedge_di": _json_value(ltn.hedge_di),
            "financeiro": _json_value(ltn.financeiro),
            "carrego_brl": _json_value(ltn.carrego_brl),
        },
    }


def _build_ntnb_golden(vm: VariaveisMercadoFixture) -> dict:
    feriados = vm.get_feriados()
    cdi = vm.get_cdi()
    ipca_dict = vm.get_ipca_dict()
    ntnb = NTNB(
        data_vencimento_titulo="2035-05-15",
        data_base=DATA_BASE,
        taxa=7.0,
        quantidade=10000,
        variaveis_mercado=vm,
        feriados=feriados,
        cdi=cdi,
        ipca_dict=ipca_dict,
    )
    outputs = {
        "cotacao": _json_value(ntnb.cotacao),
        "pu_d0": _json_value(ntnb.pu_d0),
        "pu_termo": _json_value(ntnb.pu_termo),
        "dv01": _json_value(ntnb.dv01),
        "duration": _json_value(ntnb.duration),
        "carrego_brl": _json_value(ntnb.carrego_brl),
        "hedge_dap": _json_value(ntnb.hedge_dap),
    }
    return {
        "data_base": DATA_BASE,
        "data_vencimento": "2035-05-15",
        "taxa": 7.0,
        "quantidade": 10000,
        "dias_liquidacao": 1,
        "outputs": outputs,
    }


def _build_ntnf_golden(vm: VariaveisMercadoFixture) -> dict:
    feriados = vm.get_feriados()
    cdi = vm.get_cdi()
    ntnf = NTNF(
        data_vencimento_titulo="2029-01-01",
        data_base=DATA_BASE,
        taxa=12.5,
        quantidade=50000,
        variaveis_mercado=vm,
        feriados=feriados,
        cdi=cdi,
    )
    return {
        "data_base": DATA_BASE,
        "data_vencimento": "2029-01-01",
        "taxa": 12.5,
        "quantidade": 50000,
        "dias_liquidacao": 1,
        "outputs": {
            "pu_d0": _json_value(ntnf.pu_d0),
            "pu_termo": _json_value(ntnf.pu_termo),
            "dv01": _json_value(ntnf.dv01),
            "hedge_di": _json_value(ntnf.hedge_di),
            "financeiro": _json_value(ntnf.financeiro),
        },
    }


def _build_lft_golden(vm: VariaveisMercadoFixture) -> dict:
    feriados = vm.get_feriados()
    cdi = vm.get_cdi()
    lft = LFT(
        data_vencimento_titulo="2027-03-01",
        data_base=DATA_BASE,
        taxa=0.01,
        quantidade=10000,
        variaveis_mercado=vm,
        feriados=feriados,
        cdi=cdi,
    )
    return {
        "data_base": DATA_BASE,
        "data_vencimento": "2027-03-01",
        "taxa": 0.01,
        "quantidade": 10000,
        "dias_liquidacao": 1,
        "outputs": {
            "cotacao": _json_value(lft.cotacap),
            "pu_d0": _json_value(lft.pu_d0),
            "pu_termo": _json_value(lft.pu_termo),
            "pu_carregado": _json_value(lft.pu_carregado),
            "financeiro": _json_value(lft.financeiro),
        },
    }


def _build_vencimentos_golden() -> dict:
    anbimas = load_fixture("anbimas")
    bmf = load_fixture("bmf")

    def _venc_list(titulo: str) -> list[str]:
        df = anbimas[titulo]
        vencimentos = df["VENCIMENTO"].unique()
        return sorted(pd.Timestamp(v).strftime("%Y-%m-%d") for v in vencimentos if pd.notna(v))

    di_codigos = sorted(str(c) for c in bmf["DI"]["DI"].unique() if pd.notna(c))

    return {
        "data_base": DATA_BASE,
        "ltn": _venc_list("LTN"),
        "lft": _venc_list("LFT"),
        "ntnb": _venc_list("NTN-B"),
        "ntnf": _venc_list("NTN-F"),
        "di_codigos_count": len(di_codigos),
        "di_codigos_sample": di_codigos[:3],
        "from_functions": {
            "ltn": get_vencimentos_ltn(),
            "lft": get_vencimentos_lft(),
            "ntnb": get_vencimentos_ntnb(),
            "ntnf": get_vencimentos_ntnf(),
            "todos": get_todos_vencimentos(),
            "di_count": len(get_codigos_di_disponiveis()),
        },
    }


def _build_equivalencia_golden() -> dict:
    fixed_today = pd.Timestamp(DATA_BASE)
    with patch("pandas.Timestamp.today", return_value=fixed_today):
        resultado = equivalencia(
            titulo1="LTN",
            venc1="2027-07-01",
            titulo2="NTNF",
            venc2="2029-01-01",
            qtd1=50000,
            tx1=12.5,
            tx2=12.5,
            criterio="dv",
        )
    return {
        "data_base": DATA_BASE,
        "titulo1": "LTN",
        "venc1": "2027-07-01",
        "titulo2": "NTNF",
        "venc2": "2029-01-01",
        "qtd1": 50000,
        "tx1": 12.5,
        "tx2": 12.5,
        "criterio": "dv",
        "resultado": _json_value(resultado),
    }


def export_golden(output_dir: Path, force: bool) -> int:
    scenarios = {
        "ltn_2027_taxa_12_5.json": _build_ltn_golden,
        "ntnb_2035_taxa_7_0.json": _build_ntnb_golden,
        "ntnf_2029_taxa_12_5.json": _build_ntnf_golden,
        "lft_2027_taxa_0_01.json": _build_lft_golden,
    }

    print(f"Exportando golden calculos -> {output_dir}\n")

    with patch_variaveis_mercado_io():
        vm = VariaveisMercadoFixture()

        for filename, builder in scenarios.items():
            dest = output_dir / filename
            if dest.exists() and not force:
                print(f"[SKIP] {filename} ja existe")
                continue
            print(f"Exportando {filename}...")
            data = builder(vm)
            _save_golden(data, dest)
            print(f"[OK] {filename}")

        for filename, builder in [
            ("vencimentos_baseline.json", lambda _vm: _build_vencimentos_golden()),
            ("equivalencia_ltn_ntnf_dv.json", lambda _vm: _build_equivalencia_golden()),
        ]:
            dest = output_dir / filename
            if dest.exists() and not force:
                print(f"[SKIP] {filename} ja existe")
                continue
            print(f"Exportando {filename}...")
            data = builder(vm)
            _save_golden(data, dest)
            print(f"[OK] {filename}")

    readme = output_dir / "README.md"
    readme.write_text(
        f"""# Golden files — calculos (baseline)

**Data base de referencia:** `{DATA_BASE}`

JSON congelados a partir dos titulos e funcoes auxiliares (codigo pre-refatoracao).

## Regenerar

```bash
python scripts/export_golden_calculos.py --force
```

Atualize estes arquivos apenas com justificativa explicita no PR.
""",
        encoding="utf-8",
    )
    print(f"[OK] README gravado em {readme}")
    print("\n[OK] Exportacao concluida.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta golden JSON de calculos")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true", help="Sobrescreve JSON existentes")
    args = parser.parse_args()
    return export_golden(args.output_dir.resolve(), force=args.force)


if __name__ == "__main__":
    sys.exit(main())
