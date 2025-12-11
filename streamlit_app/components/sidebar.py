"""
Componente de sidebar
"""
import streamlit as st
from streamlit_app.config import PAGES
from streamlit_app.utils.api import get_api_url, set_api_url


def render_sidebar():
    """
    Renderiza a sidebar com navegação e configurações
    """
    st.sidebar.title("📊 Navegação")
    
    # Inicializar página atual se não existir
    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "Home"
    
    # Seleção de página usando radio
    pagina_selecionada = st.sidebar.radio(
        "Selecione o título:",
        PAGES,
        index=PAGES.index(st.session_state.pagina_atual) if st.session_state.pagina_atual in PAGES else 0,
        key="pagina_selecionada"
    )
    
    # Atualizar session_state se mudou
    if pagina_selecionada != st.session_state.pagina_atual:
        st.session_state.pagina_atual = pagina_selecionada
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # URL da API
    api_url = st.sidebar.text_input(
        "URL da API",
        value=get_api_url(),
        key="api_url_input"
    )
    
    # Atualizar session_state se mudou
    if api_url != get_api_url():
        set_api_url(api_url)
    
    return st.session_state.pagina_atual
