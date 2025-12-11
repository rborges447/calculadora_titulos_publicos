"""
Funções para obter listas de vencimentos disponíveis para cada título.
"""
import pandas as pd
from typing import List, Dict
from datetime import datetime

from titulospub.dados.orquestrador import VariaveisMercado


def get_vencimentos_ltn() -> List[str]:
    """
    Retorna lista de vencimentos disponíveis para LTN.
    
    Returns:
        List[str]: Lista de datas de vencimento no formato YYYY-MM-DD
    """
    try:
        import sys
        import io
        # Redirecionar stdout temporariamente para evitar problemas de encoding
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        vm = VariaveisMercado()
        anbimas_dict = vm.get_anbimas()
        
        # Restaurar stdout
        sys.stdout = old_stdout
        
        if not anbimas_dict or "LTN" not in anbimas_dict:
            print(f"[WARN] LTN nao encontrado em anbimas_dict. Chaves disponiveis: {list(anbimas_dict.keys()) if anbimas_dict else 'vazio'}")
            return []
        
        df = anbimas_dict["LTN"]
        if df.empty or "VENCIMENTO" not in df.columns:
            print(f"[WARN] DataFrame LTN vazio ou sem coluna VENCIMENTO. Colunas: {list(df.columns) if not df.empty else 'vazio'}")
            return []
        
        vencimentos = df["VENCIMENTO"].unique()
        vencimentos = sorted([pd.Timestamp(v).strftime("%Y-%m-%d") for v in vencimentos if pd.notna(v)])
        print(f"[OK] Encontrados {len(vencimentos)} vencimentos LTN")
        return vencimentos
    except Exception as e:
        print(f"[ERRO] Erro ao buscar vencimentos LTN: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_vencimentos_lft() -> List[str]:
    """
    Retorna lista de vencimentos disponíveis para LFT.
    
    Returns:
        List[str]: Lista de datas de vencimento no formato YYYY-MM-DD
    """
    try:
        import sys
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        vm = VariaveisMercado()
        anbimas_dict = vm.get_anbimas()
        
        sys.stdout = old_stdout
        
        if not anbimas_dict or "LFT" not in anbimas_dict:
            print(f"[WARN] LFT nao encontrado em anbimas_dict. Chaves disponiveis: {list(anbimas_dict.keys()) if anbimas_dict else 'vazio'}")
            return []
        
        df = anbimas_dict["LFT"]
        if df.empty or "VENCIMENTO" not in df.columns:
            print(f"[WARN] DataFrame LFT vazio ou sem coluna VENCIMENTO. Colunas: {list(df.columns) if not df.empty else 'vazio'}")
            return []
        
        vencimentos = df["VENCIMENTO"].unique()
        vencimentos = sorted([pd.Timestamp(v).strftime("%Y-%m-%d") for v in vencimentos if pd.notna(v)])
        print(f"[OK] Encontrados {len(vencimentos)} vencimentos LFT")
        return vencimentos
    except Exception as e:
        print(f"[ERRO] Erro ao buscar vencimentos LFT: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_vencimentos_ntnb() -> List[str]:
    """
    Retorna lista de vencimentos disponíveis para NTNB.
    
    Returns:
        List[str]: Lista de datas de vencimento no formato YYYY-MM-DD
    """
    try:
        import sys
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        vm = VariaveisMercado()
        anbimas_dict = vm.get_anbimas()
        
        sys.stdout = old_stdout
        
        if not anbimas_dict or "NTN-B" not in anbimas_dict:
            print(f"[WARN] NTN-B nao encontrado em anbimas_dict. Chaves disponiveis: {list(anbimas_dict.keys()) if anbimas_dict else 'vazio'}")
            return []
        
        df = anbimas_dict["NTN-B"]
        if df.empty or "VENCIMENTO" not in df.columns:
            print(f"[WARN] DataFrame NTN-B vazio ou sem coluna VENCIMENTO. Colunas: {list(df.columns) if not df.empty else 'vazio'}")
            return []
        
        vencimentos = df["VENCIMENTO"].unique()
        vencimentos = sorted([pd.Timestamp(v).strftime("%Y-%m-%d") for v in vencimentos if pd.notna(v)])
        print(f"[OK] Encontrados {len(vencimentos)} vencimentos NTNB")
        return vencimentos
    except Exception as e:
        print(f"[ERRO] Erro ao buscar vencimentos NTNB: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_vencimentos_ntnf() -> List[str]:
    """
    Retorna lista de vencimentos disponíveis para NTNF.
    
    Returns:
        List[str]: Lista de datas de vencimento no formato YYYY-MM-DD
    """
    try:
        import sys
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        vm = VariaveisMercado()
        anbimas_dict = vm.get_anbimas()
        
        sys.stdout = old_stdout
        
        if not anbimas_dict or "NTN-F" not in anbimas_dict:
            print(f"[WARN] NTN-F nao encontrado em anbimas_dict. Chaves disponiveis: {list(anbimas_dict.keys()) if anbimas_dict else 'vazio'}")
            return []
        
        df = anbimas_dict["NTN-F"]
        if df.empty or "VENCIMENTO" not in df.columns:
            print(f"[WARN] DataFrame NTN-F vazio ou sem coluna VENCIMENTO. Colunas: {list(df.columns) if not df.empty else 'vazio'}")
            return []
        
        vencimentos = df["VENCIMENTO"].unique()
        vencimentos = sorted([pd.Timestamp(v).strftime("%Y-%m-%d") for v in vencimentos if pd.notna(v)])
        print(f"[OK] Encontrados {len(vencimentos)} vencimentos NTNF")
        return vencimentos
    except Exception as e:
        print(f"[ERRO] Erro ao buscar vencimentos NTNF: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_codigos_di_disponiveis() -> List[str]:
    """
    Retorna lista de códigos DI disponíveis (ex: DI1F32, DI1F33, etc).
    
    Returns:
        List[str]: Lista de códigos DI disponíveis
    """
    try:
        vm = VariaveisMercado()
        bmf_dict = vm.get_bmf()
        
        if "DI" not in bmf_dict:
            return []
        
        df = bmf_dict["DI"]
        codigos = df["DI"].unique().tolist()
        codigos = sorted([str(c) for c in codigos if pd.notna(c)])
        return codigos
    except Exception as e:
        print(f"Erro ao buscar códigos DI: {e}")
        return []


def get_todos_vencimentos() -> Dict[str, List[str]]:
    """
    Retorna todos os vencimentos disponíveis por título.
    
    Returns:
        Dict[str, List[str]]: Dicionário com vencimentos por título
    """
    return {
        "ltn": get_vencimentos_ltn(),
        "lft": get_vencimentos_lft(),
        "ntnb": get_vencimentos_ntnb(),
        "ntnf": get_vencimentos_ntnf(),
    }

