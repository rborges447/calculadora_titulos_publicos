import os

import pandas as pd

from titulospub.dados.anbimas import anbimas
from titulospub.dados.backup import (
    backup_anbimas,
    backup_bmf,
    backup_cdi,
    backup_feriados,
    backup_ipca_fechado,
    backup_ipca_proj,
)
from titulospub.dados.bmf import ajustes_bmf, ajustes_bmf_net
from titulospub.dados.cache import clear_cache, load_cache, save_cache
from titulospub.dados.ipca import dicionario_ipca
from titulospub.scraping import scrap_bmf_net
from titulospub.scraping.anbima_scraping import (
    scrap_anbimas,
    scrap_cdi,
    scrap_feriados,
    scrap_proj_ipca,
    scrap_vna_lft,
)
from titulospub.scraping.sidra_scraping import puxar_valores_ipca_fechado
from titulospub.utils.datas import adicionar_dias_uteis


class VariaveisMercado:
    def __init__(self):
        self._feriados = None
        self._ipca_dict = None
        self._cdi = None
        self._vna_lft = None
        self._anbimas = None
        self._bmf = None

    def get_feriados(self, force_update=False):

        if self._feriados is not None and not force_update:
            return self._feriados

        if not force_update:
            feriados = load_cache("feriados.pkl")
            if feriados:
                self._feriados = feriados
                return feriados

        try:
            print("Buscando feriados via scraping...")
            feriados = scrap_feriados()
        except Exception as e:
            print(f"[AVISO] Falha no scraping de feriados: {e}")
            feriados = backup_feriados()
            print("Feriados pego via backup")
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
        
        if feriados is None:
            feriados = self.get_feriados()

        if data is None:
            data = pd.Timestamp.today().normalize()

        try:
            print("Calculando IPCA dict...")
            ipca_fechado_df = puxar_valores_ipca_fechado()
            ipca_proj_float = scrap_proj_ipca()
            ipca_dict = dicionario_ipca(data=data,
                                        ipca_fechado_df=ipca_fechado_df, 
                                        ipca_proj_float=ipca_proj_float, 
                                        feriados=feriados)
        except Exception as e:
            print(f"[AVISO] Falha ao calcular IPCA: {e}")
            #fallback via CSV 
            ipca_fechado_df = backup_ipca_fechado()               
            ipca_proj_float =  backup_ipca_proj()
            ipca_dict = dicionario_ipca(data=data,
                                        ipca_fechado_df=ipca_fechado_df, 
                                        ipca_proj_float=ipca_proj_float, 
                                        feriados=feriados)
            print("ipca_proj_float e ipca_fechado_df pegos via backup")

        self._ipca_dict = ipca_dict
        save_cache(ipca_dict, "ipca_dict.pkl")
        return ipca_dict
    
    def get_cdi(self, force_update=False):
        if self._cdi is not None and not force_update:
            return self._cdi
        
        if not force_update:
            cdi = load_cache("cdi.pkl")
            if cdi is not None:
                self._cdi = cdi
                return cdi

        try:
            print("Buscando CDI...")
            cdi = scrap_cdi()
        except Exception as e:
            print(f"[AVISO] Falha ao buscar CDI: {e}")
            print("Tentando carregar backup local...")
            cdi = backup_cdi()
            print("cdi pego via backup")
            if cdi is None:
                raise RuntimeError("[ERRO] Falha no scraping e no backup do CDI") from e

        self._cdi = cdi
        save_cache(cdi, "cdi.pkl")
        return cdi
    
    def get_vna_lft(self, data=None, force_update=False):
        if self._vna_lft is not None and not force_update:
            return self._vna_lft

        if data is None:
           data=pd.Timestamp.today().normalize()

        if not force_update:
            cache = load_cache("vna_lft.pkl")
            if cache is not None:
                print("[OK] Usando cache existente de VNA_LFT completo.")
                self._vna_lft = cache
                return cache

        try:
            print("Realizando scraping VNA_LFT...")
            vna_lft = scrap_vna_lft(data=data)
            save_cache(vna_lft, "vna_lft.pkl")
            print("[OK] Cache salvo para VNA_LFT.")
            self._vna_lft = vna_lft
            return vna_lft
        except Exception as e:
            print(f"[ERRO] Erro ao fazer scraping/parsing VNA_LFT: {e}")
            # Por enquanto, vamos re-raise a exceção para que o erro seja visível
            # TODO: Implementar backup para VNA_LFT
            raise RuntimeError(f"Falha ao obter VNA_LFT: {e}") from e

        
    def get_anbimas(self, data=None, force_update=False):
        if self._anbimas and not force_update:
            return self._anbimas

        if data is None:
            data = adicionar_dias_uteis(data=pd.Timestamp.today().normalize(),
                                        n_dias=-1)

        if not force_update:
            cache = load_cache("anbimas.pkl")
            if cache is not None:
                print("[OK] Usando cache existente de ANBIMAS completo.")
                self._anbimas = cache
                return cache

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

        if data is None:
            data = adicionar_dias_uteis(data=pd.Timestamp.today().normalize(),
                                        n_dias=-1)

        if not force_update:
            cache = load_cache("bmf.pkl")
            if cache is not None:
                print("[OK] Usando cache existente de BMF completo.")
                self._bmf = cache
                return cache
        
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

    def atualizar_tudo(self, verbose=True):
        """
        Força a atualização de todas as variáveis de mercado.
        Faz fallback automático em caso de erro.
        """
        if verbose:
            print("Atualizando variáveis de mercado...")

        self.get_feriados(force_update=True)
        self.get_ipca_dict(force_update=True)
        self.get_cdi(force_update=True)
        self.get_anbimas(force_update=True)
        self.get_bmf(force_update=True)
        self.get_vna_lft(force_update=True)
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