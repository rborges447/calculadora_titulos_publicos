"""Testes do serviço consultas_db (T-003/T-004) com mock de reader."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest

from titulospub.dados.consultas_db import (
    BancoIndisponivelError,
    ColunasInvalidasError,
    IntervaloSemDadosError,
    LimiteExportacaoError,
    TabelaDesconhecidaError,
    consultar,
    exportar_csv,
)
from titulospub.dados.consultas_db import servico as servico_mod
from titulospub.dados.consultas_db.catalogo import FonteConsulta


def _patch_disponibilidade_larga(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita SQLite nos testes; cobre qualquer intervalo pedido."""

    def _fake(fonte: FonteConsulta) -> tuple[date | None, date | None]:
        if fonte.coluna_data is None:
            return None, None
        return date(1900, 1, 1), date(2100, 12, 31)

    monkeypatch.setattr(servico_mod, "obter_intervalo_disponivel", _fake)


class _FakeTable:
    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df
        self.fetch_range_calls: list[tuple[str, str]] = []
        self.fetch_all_calls = 0

    def fetch_range(self, start: str, end: str) -> pd.DataFrame:
        self.fetch_range_calls.append((start, end))
        return self._df.copy()

    def fetch_all(self) -> pd.DataFrame:
        self.fetch_all_calls += 1
        return self._df.copy()


def _make_reader(**tables: pd.DataFrame) -> SimpleNamespace:
    return SimpleNamespace(**{name: _FakeTable(df) for name, df in tables.items()})


@pytest.fixture
def df_cdi() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "data_referencia": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "cdi": [0.12, 0.13],
        }
    )


@pytest.fixture
def df_cdi_grande() -> pd.DataFrame:
    n = 6000
    return pd.DataFrame(
        {
            "data_referencia": pd.date_range("2024-01-01", periods=n, freq="D"),
            "cdi": [0.1] * n,
        }
    )


@pytest.fixture
def df_feriados() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "data": pd.to_datetime(
                ["2024-01-01", "2024-06-01", "2025-01-01"]
            ),
        }
    )


def test_consultar_range_ok(df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch) -> None:
    reader = _make_reader(cdi=df_cdi)
    monkeypatch.setattr(servico_mod, "get_reader", lambda: reader)
    _patch_disponibilidade_larga(monkeypatch)

    resultado = consultar(
        "cdi",
        ["data_referencia", "cdi"],
        data_inicio="2024-01-01",
        data_fim="2024-01-02",
    )

    assert resultado.total_linhas == 2
    assert resultado.truncado is False
    assert len(resultado.rows) == 2
    assert resultado.colunas == ["data_referencia", "cdi"]
    assert resultado.rows[0]["cdi"] == pytest.approx(0.12)
    assert reader.cdi.fetch_range_calls == [("2024-01-01", "2024-01-02")]


def test_consultar_preview_truncado(
    df_cdi_grande: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    reader = _make_reader(cdi=df_cdi_grande)
    monkeypatch.setattr(servico_mod, "get_reader", lambda: reader)
    _patch_disponibilidade_larga(monkeypatch)

    resultado = consultar(
        "cdi",
        ["data_referencia", "cdi"],
        data_inicio="2024-01-01",
        data_fim="2024-12-31",
        limite_preview=5000,
    )

    assert resultado.total_linhas == 6000
    assert resultado.truncado is True
    assert len(resultado.rows) == 5000


def test_consultar_tabela_invalida(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(servico_mod, "get_reader", lambda: _make_reader())

    with pytest.raises(TabelaDesconhecidaError):
        consultar("xyz", ["cdi"], data_inicio="2024-01-01", data_fim="2024-01-02")


def test_consultar_coluna_invalida(
    df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(servico_mod, "get_reader", lambda: _make_reader(cdi=df_cdi))
    _patch_disponibilidade_larga(monkeypatch)

    with pytest.raises(ColunasInvalidasError) as exc_info:
        consultar(
            "cdi",
            ["coluna_inexistente"],
            data_inicio="2024-01-01",
            data_fim="2024-01-02",
        )
    assert "coluna_inexistente" in exc_info.value.colunas_invalidas


def test_consultar_range_sem_datas(
    df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(servico_mod, "get_reader", lambda: _make_reader(cdi=df_cdi))
    _patch_disponibilidade_larga(monkeypatch)

    with pytest.raises(ValueError, match="data_inicio"):
        consultar("cdi", ["cdi"])


def test_consultar_intervalo_largo_ok(
    df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    reader = _make_reader(cdi=df_cdi)
    monkeypatch.setattr(servico_mod, "get_reader", lambda: reader)
    _patch_disponibilidade_larga(monkeypatch)

    resultado = consultar(
        "cdi",
        ["data_referencia", "cdi"],
        data_inicio="2024-01-01",
        data_fim="2025-12-31",
    )
    assert resultado.total_linhas == 2
    assert reader.cdi.fetch_range_calls == [("2024-01-01", "2025-12-31")]


def test_consultar_intervalo_clip_parcial(
    df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    reader = _make_reader(cdi=df_cdi)
    monkeypatch.setattr(servico_mod, "get_reader", lambda: reader)

    def _disp_cdi(_fonte: FonteConsulta) -> tuple[date, date]:
        return date(2024, 1, 1), date(2024, 1, 2)

    monkeypatch.setattr(servico_mod, "obter_intervalo_disponivel", _disp_cdi)

    resultado = consultar(
        "cdi",
        ["data_referencia", "cdi"],
        data_inicio="2023-01-01",
        data_fim="2025-12-31",
    )
    assert resultado.intervalo_ajustado is True
    assert resultado.mensagem_aviso is not None
    assert resultado.data_inicio_efetiva == "2024-01-01"
    assert resultado.data_fim_efetiva == "2024-01-02"
    assert reader.cdi.fetch_range_calls == [("2024-01-01", "2024-01-02")]


def test_consultar_intervalo_sem_intersecao(
    df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(servico_mod, "get_reader", lambda: _make_reader(cdi=df_cdi))

    def _disp_cdi(_fonte: FonteConsulta) -> tuple[date, date]:
        return date(2024, 1, 1), date(2024, 1, 2)

    monkeypatch.setattr(servico_mod, "obter_intervalo_disponivel", _disp_cdi)

    with pytest.raises(IntervaloSemDadosError, match="2024-01-01"):
        consultar(
            "cdi",
            ["cdi"],
            data_inicio="2025-01-01",
            data_fim="2025-12-31",
        )


def test_consultar_snapshot_feriados_com_filtro(
    df_feriados: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    reader = _make_reader(feriados=df_feriados)
    monkeypatch.setattr(servico_mod, "get_reader", lambda: reader)
    _patch_disponibilidade_larga(monkeypatch)

    resultado = consultar(
        "feriados",
        ["data"],
        data_inicio="2024-01-01",
        data_fim="2024-12-31",
    )

    assert reader.feriados.fetch_all_calls == 1
    assert resultado.total_linhas == 2
    assert resultado.rows[0]["data"] == "2024-01-01"


def test_consultar_banco_indisponivel(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise() -> None:
        raise FileNotFoundError("no db")

    monkeypatch.setattr(servico_mod, "get_reader", _raise)
    monkeypatch.setattr(servico_mod, "get_db_path", lambda: "/tmp/missing.db")
    _patch_disponibilidade_larga(monkeypatch)

    with pytest.raises(BancoIndisponivelError):
        consultar(
            "cdi",
            ["cdi"],
            data_inicio="2024-01-01",
            data_fim="2024-01-02",
        )


def test_exportar_csv_bytes_e_bom(
    df_cdi: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        servico_mod, "get_reader", lambda: _make_reader(cdi=df_cdi)
    )
    _patch_disponibilidade_larga(monkeypatch)

    conteudo, nome = exportar_csv(
        "cdi",
        ["data_referencia", "cdi"],
        data_inicio="2024-01-01",
        data_fim="2024-01-02",
    )

    assert nome == "cdi_2024-01-01_2024-01-02.csv"
    assert conteudo.startswith(b"\xef\xbb\xbf")
    texto = conteudo.decode("utf-8-sig")
    linhas = texto.strip().splitlines()
    assert linhas[0] == "data_referencia;cdi"
    assert "01/01/2024" in linhas[1]
    assert "0,12" in linhas[1]
    assert len(linhas) == 3  # header + 2 linhas


def test_exportar_csv_quoting_texto_com_semicolon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    df = pd.DataFrame(
        {
            "tipo_titulo": ["LTN"],
            "data_vencimento": pd.to_datetime(["2026-01-01"]),
            "data_referencia": pd.to_datetime(["2024-01-01"]),
            "taxa_anbima": [12.5],
            "pu": [1000.0],
            "expressao": ["PU; taxa"],
            "status": ["ativo"],
        }
    )
    monkeypatch.setattr(
        servico_mod,
        "get_reader",
        lambda: _make_reader(mercado_secundario=df),
    )
    _patch_disponibilidade_larga(monkeypatch)

    conteudo, _ = exportar_csv(
        "mercado_secundario",
        ["tipo_titulo", "data_referencia", "expressao"],
        data_inicio="2024-01-01",
        data_fim="2024-01-02",
    )
    texto = conteudo.decode("utf-8-sig")
    assert '"PU; taxa"' in texto


def test_exportar_csv_texto_com_virgula(monkeypatch: pytest.MonkeyPatch) -> None:
    df = pd.DataFrame(
        {
            "tipo_titulo": ["LTN"],
            "data_vencimento": pd.to_datetime(["2026-01-01"]),
            "data_referencia": pd.to_datetime(["2024-01-01"]),
            "taxa_anbima": [12.5],
            "pu": [1000.0],
            "expressao": ["foo, bar"],
            "status": ["ativo"],
        }
    )
    monkeypatch.setattr(
        servico_mod,
        "get_reader",
        lambda: _make_reader(mercado_secundario=df),
    )
    _patch_disponibilidade_larga(monkeypatch)

    conteudo, _ = exportar_csv(
        "mercado_secundario",
        ["tipo_titulo", "data_referencia", "expressao"],
        data_inicio="2024-01-01",
        data_fim="2024-01-02",
    )
    linhas = conteudo.decode("utf-8-sig").strip().splitlines()
    assert len(linhas) == 2
    campos = linhas[1].split(";")
    assert len(campos) == 3
    assert campos[2] == "foo, bar"


def test_exportar_csv_snapshot(
    df_feriados: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        servico_mod, "get_reader", lambda: _make_reader(feriados=df_feriados)
    )

    _, nome = exportar_csv("feriados", ["data"])
    assert nome == "feriados_snapshot.csv"


def test_exportar_csv_limite_excedido(monkeypatch: pytest.MonkeyPatch) -> None:
    n = servico_mod.LIMITE_MAX_EXPORTACAO + 1
    df = pd.DataFrame({"data_referencia": range(n), "cdi": [0.1] * n})
    monkeypatch.setattr(
        servico_mod, "get_reader", lambda: _make_reader(cdi=df)
    )
    _patch_disponibilidade_larga(monkeypatch)

    with pytest.raises(LimiteExportacaoError) as exc_info:
        exportar_csv(
            "cdi",
            ["data_referencia", "cdi"],
            data_inicio="2024-01-01",
            data_fim="2024-12-31",
        )
    assert exc_info.value.total_linhas == n
