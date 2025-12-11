"""
Aplicação Streamlit Principal - Calculadora de Títulos Públicos
"""
import streamlit as st
import traceback

# Configuração da página DEVE ser a primeira coisa
from streamlit_app.config import PAGE_CONFIG, PAGES
st.set_page_config(**PAGE_CONFIG)

# Importar componentes e páginas
try:
    from streamlit_app.components.sidebar import render_sidebar
    from streamlit_app.pages import home, ltn, lft, ntnb, ntnf
except Exception as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Renderizar sidebar e obter página selecionada
try:
    pagina = render_sidebar()
except Exception as e:
    st.sidebar.error(f"Erro na sidebar: {e}")
    st.sidebar.code(traceback.format_exc())
    pagina = "Home"

# Renderizar conteúdo baseado na página selecionada
try:
    if pagina == "Home":
        home.render()
    elif pagina == "LTN":
        ltn.render()
    elif pagina == "LFT":
        lft.render()
    elif pagina == "NTNB":
        ntnb.render()
    elif pagina == "NTNF":
        ntnf.render()
    else:
        st.error(f"Página '{pagina}' não encontrada")
        st.write(f"Páginas disponíveis: {PAGES}")
        home.render()
except Exception as e:
    st.error(f"Erro ao renderizar página '{pagina}': {e}")
    st.code(traceback.format_exc())
    import sys
    st.write(f"Tipo de erro: {type(e).__name__}")
