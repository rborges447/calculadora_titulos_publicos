"""Testes de disponibilidade de datas no SQLite (consultas_db)."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from titulospub.dados.consultas_db.catalogo import obter_fonte
from titulospub.dados.consultas_db.disponibilidade import obter_intervalo_disponivel
from titulospub.dados.consultas_db.excecoes import TabelaAusenteNoBancoError


@pytest.fixture
def sqlite_cdi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "app.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE cdi (
                data_referencia TEXT NOT NULL,
                cdi REAL NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO cdi (data_referencia, cdi) VALUES (?, ?)",
            [
                ("2024-01-01", 0.12),
                ("2024-06-15", 0.13),
            ],
        )
    monkeypatch.setattr(
        "titulospub.dados.consultas_db.disponibilidade.get_db_path",
        lambda: db_path,
    )
    return db_path


def test_obter_intervalo_disponivel_cdi(sqlite_cdi: Path) -> None:
    fonte = obter_fonte("cdi")
    disp_min, disp_max = obter_intervalo_disponivel(fonte)
    assert disp_min == date(2024, 1, 1)
    assert disp_max == date(2024, 6, 15)


def test_obter_intervalo_sem_coluna_data() -> None:
    fonte = obter_fonte("titulos_publicos")
    assert obter_intervalo_disponivel(fonte) == (None, None)


@pytest.fixture
def sqlite_cdi_uppercase(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """bbdb materializa tabelas com nomes em maiúsculas."""
    db_path = tmp_path / "app.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE CDI (data_referencia TEXT NOT NULL, cdi REAL NOT NULL)"
        )
        conn.executemany(
            "INSERT INTO CDI (data_referencia, cdi) VALUES (?, ?)",
            [("2024-03-01", 0.11), ("2024-03-31", 0.12)],
        )
    monkeypatch.setattr(
        "titulospub.dados.consultas_db.disponibilidade.get_db_path",
        lambda: db_path,
    )
    return db_path


def test_obter_intervalo_resolve_tabela_maiuscula(sqlite_cdi_uppercase: Path) -> None:
    fonte = obter_fonte("cdi")
    disp_min, disp_max = obter_intervalo_disponivel(fonte)
    assert disp_min == date(2024, 3, 1)
    assert disp_max == date(2024, 3, 31)


@pytest.fixture
def sqlite_mercado_composto(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "app.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE MERCADO_SECUNDARIO (data_referencia TEXT, titulo TEXT)"
        )
        conn.execute(
            "CREATE TABLE LIQUIDACOES_MERCADO (data_referencia TEXT, titulo TEXT)"
        )
        conn.execute(
            "INSERT INTO MERCADO_SECUNDARIO VALUES ('2024-01-10', 'LTN')"
        )
        conn.execute(
            "INSERT INTO LIQUIDACOES_MERCADO VALUES ('2024-02-20', 'LTN')"
        )
    monkeypatch.setattr(
        "titulospub.dados.consultas_db.disponibilidade.get_db_path",
        lambda: db_path,
    )
    return db_path


def test_obter_intervalo_mercado_com_liquidacoes_composto(
    sqlite_mercado_composto: Path,
) -> None:
    fonte = obter_fonte("mercado_com_liquidacoes")
    disp_min, disp_max = obter_intervalo_disponivel(fonte)
    assert disp_min == date(2024, 1, 10)
    assert disp_max == date(2024, 2, 20)


@pytest.fixture
def sqlite_sem_bases_mercado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "app.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE CDI (data_referencia TEXT, cdi REAL)")
    monkeypatch.setattr(
        "titulospub.dados.consultas_db.disponibilidade.get_db_path",
        lambda: db_path,
    )
    return db_path


def test_obter_intervalo_mercado_com_liquidacoes_sem_bases(
    sqlite_sem_bases_mercado: Path,
) -> None:
    fonte = obter_fonte("mercado_com_liquidacoes")
    with pytest.raises(TabelaAusenteNoBancoError) as exc_info:
        obter_intervalo_disponivel(fonte)
    assert "mercado_com_liquidacoes" in str(exc_info.value)
    assert "bbdb.update" in str(exc_info.value)
