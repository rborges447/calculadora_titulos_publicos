import os

import pandas as pd

from titulospub.dados.transforms import (
    anbimas,
    ajustes_bmf,
    ajustes_bmf_net,
)
from titulospub.dados.transforms.cdi import cdi_from_db
from titulospub.dados.transforms.feriados import feriados_from_db
from titulospub.dados.transforms.ipca import ipca_dict_from_db
from titulospub.dados.transforms.vna_lft import vna_lft_from_db
from titulospub.dados.transforms.backup import (
    backup_anbimas,
    backup_bmf,
)
from titulospub.dados.cache import clear_cache, load_cache, save_cache
from titulospub.scraping import scrap_bmf_net
from titulospub.scraping.anbima_scraping import scrap_anbimas
from titulospub.utils.datas import adicionar_dias_uteis


class VariaveisMercado:
    def __init__(self):
        self._feriados = None
        self._ipca_dict = None
        self._cdi = None
        self._vna_lft = None
        self._anbimas = None
        self._bmf = None

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
        feriados = feriados_from_db()
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
        cdi = cdi_from_db(data)

        self._cdi = cdi
        save_cache(cdi, "cdi.pkl")
        return cdi
    
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
        vna_lft = vna_lft_from_db(data)

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

        if data is None:
            data = adicionar_dias_uteis(
                data=pd.Timestamp.today().normalize(),
                n_dias=-1,
            )

        try:
            print("Realizando scraping ANBIMA...")
            df_anbima = scrap_anbimas(data=data)
            anbimas_dict = anbimas(df_anbima)
        except Exception as e:
            print(f"[ERRO] Erro ao fazer scraping/parsing ANBIMA: {e}")
            # Aqui pode colocar fallback via backup_anbimas()
            anbimas_dict = backup_anbimas()
            #self._anbimas = {}
            #return {}

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

        if data is None:
            data = adicionar_dias_uteis(
                data=pd.Timestamp.today().normalize(),
                n_dias=-1,
            )

        try:
            print("Realizando scraping BMF...")
            df_bmf = ajustes_bmf(data=data)
        except Exception as e:
            try:
                bmf_dict = scrap_bmf_net()
                df_bmf = ajustes_bmf_net(bmf_dict=bmf_dict, data=data)
                print(f"[ERRO] Erro ao fazer scraping/parsing BMF, buscando da net: {e}")
            except:
                print(f"[ERRO] Erro ao fazer scraping/parsing BMF, biscando do excel backup: {e}")
                # Aqui pode colocar fallback via backup_anbimas()
                df_bmf = backup_bmf()
            

        save_cache(df_bmf, "bmf.pkl")
        print("[OK] Cache salvo para todos os contrados de DI e DAP.")

        self._bmf = df_bmf
        return df_bmf

    def atualizar_tudo(self, data, verbose=True):
        """
        Força a atualização de todas as variáveis de mercado para a data informada.
        Faz fallback automático em caso de erro.
        """
        data = pd.Timestamp(data).normalize()

        if verbose:
            print(f"Atualizando variáveis de mercado (data={data.date()})...")

        feriados = self.get_feriados(force_update=True)
        self.get_ipca_dict(data=data, feriados=feriados, force_update=True)
        self.get_cdi(data=data, force_update=True)
        self.get_anbimas(data=data, force_update=True)
        self.get_bmf(data=data, force_update=True)
        self.get_vna_lft(data=data, force_update=True)
        # Futuro:
        # self.get_curvas(force_update=True)

        if verbose:
            print("[OK] Atualização concluída.")

    def limpar_cache(self):
        clear_cache("feriados.pkl")
        clear_cache("ipca_dict.pkl")
        clear_cache("cdi.pkl")
        clear_cache("anbimas.pkl")
        clear_cache("vna_lft.pkl")
        # clear_cache("curva_ltn.pkl")
        # ...
        self._feriados = None
        self._ipca_dict = None
        self._cdi = None
        self._anbimas = None
        self._vna_lft = None
if __name__ == "__main__":
    print("Testando orquestrador de variáveis de mercado...")
    
    try:
        vm = VariaveisMercado()
        
        print("Testando get_feriados()...")
        feriados = vm.get_feriados()
        print(f"[OK] Feriados: {len(feriados)} registros")
        
        print("Testando get_ipca_dict()...")
        ipca_dict = vm.get_ipca_dict()
        print(f"[OK] IPCA dict: {type(ipca_dict)}")
        
        print("Testando get_cdi()...")
        cdi = vm.get_cdi()
        print(f"[OK] CDI: {cdi}")
        
        print("Testando get_anbimas()...")
        anbimas = vm.get_anbimas()
        print(f"[OK] ANBIMAS: {len(anbimas)} tipos de títulos")
        for titulo, df in anbimas.items():
            print(f"  - {titulo}: {len(df)} registros")
        
        print("Testando get_bmf()...")
        bmf = vm.get_bmf()
        print(f"[OK] BMF: {len(bmf)} tipos de contratos")
        for tipo, df in bmf.items():
            print(f"  - {tipo}: {len(df)} registros")
        
        print("[OK] Orquestrador funcionando corretamente!")
        
    except Exception as e:
        print(f"[ERRO] Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        # Futuro:
        # self._curvas = {}