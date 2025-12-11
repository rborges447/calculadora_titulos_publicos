"""
Página NTNF - Nota do Tesouro Nacional - Série F
"""
import streamlit as st
import requests
from datetime import date
from streamlit_app.utils.api import get_api_url


def render():
    """
    Renderiza a página de cálculo NTNF
    """
    st.title("📌 NTNF - Nota do Tesouro Nacional - Série F")
    st.markdown("---")
    
    API_URL = get_api_url()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data_vencimento = st.date_input("Data de Vencimento", value=date(2025, 1, 1), key="ntnf_venc")
    
    with col2:
        taxa = st.number_input("Taxa (%)", min_value=0.0, value=12.5, step=0.01, format="%.2f", key="ntnf_taxa")
    
    with col3:
        dias_liquidacao = st.number_input("Dias para Liquidação", min_value=0, value=1, key="ntnf_liq")
    
    col4, col5 = st.columns(2)
    
    with col4:
        quantidade = st.number_input("Quantidade", min_value=0.0, value=0.0, step=1.0, key="ntnf_qtd")
    
    with col5:
        financeiro = st.number_input("Valor Financeiro (R$)", min_value=0.0, value=0.0, step=1000.0, key="ntnf_fin")
    
    if st.button("Calcular", type="primary", key="ntnf_btn"):
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
                response = requests.post(f"{API_URL}/titulos/ntnf", json=data_request, timeout=30)
            
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
                
                with st.expander("📋 Detalhes Completos"):
                    st.json(resultado)
            else:
                st.error(f"❌ Erro na API: {response.status_code}")
                st.json(response.json() if response.text else {})
        except requests.exceptions.ConnectionError:
            st.error("❌ Não foi possível conectar à API. Verifique se está rodando.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
