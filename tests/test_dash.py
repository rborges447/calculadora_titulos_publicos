"""
Smoke tests para aplicação Dash.

Estes testes verificam que o Dash pode ser inicializado
e que as rotas principais funcionam.
"""
import pytest


class TestDashApp:
    """Testes básicos para aplicação Dash"""
    
    def test_dash_import(self):
        """Testa que Dash pode ser importado"""
        from dash_app.app import app
        assert app is not None
    
    def test_dash_config(self):
        """Testa que configuração do Dash está correta"""
        from dash_app import config
        assert hasattr(config, 'API_URL')
        assert hasattr(config, 'APP_TITLE')
        assert config.API_URL is not None
    
    def test_dash_pages_import(self):
        """Testa que páginas do Dash podem ser importadas"""
        from dash_app.pages import home, ltn, lft, ntnb, ntnf
        assert home is not None
        assert ltn is not None
        assert lft is not None
        assert ntnb is not None
        assert ntnf is not None
    
    def test_dash_pages_have_layout(self):
        """Testa que páginas têm função layout()"""
        from dash_app.pages import home, ltn, lft, ntnb, ntnf
        
        assert hasattr(home, 'layout')
        assert callable(home.layout)
        
        assert hasattr(ltn, 'layout')
        assert callable(ltn.layout)
        
        assert hasattr(lft, 'layout')
        assert callable(lft.layout)
        
        assert hasattr(ntnb, 'layout')
        assert callable(ntnb.layout)
        
        assert hasattr(ntnf, 'layout')
        assert callable(ntnf.layout)
    
    def test_dash_utils_import(self):
        """Testa que utilitários do Dash podem ser importados"""
        from dash_app.utils import api, carteiras, vencimentos, formatacao
        assert api is not None
        assert carteiras is not None
        assert vencimentos is not None
        assert formatacao is not None
    
    def test_dash_no_titulospub_import(self):
        """Testa que Dash não importa titulospub diretamente"""
        import dash_app.pages.ltn as ltn_module
        import dash_app.utils.api as api_module
        
        # Verificar que não há imports diretos de titulospub
        import inspect
        
        ltn_source = inspect.getsource(ltn_module)
        api_source = inspect.getsource(api_module)
        
        # Não deve haver "from titulospub" ou "import titulospub"
        assert "from titulospub" not in ltn_source
        assert "import titulospub" not in ltn_source
        assert "from titulospub" not in api_source
        assert "import titulospub" not in api_source
