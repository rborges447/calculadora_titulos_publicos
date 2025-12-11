# Calculadora de Títulos Públicos

Sistema completo para cálculo e análise de títulos públicos brasileiros com API FastAPI e interface Streamlit.

## Estrutura do Projeto

```
calculadora_titulos_publicos/
├── api/                    # API FastAPI
│   ├── main.py            # Aplicação principal
│   ├── models.py          # Modelos Pydantic
│   └── routers/          # Endpoints por tipo de título
├── pages/                  # Páginas Streamlit
│   ├── 1_LTN.py
│   ├── 2_LFT.py
│   ├── 3_NTNB.py
│   └── 4_NTNF.py
├── titulospub/            # Módulo principal (pacote Python)
├── streamlit_app.py        # App Streamlit principal
├── run_api.py             # Script para iniciar API
└── requirements.txt       # Dependências
```

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar pacote titulospub em modo desenvolvimento
pip install -e .
```

## Como Usar

### 1. Iniciar a API

```bash
python run_api.py
```

A API estará disponível em: http://localhost:8000
- Documentação: http://localhost:8000/docs

### 2. Iniciar Interface Streamlit

```bash
streamlit run streamlit_app.py
```

A interface abrirá automaticamente no navegador.

## Endpoints da API

- `POST /titulos/ltn` - Criar título LTN
- `POST /titulos/lft` - Criar título LFT
- `POST /titulos/ntnb` - Criar título NTNB
- `POST /titulos/ntnb/hedge-di` - Calcular hedge DI para NTNB
- `POST /titulos/ntnf` - Criar título NTNF

## Uso do Pacote Python

```python
from titulospub import NTNB, LTN, LFT, NTNF, equivalencia

# Criar título
ltn = LTN("2025-01-01", taxa=12.5)
ltn.quantidade = 50000
print(f"Financeiro: R$ {ltn.financeiro:,.2f}")

# Calcular equivalência
eq = equivalencia("LTN", "2025-01-01", "NTNB", "2035-05-15", 
                  qtd1=10000, criterio="dv")
```

## Desenvolvido com

- FastAPI - Framework web moderno
- Streamlit - Interface web interativa
- Python 3.8+



