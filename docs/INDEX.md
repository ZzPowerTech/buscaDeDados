# 📚 Índice de Documentação

Bem-vindo à documentação do **BBAS3 News Collector & Sentiment Analysis**!

## 🚀 Começando

1. **[../README.md](../README.md)** - Comece aqui! Visão geral e quick start
2. **[ESTRUTURA.md](ESTRUTURA.md)** - Estrutura de diretórios do projeto

## 🏗️ Arquitetura

3. **[ARQUITETURA.md](ARQUITETURA.md)** - Arquitetura SOLID/Clean Code detalhada
   - Princípios SOLID aplicados
   - Camadas do sistema (Services, Models, Repositories)
   - Fluxo de dados
   - Transformações (nested → flat)

4. **[ARQUITETURA_DW.md](ARQUITETURA_DW.md)** - Data Warehouse
   - Star schema
   - Dimensões e fatos
   - Transformações ETL

## 📝 Histórico

5. **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças e versões

## 🔗 Links Rápidos

### Para Desenvolvedores
- [Configuração (.env)](../README.md#-configuração-env)
- [Estrutura de Código](ARQUITETURA.md#-estrutura-de-código)
- [Repository Pattern](ARQUITETURA.md#-repositórios-data-access-layer)
- [Modelos de Dados](ARQUITETURA.md#-estrutura-de-dados)

### Para Analistas
- [Análises SQL](../README.md#-análises-sql)
- [Feature Engineering](ESTRUTURA.md#-fluxo-de-dados)
- [Star Schema](ARQUITETURA_DW.md)

### Para Operação
- [Scripts Úteis](../README.md#-scripts-úteis)
- [Pipeline Completo](ESTRUTURA.md#-como-usar)
- [Testes](../README.md#-testes)

## 📂 Organização

```
docs/
├── INDEX.md               # Este arquivo (índice)
├── ESTRUTURA.md           # Estrutura de diretórios
├── ARQUITETURA.md         # Arquitetura SOLID
├── ARQUITETURA_DW.md      # Data Warehouse
└── CHANGELOG.md           # Histórico de mudanças
```

## 🆘 Precisa de Ajuda?

- **Erro ao executar?** → Ver [README.md - Testes](../README.md#-testes)
- **Configuração?** → Ver [.env.example](../.env.example)
- **Entender código?** → Ver [ARQUITETURA.md](ARQUITETURA.md)
- **Análise de dados?** → Ver [ARQUITETURA_DW.md](ARQUITETURA_DW.md)

## 🎯 Próximos Passos

Depois de ler a documentação:

1. Configure o `.env`
2. Execute `python collect_news_bbas3.py`
3. Analise os dados com `python sentimentos.py`
4. Explore queries SQL na documentação

---

**Versão**: 2.0.0  
**Última atualização**: Janeiro 2025
