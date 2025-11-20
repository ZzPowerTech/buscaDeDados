# 🔄 Changelog - Atualizações do Projeto

## [2.0.0] - 2025-11-20

### ⭐ NOVA FUNCIONALIDADE PRINCIPAL

**Salvamento Automático Multi-Destino** no `collect_news_bbas3.py`

O script agora salva automaticamente os dados coletados em **4 destinos** simultaneamente:

1. 📄 **JSON local** (`collected_articles_bbas3.json`)
2. 🗄️ **MongoDB** (`bigData.projeto_ativos`)
3. 🐘 **PostgreSQL** (`bigdata.dados_mong`)
4. ❄️ **Snowflake** (`BBAS3.PUBLIC.DADOS_MONG`)

### ✨ Mudanças

#### `collect_news_bbas3.py`

- ✅ Adicionado suporte a PostgreSQL
- ✅ Adicionado suporte a Snowflake
- ✅ Nova função `save_to_postgres()` - salva dados no PostgreSQL
- ✅ Nova função `save_to_snowflake()` - salva dados no Snowflake
- ✅ Dados de sentimento expandidos automaticamente em colunas
- ✅ Configuração via variáveis de ambiente
- ✅ Logs mais detalhados com resumo final

#### Dependências Adicionadas

```
pandas
sqlalchemy
psycopg2-binary
snowflake-connector-python
snowflake-sqlalchemy
```

#### Novos Arquivos

- `config_example.ps1` - Template de configuração de variáveis
- `CHANGELOG.md` - Este arquivo

### 🔧 Configuração Necessária

Antes de executar, configure as variáveis de ambiente:

```powershell
# Copiar arquivo de exemplo
Copy-Item config_example.ps1 config_local.ps1

# Editar config_local.ps1 com suas credenciais
notepad config_local.ps1

# Carregar configurações
. .\config_local.ps1

# Executar coleta
python collect_news_bbas3.py
```

### 📊 Fluxo de Dados Atualizado

```
Google News RSS
      │
      ▼
[collect_news_bbas3.py]
      │
      ├─→ 📄 JSON local
      ├─→ 🗄️ MongoDB
      ├─→ 🐘 PostgreSQL
      └─→ ❄️ Snowflake
```

### 🚀 Uso Simplificado

**Antes** (múltiplos scripts):

```powershell
python collect_news_bbas3.py  # Salva MongoDB + JSON
python migrar.py              # Migra para Snowflake
```

**Agora** (1 comando):

```powershell
python collect_news_bbas3.py  # Salva TUDO automaticamente
```

### ⚡ Performance

- Tempo de execução: +2-5 minutos (devido ao salvamento adicional)
- Ganho de eficiência: Elimina necessidade de migração separada
- Dados imediatamente disponíveis em todos os destinos

### 🔒 Segurança

- Credenciais via variáveis de ambiente
- Arquivo `config_local.ps1` não commitado (adicionar ao .gitignore)
- Valores padrão para desenvolvimento local

### 📝 Notas

- O salvamento no Snowflake substitui a tabela inteira (`overwrite=True`)
- MongoDB continua usando `upsert` para evitar duplicatas
- PostgreSQL substitui a tabela (`if_exists='replace'`)
- Estrutura de dados expandida automaticamente (coluna `sentimentos` → múltiplas colunas)

### 🐛 Correções

- Melhor tratamento de erros em cada destino
- Logs independentes para cada operação de salvamento
- Continua execução mesmo se um destino falhar

### 🔜 Próximas Versões

- [ ] Opção para escolher destinos via parâmetro CLI
- [ ] Salvamento incremental no PostgreSQL/Snowflake
- [ ] Backup automático antes de sobrescrever
- [ ] Compressão de dados para Snowflake
- [ ] Retry automático em caso de falha
