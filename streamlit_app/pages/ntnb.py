"""
Página NTNB - Nota do Tesouro Nacional - Série B
"""
import streamlit as st
import requests
from datetime import date
from streamlit_app.utils.api import get_api_url


def render():
    """
    Renderiza a página de cálculo NTNB
    """
    st.title("📊 NTNB - Nota do Tesouro Nacional - Série B")
    st.markdown("---")
    
    API_URL = get_api_url()
    
    tab1, tab2 = st.tabs(["📊 Calcular NTNB", "🎯 Calcular Hedge DI"])
    
    with tab1:
        _render_calcular_ntnb(API_URL)
    
    with tab2:
        _render_hedge_di(API_URL)


def _render_calcular_ntnb(api_url: str):
    """
    Renderiza o formulário de cálculo NTNB
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data_vencimento = st.date_input("Data de Vencimento", value=date(2025, 1, 1), key="ntnb_venc")
    
    with col2:
        taxa = st.number_input("Taxa (%)", min_value=0.0, value=7.5, step=0.01, format="%.2f", key="ntnb_taxa")
    
    with col3:
        dias_liquidacao = st.number_input("Dias para Liquidação", min_value=0, value=1, key="ntnb_liq")
    
    col4, col5 = st.columns(2)
    
    with col4:
        quantidade = st.number_input("Quantidade", min_value=0.0, value=0.0, step=1.0, key="ntnb_qtd")
    
    with col5:
        financeiro = st.number_input("Valor Financeiro (R$)", min_value=0.0, value=0.0, step=1000.0, key="ntnb_fin")
    
    if st.button("Calcular", type="primary", key="ntnb_btn"):
        data_request = {
            "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
            "dias_liquidacao": int(dias_liquidacao),
        }
        
        if taxa > 0:
            data_request["taxa"] = float(taxa)
        
        if financeiro > 0:
            data_request["financeiro"] = float(financeiro)
        elif quantidade > 0:
            data_request["quantidade"] = float(quantidade)
        else:
            st.warning("⚠️ Informe quantidade ou valor financeiro")
            st.stop()
        
        try:
            with st.spinner("🔄 Calculando..."):
                response = requests.post(f"{api_url}/titulos/ntnb", json=data_request, timeout=30)
            
            if response.status_code == 200:
                resultado = response.json()
                st.success("✅ Cálculo realizado com sucesso!")
                st.markdown("---")
                
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                with col_res1:
                    st.metric("Quantidade", f"{resultado.get('quantidade', 0):,.0f}")
                with col_res2:
                    st.metric("Financeiro", f"R$ {resultado.get('financeiro', 0):,.2f}")
                with col_res3:
                    st.metric("Taxa", f"{resultado.get('taxa', 0):.2f}%")
                with col_res4:
                    st.metric("PU D0", f"{resultado.get('pu_d0', 0):.6f}")
                
                if resultado.get('dv01'):
                    st.metric("DV01", f"{resultado['dv01']:.2f}")
                
                with st.expander("📋 Detalhes Completos"):
                    st.json(resultado)
            else:
                st.error(f"❌ Erro na API: {response.status_code}")
                st.json(response.json() if response.text else {})
        except requests.exceptions.ConnectionError:
            st.error("❌ Não foi possível conectar à API. Verifique se está rodando.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")


def _render_hedge_di(api_url: str):
    """
    Renderiza o formulário de cálculo de hedge DI
    """
    st.subheader("🎯 Calcular Hedge DI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_vencimento_hedge = st.date_input("Data de Vencimento NTNB", value=date(2025, 1, 1), key="hedge_venc")
        codigo_di = st.text_input("Código DI (ex: DI1F32)", value="DI1F32", key="hedge_di")
        taxa_hedge = st.number_input("Taxa (%)", min_value=0.0, value=7.5, step=0.01, format="%.2f", key="hedge_taxa")
        dias_liq_hedge = st.number_input("Dias para Liquidação", min_value=0, value=1, key="hedge_liq")
    
    with col2:
        quantidade_hedge = st.number_input("Quantidade NTNB", min_value=0.0, value=0.0, step=1.0, key="hedge_qtd")
        financeiro_hedge = st.number_input("Valor Financeiro (R$)", min_value=0.0, value=0.0, step=1000.0, key="hedge_fin")
    
    if st.button("Calcular Hedge DI", type="primary", key="hedge_btn"):
        data_request = {
            "data_vencimento": data_vencimento_hedge.strftime("%Y-%m-%d"),
            "codigo_di": codigo_di,
            "dias_liquidacao": int(dias_liq_hedge),
        }
        
        if taxa_hedge > 0:
            data_request["taxa"] = float(taxa_hedge)
        
        if financeiro_hedge > 0:
            data_request["financeiro"] = float(financeiro_hedge)
        elif quantidade_hedge > 0:
            data_request["quantidade"] = float(quantidade_hedge)
        else:
            st.warning("⚠️ Informe quantidade ou valor financeiro")
            st.stop()
        
        try:
            with st.spinner("🔄 Calculando hedge DI..."):
                response = requests.post(f"{api_url}/titulos/ntnb/hedge-di", json=data_request, timeout=30)
            
            if response.status_code == 200:
                resultado = response.json()
                st.success("✅ Hedge DI calculado com sucesso!")
                st.markdown("---")
                
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric("Quantidade NTNB", f"{resultado.get('quantidade', 0):,.0f}")
                with col_res2:
                    st.metric("DV01 NTNB", f"{resultado.get('dv01_ntnb', 0):.2f}")
                with col_res3:
                    st.metric("Hedge DI", f"{resultado.get('hedge_di', 0):,} contratos")
                
                st.metric("Ajuste DI", f"{resultado.get('ajuste_di', 0):.2f}%")
                
                with st.expander("📋 Detalhes Completos"):
                    st.json(resultado)
            else:
                st.error(f"❌ Erro na API: {response.status_code}")
                st.json(response.json() if response.text else {})
        except requests.exceptions.ConnectionError:
            st.error("❌ Não foi possível conectar à API. Verifique se está rodando.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
