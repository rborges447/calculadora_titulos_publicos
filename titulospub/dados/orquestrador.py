import pandas as pd

from titulospub.dados.cache import clear_cache, load_cache, save_cache
from titulospub.dados.resilience import fetch_with_fallback
from titulospub.dados.transforms.anbimas import anbimas_from_db, anbimas_from_scraping
from titulospub.dados.transforms.bmf import bmf_from_db, bmf_from_scraping
from titulospub.dados.transforms.cdi import cdi_from_db, cdi_from_scraping
from titulospub.dados.transforms.feriados import feriados_from_db, feriados_from_scraping
from titulospub.dados.transforms.ipca import ipca_dict_from_db
from titulospub.dados.transforms.ptax import ptax_from_db
from titulospub.dados.transforms.vna_lft import vna_lft_from_db, vna_lft_from_scraping
from titulospub.utils.datas import adicionar_dias_uteis


def _data_leitura_mercado_sessao(data: pd.Timestamp | str | None) -> pd.Timestamp:
    """Data efetiva de leitura ANBIMA/BMF: literal, exceto se for hoje → D-1 útil."""
    hoje = pd.Timestamp.today().normalize()
    base = hoje if data is None else pd.Timestamp(data).normalize()
    if base == hoje:
        return adicionar_dias_uteis(hoje, n_dias=-1)
    return base


class VariaveisMercado:
    def __init__(self):
        self._feriados = None
        self._ipca_dict = None
        self._cdi = None
        self._vna_lft = None
        self._anbimas = None
        self._bmf = None
        self._ptax = None

    @staticmethod
    def _require_data(data, force_update: bool, method: str) -> None:
        if force_update and data is None:
            raise ValueError(
                f"{method}: parâmetro 'data' é obrigatório quando force_update=True"
            )

    def get_feriados(self, force_update=False):

        if self._feriados is not None and not force_update:
            return self._feriados

        if not force_update:
            feriados = load_cache("feriados.pkl")
            if feriados:
                self._feriados = feriados
                return feriados

        print("Carregando feriados via banco local...")
        feriados = fetch_with_fallback(
            "feriados",
            feriados_from_db,
            feriados_from_scraping,
        )
        self._feriados = feriados
        save_cache(feriados, "feriados.pkl")
        return feriados

    def get_ipca_dict(self, data=None, feriados=None, force_update=False):

        if self._ipca_dict is not None and not force_update:
            return self._ipca_dict

        if not force_update:
            ipca_dict = load_cache("ipca_dict.pkl")
            if ipca_dict is not None:
                self._ipca_dict = ipca_dict
                return ipca_dict

        self._require_data(data, force_update, "get_ipca_dict")

        if data is None:
            data = pd.Timestamp.today().normalize()

        print("Carregando IPCA dict via banco local...")
        ipca_dict = ipca_dict_from_db(data)

        self._ipca_dict = ipca_dict
        save_cache(ipca_dict, "ipca_dict.pkl")
        return ipca_dict

    def get_cdi(self, data=None, force_update=False):
        if self._cdi is not None and not force_update:
            return self._cdi

        if not force_update:
            cdi = load_cache("cdi.pkl")
            if cdi is not None:
                self._cdi = cdi
                return cdi

        self._require_data(data, force_update, "get_cdi")

        if data is None:
            data = pd.Timestamp.today().normalize()

        print("Carregando CDI via banco local...")
        cdi = fetch_with_fallback(
            "cdi",
            cdi_from_db,
            cdi_from_scraping,
            data=data,
        )

        self._cdi = cdi
        save_cache(cdi, "cdi.pkl")
        return cdi

    def get_ptax(self, data=None, force_update=False):
        if self._ptax is not None and not force_update:
            return self._ptax

        if not force_update:
            ptax = load_cache("ptax.pkl")
            if ptax is not None:
                self._ptax = ptax
                return ptax

        self._require_data(data, force_update, "get_ptax")

        if data is None:
            data = pd.Timestamp.today().normalize()

        print("Carregando PTAX via banco local...")
        ptax = ptax_from_db(data)

        self._ptax = ptax
        save_cache(ptax, "ptax.pkl")
        return ptax

    def get_vna_lft(self, data=None, force_update=False):
        if self._vna_lft is not None and not force_update:
            return self._vna_lft

        if not force_update:
            cache = load_cache("vna_lft.pkl")
            if cache is not None:
                self._vna_lft = cache
                return cache

        self._require_data(data, force_update, "get_vna_lft")

        if data is None:
            data = pd.Timestamp.today().normalize()

        print("Carregando VNA LFT via banco local...")
        vna_lft = fetch_with_fallback(
            "vna_lft",
            vna_lft_from_db,
            vna_lft_from_scraping,
            data=data,
        )

        self._vna_lft = vna_lft
        save_cache(vna_lft, "vna_lft.pkl")
        return vna_lft

    def get_anbimas(self, data=None, force_update=False):
        if self._anbimas and not force_update:
            return self._anbimas

        if not force_update:
            cache = load_cache("anbimas.pkl")
            if cache is not None:
                print("[OK] Usando cache existente de ANBIMAS completo.")
                self._anbimas = cache
                return cache

        self._require_data(data, force_update, "get_anbimas")

        data = _data_leitura_mercado_sessao(data)

        print("Carregando ANBIMAs via banco local...")
        anbimas_dict = fetch_with_fallback(
            "anbimas",
            anbimas_from_db,
            anbimas_from_scraping,
            data=data,
        )

        save_cache(anbimas_dict, "anbimas.pkl")
        print("[OK] Cache salvo para todos os títulos ANBIMA.")

        self._anbimas = anbimas_dict
        return anbimas_dict

    def get_bmf(self, data=None, force_update=False):
        if self._bmf and not force_update:
            return self._bmf

        if not force_update:
            cache = load_cache("bmf.pkl")
            if cache is not None:
                print("[OK] Usando cache existente de BMF completo.")
                self._bmf = cache
                return cache

        self._require_data(data, force_update, "get_bmf")

        data = _data_leitura_mercado_sessao(data)

        print("Carregando BMF via banco local...")
        df_bmf = fetch_with_fallback(
            "bmf",
            bmf_from_db,
            bmf_from_scraping,
            data=data,
        )

        save_cache(df_bmf, "bmf.pkl")
        print("[OK] Cache salvo para todos os contratos de DI e DAP.")

        self._bmf = df_bmf
        return df_bmf

    def atualizar_tudo(self, data, verbose=True):
        """
        Força a atualização de todas as variáveis de mercado para a data informada.

        ``data`` é usada literalmente em CDI, IPCA, PTAX e VNA. Em ANBIMA e BMF, se ``data``
        for o dia corrente, a leitura usa D-1 útil; caso contrário, usa a própria data.
        """
        data = pd.Timestamp(data).normalize()

        if verbose:
            print(f"Atualizando variáveis de mercado (data={data.date()})...")

        feriados = self.get_feriados(force_update=True)
        self.get_ipca_dict(data=data, feriados=feriados, force_update=True)
        self.get_cdi(data=data, force_update=True)
        self.get_ptax(data=data, force_update=True)
        self.get_anbimas(data=data, force_update=True)
        self.get_bmf(data=data, force_update=True)
        self.get_vna_lft(data=data, force_update=True)

        if verbose:
            print("[OK] Atualização concluída.")

    def limpar_cache(self):
        clear_cache("feriados.pkl")
        clear_cache("ipca_dict.pkl")
        clear_cache("cdi.pkl")
        clear_cache("anbimas.pkl")
        clear_cache("bmf.pkl")
        clear_cache("vna_lft.pkl")
        clear_cache("ptax.pkl")
        self._feriados = None
        self._ipca_dict = None
        self._cdi = None
        self._anbimas = None
        self._bmf = None
        self._vna_lft = None
        self._ptax = None
