# 🚀 Guia Rápido de Execução

## Setup Inicial (apenas uma vez)

```powershell
.\setup_env.ps1
```

Isso cria o ambiente virtual, instala todas as dependências e baixa o corpus NLTK.

---

## Uso Diário

### Opção 1: Pipeline Completo (Recomendado) ⭐

```powershell
.\pipeline_completo.ps1
```

**O que faz:**

- ✅ Testa conexão MongoDB
- 📰 Coleta todas as notícias (~859 artigos)
- 🗄️ Salva no MongoDB e JSON
- 📊 Gera análise estatística
- 📈 Gera análise detalhada por tema

**Tempo:** 15-30 minutos
**Quando usar:** Para atualizar os dados com notícias novas

---

### Opção 2: Análise Rápida

```powershell
.\analise_rapida.ps1
```

**O que faz:**

- 📊 Análise estatística dos dados existentes
- 📈 Análise detalhada por tema
- 🗄️ Verificação MongoDB

**Tempo:** 1-2 minutos
**Quando usar:** Para reprocessar análises sem recoletar

---

## Scripts Individuais

```powershell
# Apenas coletar
python collect_news_bbas3.py

# Apenas verificar MongoDB
python verify_mongo_data.py

# Apenas análise estatística
python sentimentos.py

# Apenas análise detalhada
python analise_detalhada.py
```

---

## Arquivos Gerados

- `collected_articles_bbas3.json` - Todos os artigos coletados
- MongoDB: `bigData.projeto_ativos` - Mesmo conteúdo no banco

---

## Troubleshooting

### Erro: MongoDB não conecta

```powershell
# Verificar se MongoDB está rodando
python testConnection.py
```

### Erro: venv não encontrado

```powershell
# Criar ambiente virtual novamente
.\setup_env.ps1
```

### Erro: Módulo não encontrado

```powershell
# Reinstalar dependências
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Estrutura do Projeto

```
buscaDeDados/
├── setup_env.ps1              # Setup inicial
├── pipeline_completo.ps1      # Pipeline automático ⭐
├── analise_rapida.ps1         # Análises rápidas
├── run.ps1                    # Runner simples
├── collect_news_bbas3.py      # Coletor principal
├── sentimentos.py             # Análise estatística
├── analise_detalhada.py       # Análise por tema
├── verify_mongo_data.py       # Verificação MongoDB
├── testConnection.py          # Teste de conexão
├── requirements.txt           # Dependências Python
└── collected_articles_bbas3.json  # Dados coletados
```
