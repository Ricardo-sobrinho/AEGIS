# CHANGELOG

Todas as mudanças relevantes do projeto AEGIS serão documentadas neste arquivo.

O versionamento segue o conceito de evolução incremental da arquitetura do sistema, utilizando RFCs (Request for Comments) para registrar decisões técnicas importantes.

---

# Versionamento

- Status Atual: **v0.9.0**
- Arquitetura: Clean Architecture + SOLID + Event Driven Architecture
- Linguagem: Python 3.13
- Status: Em Desenvolvimento

---

# v0.9.0 — RFC-004 Bankroll Engine

Data: Julho/2026

## Objetivo

Implementar um módulo financeiro desacoplado responsável pelo gerenciamento da banca da AEGIS para operações de contratos de tempo fixo (Binary Options), mantendo todo o fluxo financeiro centralizado em um único agregado.

## Adicionado

### Bankroll

- BankrollEngine
- BankrollStatistics
- BankrollTransaction
- BankrollTransactionFactory

### Funcionalidades

- Controle de saldo disponível
- Controle de saldo reservado
- Ledger financeiro imutável
- Reserva de stake
- Liberação de stake
- Liquidação WIN
- Liquidação LOSS
- Liquidação DRAW
- Depósitos
- Saques
- Ajustes de crédito
- Ajustes de débito
- Controle por Contract ID
- Estatísticas da banca

### Garantias Arquiteturais

- Ledger imutável
- Operações atômicas
- Validação completa antes da alteração do estado
- Separação entre criação de transações e atualização financeira
- Apenas o BankrollEngine pode alterar os saldos
- Snapshot imutável das estatísticas

### Testes

Novos testes adicionados:

- test_transaction.py
- test_transaction_factory.py
- test_statistics.py
- test_bankroll.py

Resultado da suíte:

```
Ran 234 tests

OK
```

---

# v0.8.0 — Portfolio Engine

## Adicionado

- PortfolioEngine
- Controle de posições
- Preço médio
- Lucro realizado
- Lucro não realizado
- Patrimônio
- Compra
- Venda parcial
- Venda total
- Atualização de preços
- Controle por ativo

## Garantias

- Apenas PortfolioEngine altera posições
- PositionManager removido da arquitetura

---

# v0.7.0 — Execution Architecture

## Adicionado

- Execution Engine
- EventBus
- Eventos de execução
- Integração entre módulos

---

# v0.6.0 — Core Trading

## Adicionado

- Performance Engine
- Risk Manager
- Strategy Engine
- Paper Trading
- Indicadores
- Repositório de candles

---

# v0.5.0

## Adicionado

- Market Data
- Binance Client
- Candle Repository

---

# v0.4.0

## Adicionado

- Estrutura inicial da arquitetura
- Organização do projeto
- Primeiros testes

---

# Estatísticas atuais

## Arquitetura

- Clean Architecture
- SOLID
- Event Driven Architecture
- Domain Driven Design (parcial)

## Testes

```
234 testes
0 falhas
100% aprovados
```

## Componentes implementados

- Event Bus
- Market Data
- Candle Repository
- Indicator Engine
- Strategy Engine
- Risk Manager
- Portfolio Engine
- Performance Engine
- Paper Trading Engine
- Bankroll Engine

---

# Próxima versão

## RFC-005

Execution & Binary Options Integration

Objetivos:

- Integrar RiskManager ao BankrollEngine
- Reserva automática da stake
- Liquidação automática WIN/LOSS/DRAW
- Fluxo financeiro completo
- Integração com Broker Adapter
- Conta Demo
- Preparação para execução real

---

Fim do documento.