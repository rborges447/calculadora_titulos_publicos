"""
Página inicial
"""
import streamlit as st


def render():
    """
    Renderiza a página inicial
    """
    st.title("📊 Calculadora de Títulos Públicos")
    st.markdown("---")
    st.markdown("""
    ## 🏠 Bem-vindo
    
    Esta aplicação permite calcular diferentes tipos de títulos públicos brasileiros.
    
    ### 📋 Tipos de Títulos Disponíveis:
    
    - **📈 LTN** - Letra do Tesouro Nacional
    - **📉 LFT** - Letra Financeira do Tesouro  
    - **📊 NTNB** - Nota do Tesouro Nacional - Série B
    - **📌 NTNF** - Nota do Tesouro Nacional - Série F
    
    Use o menu lateral para navegar entre as páginas.
    """)
