# Changelog

Todas as alterações relevantes da plataforma **AEGIS (Adaptive Evolutionary Global Intelligence System)** são registradas neste documento.

---

# [0.7.0] - 2026-07-18

## 🎉 Marco da Versão

Implementação da **Execution Architecture**, estabelecendo a separação definitiva entre Estratégia, Risco, Execução, Carteira e Performance.

---

## ✨ Adicionado

### Nova camada de execução

- Criação do módulo `execution`
- Implementação do `ExecutionEngine`
- Novo fluxo de execução baseado em eventos

### Novos eventos

- `TRADE_REQUESTED`
- `TRADE_EXECUTED`
- `TRADE_REJECTED`

### Portfolio Engine

- Controle de saldo
- Controle de posições
- Atualização automática da carteira
- Validação final das operações

### Performance Engine

- Equity
- PnL
- ROI
- Valor da carteira

### Testes

- Testes automatizados da arquitetura de execução
- Validação do fluxo de compra
- Validação de rejeições
- Validação de encerramento de posição

---

## 🔄 Alterado

- RiskManager
- StrategyEngine
- Application
- Fluxo principal da aplicação

---

## 🐛 Corrigido

- Ordem das mensagens no terminal
- Operações duplicadas
- Validações de saldo
- Controle de posição aberta

---

## ✅ Testes

```text
Ran 4 tests

OK
```

---

# Histórico

| Versão | Descrição |
|---------|-----------|
| 0.1 | Estrutura inicial |
| 0.2 | Banco SQLite |
| 0.3 | Integração Binance |
| 0.4 | Estratégias |
| 0.5 | EventBus |
| 0.6 | Risk Manager |
| **0.7** | **Execution Architecture** |