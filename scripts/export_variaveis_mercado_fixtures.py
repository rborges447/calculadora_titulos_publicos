#!/usr/bin/env python
"""Exporta outputs de VariaveisMercado.get_*() para fixtures de baseline (Spec 001).

Uso one-shot (requer rede e/ou backup Excel local):
    python scripts/export_variaveis_mercado_fixtures.py --force

Não altera código de produção — apenas grava pickles em tests/fixtures/.
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

# Garante import do pacote a partir da raiz do repositório
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from titulospub.dados.orquestrador import VariaveisMercado  # noqa: E402

DEFAULT_DATA_BASE = "2026-05-25"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "tests" / "fixtures" / "variaveis_mercado"

ANBIMAS_KEYS_REQUIRED = {"LTN", "NTN-B", "NTN-F", "LFT"}
ANBIMAS_COLUMNS = {"TITULO", "DATA", "VENCIMENTO", "ANBIMA", "PU"}
BMF_KEYS_REQUIRED = {"DI", "DAP"}
IPCA_KEYS_REQUIRED = {
    "ULTIMO_MES_IPCA",
    "INDICE_IPCA_DATA_BASE",
    "INDICE_IPCA_FECHADO_ATUAL",
    "INDICE_IPCA_FECHADO_ANTERIOR",
    "VAR_IPCA_ATUAL",
    "VAR_IPCA_ANTERIOR",
    "IPCA_PROJ",
    "IPCA_USADO",
}

MANDATORY_FIXTURES = {"feriados.pkl", "ipca_dict.pkl", "cdi.pkl", "anbimas.pkl", "bmf.pkl"}
OPTIONAL_FIXTURES = {"vna_lft.pkl"}


def _save_pickle(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def _describe_value(obj: Any) -> dict[str, Any]:
    if isinstance(obj, list):
        return {"type": "list", "size": len(obj)}
    if isinstance(obj, dict):
        info: dict[str, Any] = {"type": "dict", "keys": sorted(obj.keys())}
        if all(isinstance(v, pd.DataFrame) for v in obj.values()):
            info["dataframes"] = {k: {"rows": len(v), "columns": list(v.columns)} for k, v in obj.items()}
        return info
    if isinstance(obj, (int, float)):
        return {"type": type(obj).__name__, "value": obj}
    return {"type": type(obj).__name__}


def _validate_feriados(feriados: list) -> None:
    if not isinstance(feriados, list):
        raise TypeError(f"feriados deve ser list, recebeu {type(feriados)}")
    if len(feriados) == 0:
        raise ValueError("feriados está vazio")


def _validate_ipca_dict(ipca_dict: dict) -> None:
    if not isinstance(ipca_dict, dict):
        raise TypeError(f"ipca_dict deve ser dict, recebeu {type(ipca_dict)}")
    missing = IPCA_KEYS_REQUIRED - set(ipca_dict.keys())
    if missing:
        raise ValueError(f"ipca_dict sem chaves: {sorted(missing)}")


def _validate_cdi(cdi: float) -> None:
    if not isinstance(cdi, (int, float)):
        raise TypeError(f"cdi deve ser numérico, recebeu {type(cdi)}")


def _validate_anbimas(anbimas_dict: dict[str, pd.DataFrame]) -> None:
    if not isinstance(anbimas_dict, dict):
        raise TypeError(f"anbimas deve ser dict, recebeu {type(anbimas_dict)}")
    missing_keys = ANBIMAS_KEYS_REQUIRED - set(anbimas_dict.keys())
    if missing_keys:
        raise ValueError(f"anbimas sem chaves obrigatórias: {sorted(missing_keys)}")
    for titulo, df in anbimas_dict.items():
        if titulo not in ANBIMAS_KEYS_REQUIRED:
            continue
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"anbimas[{titulo!r}] deve ser DataFrame")
        missing_cols = ANBIMAS_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValueError(f"anbimas[{titulo!r}] sem colunas: {sorted(missing_cols)}")
        if len(df) == 0:
            raise ValueError(f"anbimas[{titulo!r}] está vazio")


def _validate_bmf(bmf_dict: dict[str, pd.DataFrame]) -> None:
    if not isinstance(bmf_dict, dict):
        raise TypeError(f"bmf deve ser dict, recebeu {type(bmf_dict)}")
    missing_keys = BMF_KEYS_REQUIRED - set(bmf_dict.keys())
    if missing_keys:
        raise ValueError(f"bmf sem chaves obrigatórias: {sorted(missing_keys)}")
    for nome in BMF_KEYS_REQUIRED:
        df = bmf_dict[nome]
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"bmf[{nome!r}] deve ser DataFrame")
        expected_cols = {"DATA", "DATA_VENCIMENTO", nome, "ADJ"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise ValueError(f"bmf[{nome!r}] sem colunas: {sorted(missing_cols)}")
        if len(df) == 0:
            raise ValueError(f"bmf[{nome!r}] está vazio")
        if not df["DATA_VENCIMENTO"].is_monotonic_increasing:
            raise ValueError(f"bmf[{nome!r}] não está ordenado por DATA_VENCIMENTO ascendente")


def _validate_vna_lft(vna_lft: float) -> None:
    if not isinstance(vna_lft, (int, float)):
        raise TypeError(f"vna_lft deve ser numérico, recebeu {type(vna_lft)}")


def _export_feriados(vm: VariaveisMercado, force_update: bool) -> list:
    feriados = vm.get_feriados(force_update=force_update)
    _validate_feriados(feriados)
    return feriados


def _export_ipca_dict(
    vm: VariaveisMercado, data_base: pd.Timestamp, feriados: list, force_update: bool
) -> dict:
    ipca_dict = vm.get_ipca_dict(data=data_base, feriados=feriados, force_update=force_update)
    _validate_ipca_dict(ipca_dict)
    return ipca_dict


def _export_cdi(vm: VariaveisMercado, force_update: bool) -> float:
    cdi = vm.get_cdi(force_update=force_update)
    _validate_cdi(cdi)
    return cdi


def _export_anbimas(vm: VariaveisMercado, data_base: pd.Timestamp, force_update: bool) -> dict:
    anbimas_dict = vm.get_anbimas(data=data_base, force_update=force_update)
    _validate_anbimas(anbimas_dict)
    return anbimas_dict


def _export_bmf(vm: VariaveisMercado, data_base: pd.Timestamp, force_update: bool) -> dict:
    bmf_dict = vm.get_bmf(data=data_base, force_update=force_update)
    _validate_bmf(bmf_dict)
    return bmf_dict


def _try_export_vna_lft(vm: VariaveisMercado, data_base: pd.Timestamp, force_update: bool) -> float:
    vna_lft = vm.get_vna_lft(data=data_base, force_update=force_update)
    _validate_vna_lft(vna_lft)
    return vna_lft


def _write_manifest(output_dir: Path, data_base: str, fixtures_meta: dict) -> None:
    manifest = {
        "data_base": data_base,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "strategy": "VariaveisMercado.get_* (cache -> scraping -> backup)",
        "fixtures": fixtures_meta,
    }
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[OK] Manifest gravado em {manifest_path}")


def _write_readme(output_dir: Path, data_base: str, fixtures_meta: dict) -> None:
    vna_status = fixtures_meta.get("vna_lft.pkl", {}).get("status", "unknown")
    vna_note = ""
    if vna_status == "skipped":
        reason = fixtures_meta["vna_lft.pkl"].get("reason", "desconhecido")
        vna_note = f"\n\n> **vna_lft.pkl** não foi exportado: {reason}\n> Testes de contrato usarão `@pytest.mark.skip` até regeneração.\n"

    readme = f"""# Fixtures — VariaveisMercado (baseline)

**Data base de referência:** `{data_base}`

Pickles congelados a partir de `VariaveisMercado.get_*()` (código pré-refatoração).
Usados pela suite de regressão da Spec 001.

## Regenerar baseline

```bash
python scripts/export_variaveis_mercado_fixtures.py --data-base {data_base} --force
```

Requer rede e/ou arquivos em `titulospub/dados/backup_excel/`.

## Atualização

Só altere estes arquivos com **justificativa explícita** no PR (mudança intencional
de contrato ou correção de bug comprovada).
{vna_note}
"""
    readme_path = output_dir / "README.md"
    readme_path.write_text(readme, encoding="utf-8")
    print(f"[OK] README gravado em {readme_path}")


def _smoke_load_pickles(output_dir: Path) -> None:
    for pkl in sorted(output_dir.glob("*.pkl")):
        with open(pkl, "rb") as f:
            pickle.load(f)
        print(f"[OK] Smoke load: {pkl.name}")


def export_fixtures(
    data_base: str,
    output_dir: Path,
    force: bool,
    force_update: bool,
) -> int:
    data_ts = pd.Timestamp(data_base).normalize()
    output_dir.mkdir(parents=True, exist_ok=True)

    fixtures_meta: dict[str, dict] = {}
    errors: list[str] = []

    vm = VariaveisMercado()

    def _maybe_skip(filename: str) -> bool:
        dest = output_dir / filename
        return dest.exists() and not force

    print(f"Exportando baseline VariaveisMercado (data_base={data_base}) -> {output_dir}\n")

    # --- feriados ---
    filename = "feriados.pkl"
    if _maybe_skip(filename):
        print(f"[SKIP] {filename} já existe (use --force para sobrescrever)")
        fixtures_meta[filename] = {"status": "skipped", "reason": "arquivo existente"}
    else:
        try:
            print(f"Exportando {filename}...")
            feriados = _export_feriados(vm, force_update=force_update)
            _save_pickle(feriados, output_dir / filename)
            fixtures_meta[filename] = {"status": "ok", **_describe_value(feriados)}
            print(f"[OK] {filename}")
        except Exception as e:
            errors.append(f"{filename}: {e}")
            fixtures_meta[filename] = {"status": "error", "reason": str(e)}
            print(f"[ERRO] {filename}: {e}")
            feriados = None

    if feriados is None:
        _write_manifest(output_dir, data_base, fixtures_meta)
        print("\n[FALHA] feriados é obrigatório; abortando exportação.")
        return 1

    # --- ipca_dict ---
    filename = "ipca_dict.pkl"
    if _maybe_skip(filename):
        print(f"[SKIP] {filename} já existe")
        fixtures_meta[filename] = {"status": "skipped", "reason": "arquivo existente"}
    else:
        try:
            print(f"Exportando {filename}...")
            ipca_dict = _export_ipca_dict(vm, data_ts, feriados, force_update=force_update)
            _save_pickle(ipca_dict, output_dir / filename)
            fixtures_meta[filename] = {"status": "ok", **_describe_value(ipca_dict)}
            print(f"[OK] {filename}")
        except Exception as e:
            errors.append(f"{filename}: {e}")
            fixtures_meta[filename] = {"status": "error", "reason": str(e)}
            print(f"[ERRO] {filename}: {e}")

    # --- cdi ---
    filename = "cdi.pkl"
    if _maybe_skip(filename):
        print(f"[SKIP] {filename} já existe")
        fixtures_meta[filename] = {"status": "skipped", "reason": "arquivo existente"}
    else:
        try:
            print(f"Exportando {filename}...")
            cdi = _export_cdi(vm, force_update=force_update)
            _save_pickle(cdi, output_dir / filename)
            fixtures_meta[filename] = {"status": "ok", **_describe_value(cdi)}
            print(f"[OK] {filename}")
        except Exception as e:
            errors.append(f"{filename}: {e}")
            fixtures_meta[filename] = {"status": "error", "reason": str(e)}
            print(f"[ERRO] {filename}: {e}")

    # --- anbimas ---
    filename = "anbimas.pkl"
    if _maybe_skip(filename):
        print(f"[SKIP] {filename} já existe")
        fixtures_meta[filename] = {"status": "skipped", "reason": "arquivo existente"}
    else:
        try:
            print(f"Exportando {filename}...")
            anbimas_dict = _export_anbimas(vm, data_ts, force_update=True)
            _save_pickle(anbimas_dict, output_dir / filename)
            fixtures_meta[filename] = {"status": "ok", **_describe_value(anbimas_dict)}
            print(f"[OK] {filename}")
        except Exception as e:
            errors.append(f"{filename}: {e}")
            fixtures_meta[filename] = {"status": "error", "reason": str(e)}
            print(f"[ERRO] {filename}: {e}")

    # --- bmf ---
    filename = "bmf.pkl"
    if _maybe_skip(filename):
        print(f"[SKIP] {filename} já existe")
        fixtures_meta[filename] = {"status": "skipped", "reason": "arquivo existente"}
    else:
        try:
            print(f"Exportando {filename}...")
            bmf_dict = _export_bmf(vm, data_ts, force_update=True)
            _save_pickle(bmf_dict, output_dir / filename)
            fixtures_meta[filename] = {"status": "ok", **_describe_value(bmf_dict)}
            print(f"[OK] {filename}")
        except Exception as e:
            errors.append(f"{filename}: {e}")
            fixtures_meta[filename] = {"status": "error", "reason": str(e)}
            print(f"[ERRO] {filename}: {e}")

    # --- vna_lft (opcional) ---
    filename = "vna_lft.pkl"
    if _maybe_skip(filename):
        print(f"[SKIP] {filename} já existe")
        fixtures_meta[filename] = {"status": "skipped", "reason": "arquivo existente"}
    else:
        try:
            print(f"Exportando {filename} (opcional)...")
            vna_lft = _try_export_vna_lft(vm, data_ts, force_update=True)
            _save_pickle(vna_lft, output_dir / filename)
            fixtures_meta[filename] = {"status": "ok", **_describe_value(vna_lft)}
            print(f"[OK] {filename}")
        except Exception as e:
            fixtures_meta[filename] = {"status": "skipped", "reason": str(e)}
            print(f"[AVISO] {filename} não exportado (opcional): {e}")

    _write_manifest(output_dir, data_base, fixtures_meta)
    _write_readme(output_dir, data_base, fixtures_meta)

    if list(output_dir.glob("*.pkl")):
        print("\nSmoke load dos pickles:")
        _smoke_load_pickles(output_dir)

    print("\n--- Resumo ---")
    for name, meta in fixtures_meta.items():
        print(f"  {name}: {meta.get('status', '?')}")

    mandatory_failed = [
        f
        for f in MANDATORY_FIXTURES
        if fixtures_meta.get(f, {}).get("status") not in ("ok", "skipped")
    ]
    if mandatory_failed or any(
        fixtures_meta.get(f, {}).get("status") == "error" for f in MANDATORY_FIXTURES
    ):
        print(f"\n[FALHA] Fixtures obrigatórios com erro: {mandatory_failed or errors}")
        return 1

    print("\n[OK] Exportação concluída.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporta fixtures de baseline de VariaveisMercado para tests/fixtures/"
    )
    parser.add_argument(
        "--data-base",
        default=DEFAULT_DATA_BASE,
        help=f"Data base de referência (default: {DEFAULT_DATA_BASE})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretório de destino dos pickles",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescreve pickles existentes no destino",
    )
    parser.add_argument(
        "--force-update",
        action="store_true",
        default=True,
        help="Passa force_update=True aos get_* (default: True)",
    )
    parser.add_argument(
        "--no-force-update",
        action="store_false",
        dest="force_update",
        help="Usa cache local do orquestrador quando disponível",
    )
    args = parser.parse_args()

    return export_fixtures(
        data_base=args.data_base,
        output_dir=args.output_dir.resolve(),
        force=args.force,
        force_update=args.force_update,
    )


if __name__ == "__main__":
    sys.exit(main())
