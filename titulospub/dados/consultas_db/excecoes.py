"""Exceções de domínio do explorer de consultas ao banco gold (Spec 003)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence


class ConsultaDbError(Exception):
    """Erro base do módulo ``consultas_db``.

    Usado no router da API para capturar falhas de negócio do explorer.
    Não mapeia diretamente a um status HTTP.
    """


class TabelaDesconhecidaError(ConsultaDbError):
    """Tabela solicitada não existe no catálogo (máscara).

    Mapeamento HTTP previsto: ``404``.
    """

    def __init__(self, tabela: str) -> None:
        self.tabela = tabela
        super().__init__(
            f"Tabela '{tabela}' desconhecida. "
            "Use GET /consultas-db/catalogo para ver fontes disponíveis."
        )


class ColunasInvalidasError(ConsultaDbError):
    """Colunas vazias ou fora da whitelist da fonte.

    Mapeamento HTTP previsto: ``422``.
    """

    def __init__(
        self,
        tabela: str,
        *,
        colunas_invalidas: Sequence[str] | None = None,
        motivo: str | None = None,
    ) -> None:
        self.tabela = tabela
        self.colunas_invalidas = tuple(colunas_invalidas or ())
        if motivo:
            msg = motivo
        elif not self.colunas_invalidas:
            msg = (
                f"Nenhuma coluna informada para a tabela '{tabela}'. "
                "Informe ao menos uma coluna permitida pelo catálogo."
            )
        else:
            invalidas = ", ".join(self.colunas_invalidas)
            msg = (
                f"Colunas inválidas para '{tabela}': {invalidas}. "
                "Consulte o catálogo para a whitelist permitida."
            )
        super().__init__(msg)


class TabelaAusenteNoBancoError(ConsultaDbError):
    """Tabela gold do catálogo não existe no SQLite local (schema desatualizado).

    Mapeamento HTTP previsto: ``503``.
    """

    def __init__(self, tabela: str, *, nome_sql: str | None = None) -> None:
        self.tabela = tabela
        self.nome_sql = nome_sql or tabela
        super().__init__(
            f"Dados da fonte '{tabela}' não disponíveis no SQLite "
            f"(tabela/view '{self.nome_sql}' ausente ou vazia). "
            "Execute bbdb.update(data_root=...) para materializar o gold; "
            "fontes compostas (ex.: mercado_com_liquidacoes) exigem as tabelas base no banco."
        )


class BancoIndisponivelError(ConsultaDbError):
    """SQLite do bbdb ausente ou inacessível.

    Mapeamento HTTP previsto: ``503``.
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path).resolve() if path is not None else None
        if self.path is not None:
            msg = (
                f"SQLite do bbdb não encontrado: {self.path}. "
                "Copie .env.example para .env, ajuste BBDB_DB_PATH e execute "
                "bbdb.update(data_root=...) para materializar o banco."
            )
        else:
            msg = (
                "Banco de dados indisponível. "
                "Copie .env.example para .env, ajuste BBDB_DB_PATH e execute "
                "bbdb.update(data_root=...) para materializar o banco."
            )
        super().__init__(msg)


class IntervaloSemDadosError(ConsultaDbError):
    """Pedido sem interseção com as datas existentes no banco.

    Mapeamento HTTP previsto: ``422``.
    """

    def __init__(
        self,
        tabela: str,
        *,
        pedido_inicio: str | None = None,
        pedido_fim: str | None = None,
        disponivel_inicio: str | None = None,
        disponivel_fim: str | None = None,
        sem_dados_na_fonte: bool = False,
    ) -> None:
        self.tabela = tabela
        self.pedido_inicio = pedido_inicio
        self.pedido_fim = pedido_fim
        self.disponivel_inicio = disponivel_inicio
        self.disponivel_fim = disponivel_fim
        self.sem_dados_na_fonte = sem_dados_na_fonte

        if sem_dados_na_fonte:
            msg = f"A fonte '{tabela}' não possui dados no banco."
        elif disponivel_inicio and disponivel_fim:
            msg = (
                f"Não há dados para '{tabela}' no período solicitado "
                f"({pedido_inicio} a {pedido_fim}). "
                f"Dados disponíveis apenas entre {disponivel_inicio} e {disponivel_fim}."
            )
        else:
            msg = f"Não há dados para '{tabela}' no período solicitado."
        super().__init__(msg)


class LimiteExportacaoError(ConsultaDbError):
    """Exportação CSV excede o limite máximo de linhas.

    Mapeamento HTTP previsto: ``422``.
    """

    def __init__(self, total_linhas: int, limite: int) -> None:
        self.total_linhas = total_linhas
        self.limite = limite
        super().__init__(
            f"Exportação excede o limite de {limite:,} linhas "
            f"({total_linhas:,} linhas após filtros). "
            "Reduza o intervalo de datas ou as colunas solicitadas."
        )
