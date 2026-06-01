"""Verifica contrato T-013/T-014 para consumidores de vencimentos.py (Spec 002).

Uso:
    python scripts/verify_vencimentos_contrato.py          # offline (fixtures)
    python scripts/verify_vencimentos_contrato.py --db    # smoke com banco real
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tests.conftest import (  # noqa: E402
    ANBIMAS_KEYS,
    load_golden,
    patch_variaveis_mercado_io,
)
from titulospub.dados.orquestrador import VariaveisMercado  # noqa: E402
from titulospub.dados.vencimentos import (  # noqa: E402
    get_codigos_di_disponiveis,
    get_todos_vencimentos,
)

DATA_BASE = "2026-05-25"
EXPECTED = {"LTN": 12, "LFT": 17, "NTN-B": 15, "NTN-F": 6, "DI": 47}


def verify_offline() -> None:
    golden = load_golden("vencimentos_baseline")

    with patch_variaveis_mercado_io():
        vm = VariaveisMercado()
        anbimas = vm.get_anbimas(data=DATA_BASE)
        bmf = vm.get_bmf(data=DATA_BASE)

    assert ANBIMAS_KEYS.issubset(anbimas.keys()), (
        f"chaves ANBIMA faltando: {ANBIMAS_KEYS - anbimas.keys()}"
    )
    for titulo in ANBIMAS_KEYS:
        df = anbimas[titulo]
        assert "VENCIMENTO" in df.columns, f"{titulo}: coluna VENCIMENTO ausente"
        n = df["VENCIMENTO"].nunique()
        assert n == EXPECTED[titulo], f"{titulo}: esperado {EXPECTED[titulo]}, obtido {n}"

    assert "DI" in bmf and "DI" in bmf["DI"].columns
    di_count = bmf["DI"]["DI"].nunique()
    assert di_count == EXPECTED["DI"], f"DI: esperado 47, obtido {di_count}"

    with patch_variaveis_mercado_io():
        todos = get_todos_vencimentos()
        di_fn = len(get_codigos_di_disponiveis())

    assert todos["ltn"] == golden["ltn"]
    assert todos["lft"] == golden["lft"]
    assert todos["ntnb"] == golden["ntnb"]
    assert todos["ntnf"] == golden["ntnf"]
    assert di_fn == golden["di_codigos_count"]

    print("OK: contrato T-013/T-014 (offline/fixtures)")
    print(
        f"  LTN={len(todos['ltn'])} LFT={len(todos['lft'])} "
        f"NTNB={len(todos['ntnb'])} NTNF={len(todos['ntnf'])} DI={di_fn}"
    )


def verify_db(data: str = DATA_BASE) -> None:
    """Smoke com orquestrador real: atualiza cache a partir do SQLite."""
    golden = load_golden("vencimentos_baseline")

    vm = VariaveisMercado()
    vm.limpar_cache()
    vm.atualizar_tudo(data, verbose=True)

    todos = get_todos_vencimentos()
    di_fn = len(get_codigos_di_disponiveis())

    assert todos["ltn"] == golden["ltn"], "LTN diverge do golden"
    assert todos["lft"] == golden["lft"], "LFT diverge do golden"
    assert todos["ntnb"] == golden["ntnb"], "NTNB diverge do golden"
    assert todos["ntnf"] == golden["ntnf"], "NTNF diverge do golden"
    assert di_fn == golden["di_codigos_count"], "contagem DI diverge do golden"

    print(f"OK: smoke DB (data={data})")
    print(
        f"  LTN={len(todos['ltn'])} LFT={len(todos['lft'])} "
        f"NTNB={len(todos['ntnb'])} NTNF={len(todos['ntnf'])} DI={di_fn}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        action="store_true",
        help="Smoke com banco real (requer .env e gold materializado)",
    )
    parser.add_argument(
        "--data",
        default=DATA_BASE,
        help=f"Data de referência para --db (padrão: {DATA_BASE})",
    )
    args = parser.parse_args()

    verify_offline()
    if args.db:
        verify_db(args.data)


if __name__ == "__main__":
    main()
