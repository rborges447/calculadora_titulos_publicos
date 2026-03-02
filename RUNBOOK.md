# Runbook - Execução em Rede Interna

Este documento descreve como executar a aplicação para acesso via rede interna.

## Estrutura do Projeto

- **API FastAPI**: `api/main.py` - Entrypoint: `api.main:app`
- **Dash App**: `dash_app/app.py` - Entrypoint: `dash_app.app:app` (com `server = app.server` para gunicorn)

## Pré-requisitos

1. Python 3.8+ instalado
2. Dependências instaladas: `pip install -r requirements.txt`
3. Firewall configurado para permitir conexões nas portas 8000 (API) e 8050 (Dash)

## Configuração para Rede Interna

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente antes de executar:

```bash
# Windows PowerShell
$env:API_BASE_URL="http://10.182.129.1:8000"
$env:DASH_HOST="0.0.0.0"
$env:DASH_PORT="8050"
$env:API_WORKERS="1"  # Número de workers para FastAPI (padrão: 1)

# Linux/Mac
export API_BASE_URL="http://10.182.129.1:8000"
export DASH_HOST="0.0.0.0"
export DASH_PORT="8050"
export API_WORKERS="1"
```

**Nota**: Se `API_BASE_URL` não for definida, o Dash usará `http://127.0.0.1:8000` por padrão.

## Executando os Serviços

### 1. Iniciar API FastAPI

```bash
# Opção 1: Usando o script run_api.py (recomendado)
python run_api.py

# Opção 2: Usando uvicorn diretamente
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
```

A API estará disponível em:
- **Local**: http://127.0.0.1:8000
- **Rede**: http://10.182.129.1:8000
- **Documentação**: http://10.182.129.1:8000/docs

### 2. Iniciar Dash App

**IMPORTANTE**: Configure `API_BASE_URL` antes de iniciar o Dash!

```bash
# Opção 1: Usando o script run_dash_app.py (recomendado)
python run_dash_app.py

# Opção 2: Usando gunicorn (produção)
gunicorn dash_app.app:server --bind 0.0.0.0:8050 --workers 2

# Opção 3: Usando o módulo diretamente (desenvolvimento)
python -m dash_app.app
```

O Dash estará disponível em:
- **Local**: http://127.0.0.1:8050
- **Rede**: http://10.182.129.1:8050

## Testando o Acesso

### Teste Local (no servidor)

```bash
# Testar API
curl http://127.0.0.1:8000/health

# Testar Dash (deve retornar HTML)
curl http://127.0.0.1:8050/
```

### Teste pela Rede (de outro computador)

```bash
# Testar API
curl http://10.182.129.1:8000/health

# Testar Dash (deve retornar HTML)
curl http://10.182.129.1:8050/
```

### Teste no Navegador

De outro computador na rede, abra:
- **API Docs**: http://10.182.129.1:8000/docs
- **Dash App**: http://10.182.129.1:8050/

## Configuração de Firewall (Windows)

Se o acesso não funcionar, pode ser necessário liberar as portas no firewall:

```powershell
# PowerShell como Administrador
New-NetFirewallRule -DisplayName "API FastAPI" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Dash App" -Direction Inbound -LocalPort 8050 -Protocol TCP -Action Allow
```

## Configuração de Firewall (Linux)

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw allow 8050/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=8050/tcp
sudo firewall-cmd --reload
```

## Execução em Background (Linux/Mac)

### Usando nohup

```bash
# API
nohup python run_api.py > api.log 2>&1 &

# Dash
nohup python run_dash_app.py > dash.log 2>&1 &
```

### Usando systemd (produção)

Crie arquivos de serviço em `/etc/systemd/system/`:

**`/etc/systemd/system/api-titulos.service`**:
```ini
[Unit]
Description=API Títulos Públicos
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/projeto
Environment="API_WORKERS=1"
ExecStart=/usr/bin/python3 run_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/dash-titulos.service`**:
```ini
[Unit]
Description=Dash Títulos Públicos
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/projeto
Environment="API_BASE_URL=http://10.182.129.1:8000"
Environment="DASH_HOST=0.0.0.0"
Environment="DASH_PORT=8050"
ExecStart=/usr/bin/python3 run_dash_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar serviços:
```bash
sudo systemctl enable api-titulos
sudo systemctl enable dash-titulos
sudo systemctl start api-titulos
sudo systemctl start dash-titulos
```

## Troubleshooting

### Dash não consegue conectar à API

1. Verifique se `API_BASE_URL` está configurada corretamente
2. Verifique se a API está rodando: `curl http://10.182.129.1:8000/health`
3. Verifique logs do navegador (F12) para ver erros de CORS ou conexão

### Erro de CORS

A API já está configurada com `allow_origins=["*"]`, então não deve haver problemas de CORS. Se houver, verifique:
- Se a API está realmente rodando em `0.0.0.0`
- Se o firewall não está bloqueando

### Múltiplos Usuários Simultâneos

**⚠️ AVISO**: O sistema atual usa estado em memória para carteiras. Com múltiplos usuários:
- Cada usuário terá suas próprias carteiras (isoladas)
- Carteiras não são compartilhadas entre usuários
- Para produção escalável, considere migrar carteiras para banco de dados ou Redis

## Comandos Rápidos (Sem Alterar Código)

Se preferir não alterar código, pode usar diretamente:

```bash
# API
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Dash (após configurar API_BASE_URL)
API_BASE_URL=http://10.182.129.1:8000 python run_dash_app.py
```

E editar manualmente `dash_app/config.py` para:
```python
API_URL = "http://10.182.129.1:8000"
```

## Verificação Final

Após iniciar ambos os serviços, de outro computador na rede:

1. ✅ Acesse http://10.182.129.1:8000/docs - deve mostrar Swagger UI
2. ✅ Acesse http://10.182.129.1:8050/ - deve carregar o Dash
3. ✅ No Dash, tente fazer um cálculo - deve funcionar sem erros de conexão

Se todos os passos funcionarem, a configuração está correta! 🎉







