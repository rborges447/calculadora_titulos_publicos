"""Casos de teste compartilhados para formatação pt-BR (domínio e Dash)."""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd

# (valor, casas_decimais | None, esperado)
CASOS_NUMERO: list[tuple] = [
    (None, None, ""),
    (0, None, "0"),
    (0.12, None, "0,12"),
    (1234.567, None, "1.234,567"),
    (1500000, 0, "1.500.000"),
    (-1234.5, None, "-1.234,5"),
    (0.100000, 6, "0,1"),
]

# (valor, esperado) — valores não-string usam placeholders no parametrize
CASOS_DATA_STRING: list[tuple[str, str]] = [
    ("2024-01-15", "15/01/2024"),
    ("", ""),
]

CASOS_DATA_OBJETOS: list[tuple] = [
    (date(2024, 6, 1), "01/06/2024"),
    (datetime(2024, 12, 31, 10, 30), "31/12/2024"),
    (pd.Timestamp("2024-03-20"), "20/03/2024"),
    (None, ""),
]

CASOS_ROWS = {
    "colunas": ["data_referencia", "cdi", "tipo_titulo", "qtd_operacoes"],
    "rows": [
        {
            "data_referencia": "2024-01-01",
            "cdi": 0.123456,
            "tipo_titulo": "LTN",
            "qtd_operacoes": 1500,
        }
    ],
    "expected": [
        {
            "data_referencia": "01/01/2024",
            "cdi": "0,123456",
            "tipo_titulo": "LTN",
            "qtd_operacoes": "1.500",
        }
    ],
}
