#!/usr/bin/env python
"""Exporta golden JSON de respostas HTTP da API (Spec 001, Fase 5).

Uso (offline via fixtures):
    python scripts/export_golden_api.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from starlette.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from conftest import DATA_BASE_FIXA, load_golden, patch_api_offline  # noqa: E402

DEFAULT_OUTPUT_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"


def _save_golden(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _post(client: TestClient, path: str, payload: dict) -> dict:
    resp = client.post(path, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"POST {path} -> {resp.status_code}: {resp.text}")
    return resp.json()


def export_all(output_dir: Path) -> list[str]:
    generated: list[str] = []
    core_ltn = load_golden("ltn_2027_taxa_12_5")
    core_ntnb = load_golden("ntnb_2035_taxa_7_0")
    core_ntnf = load_golden("ntnf_2029_taxa_12_5")
    core_lft = load_golden("lft_2027_taxa_0_01")
    core_equiv = load_golden("equivalencia_ltn_ntnf_dv")

    ltn_request = {
        "data_vencimento": core_ltn["data_vencimento"],
        "data_base": core_ltn["data_base"],
        "taxa": core_ltn["taxa"],
        "quantidade": core_ltn["quantidade"],
        "dias_liquidacao": core_ltn.get("dias_liquidacao", 1),
    }
    ntnb_request = {
        "data_vencimento": core_ntnb["data_vencimento"],
        "data_base": core_ntnb["data_base"],
        "taxa": core_ntnb["taxa"],
        "quantidade": core_ntnb["quantidade"],
        "dias_liquidacao": core_ntnb.get("dias_liquidacao", 1),
    }
    ntnf_request = {
        "data_vencimento": core_ntnf["data_vencimento"],
        "data_base": core_ntnf["data_base"],
        "taxa": core_ntnf["taxa"],
        "quantidade": core_ntnf["quantidade"],
        "dias_liquidacao": core_ntnf.get("dias_liquidacao", 1),
    }
    lft_request = {
        "data_vencimento": core_lft["data_vencimento"],
        "data_base": core_lft["data_base"],
        "taxa": core_lft["taxa"],
        "quantidade": core_lft["quantidade"],
        "dias_liquidacao": core_lft.get("dias_liquidacao", 1),
    }
    equiv_request = {
        "titulo1": core_equiv["titulo1"],
        "venc1": core_equiv["venc1"],
        "titulo2": core_equiv["titulo2"],
        "venc2": core_equiv["venc2"],
        "qtd1": core_equiv["qtd1"],
        "tx1": core_equiv["tx1"],
        "tx2": core_equiv["tx2"],
        "criterio": core_equiv["criterio"],
    }

    with patch_api_offline():
        from api.main import app

        with TestClient(app) as client:
            ltn_resp = _post(client, "/titulos/ltn", ltn_request)
            ntnb_resp = _post(client, "/titulos/ntnb", ntnb_request)
            ntnf_resp = _post(client, "/titulos/ntnf", ntnf_request)
            lft_resp = _post(client, "/titulos/lft", lft_request)

            fixed_today = pd.Timestamp(DATA_BASE_FIXA)
            with patch("pandas.Timestamp.today", return_value=fixed_today):
                equiv_resp = _post(client, "/equivalencia", equiv_request)

    exports = [
        (
            "api_ltn_response.json",
            {"data_base": DATA_BASE_FIXA, "request": ltn_request, "response": ltn_resp},
        ),
        (
            "api_ntnb_response.json",
            {"data_base": DATA_BASE_FIXA, "request": ntnb_request, "response": ntnb_resp},
        ),
        (
            "api_ntnf_response.json",
            {"data_base": DATA_BASE_FIXA, "request": ntnf_request, "response": ntnf_resp},
        ),
        (
            "api_lft_response.json",
            {"data_base": DATA_BASE_FIXA, "request": lft_request, "response": lft_resp},
        ),
        (
            "api_equivalencia_ltn_ntnf_dv.json",
            {
                "data_base": DATA_BASE_FIXA,
                "request": equiv_request,
                "response": equiv_resp,
            },
        ),
    ]

    for filename, payload in exports:
        path = output_dir / filename
        _save_golden(payload, path)
        generated.append(filename)

    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta golden JSON da API")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretorio de saida",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescreve arquivos existentes",
    )
    args = parser.parse_args()

    existing = list(args.output_dir.glob("api_*.json")) if args.output_dir.exists() else []
    if existing and not args.force:
        print("Golden API ja existem. Use --force para regenerar.")
        for p in sorted(existing):
            print(f"  - {p.name}")
        return 1

    print(f"Exportando golden API em {args.output_dir} ...")
    generated = export_all(args.output_dir)
    print(f"Gerados {len(generated)} arquivos:")
    for name in generated:
        print(f"  - {name}")
    print(f"Concluido em {datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
