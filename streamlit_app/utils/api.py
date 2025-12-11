"""
Utilitários para interação com a API
"""
import streamlit as st


def get_api_url() -> str:
    """
    Obtém a URL da API do session_state
    
    Returns:
        str: URL da API
    """
    if "api_url" not in st.session_state:
        st.session_state.api_url = "http://localhost:8000"
    return st.session_state.api_url


def set_api_url(url: str):
    """
    Define a URL da API no session_state
    
    Args:
        url: URL da API
    """
    st.session_state.api_url = url
