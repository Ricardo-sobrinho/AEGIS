# AEGIS — PROJECT CHECKPOINT

> Documento oficial de acompanhamento do desenvolvimento da plataforma AEGIS.

---

# Informações Gerais

| Campo | Valor |
|--------|-------|
| Projeto | AEGIS |
| Nome Completo | Adaptive Evolutionary Global Intelligence System |
| Versão | v0.7.0 |
| Status | Em Desenvolvimento |
| Linguagem | Python |
| Arquitetura | Event Driven Architecture |
| Última Atualização | 18/07/2026 |

---

# Visão Geral

A AEGIS é uma plataforma de trading algorítmico construída utilizando arquitetura orientada a eventos (Event Driven Architecture).

O objetivo do projeto é evoluir gradualmente até se tornar uma plataforma completa capaz de operar automaticamente em diferentes corretoras, executar estratégias quantitativas, gerenciar risco, controlar patrimônio e futuramente incorporar Inteligência Artificial para auxílio na tomada de decisão.

O projeto está sendo desenvolvido com foco em:

- Arquitetura limpa
- Baixo acoplamento
- Alta escalabilidade
- Testabilidade
- Facilidade de manutenção
- Evolução contínua

---

# Objetivo Final

Construir uma plataforma profissional capaz de operar em:

- Paper Trading
- Binance Spot
- Binance Futures
- Bybit
- MetaTrader
- Corretoras brasileiras
- Multi Broker

Sem necessidade de alterar os módulos de estratégia, risco ou carteira.

---

# Princípios Arquiteturais

A arquitetura da AEGIS segue algumas regras fundamentais.

## 1. Responsabilidade Única

Cada módulo possui apenas uma responsabilidade.

## 2. Baixo Acoplamento

Os componentes não conhecem a implementação interna dos demais módulos.

## 3. Comunicação por Eventos

Toda comunicação entre módulos acontece através do EventBus.

Nenhum componente chama diretamente outro componente.

## 4. Escalabilidade

Novos módulos podem ser adicionados sem modificar os módulos existentes.

## 5. Testabilidade

Todo componente deve ser testável de forma isolada.

---

# Fluxo Atual da Aplicação

```
Market
   │
   ▼
Strategy
   │
   ▼
Risk
   │
   ▼
Execution
   │
   ▼
Portfolio
   │
   ▼
Performance
```

---

# Estrutura do Projeto

```
src/

application/
core/
database/
execution/
interfaces/
market/
models/
performance/
portfolio/
risk/
services/
strategies/
trading/
utils/
```

---

# Componentes

## Market

Responsável por coletar dados do mercado.

### Responsabilidades

- Buscar candles
- Normalizar informações
- Publicar eventos

Evento publicado

```
MARKET_CANDLES_RECEIVED
```

---

## Indicator Engine

Responsável pelo cálculo de indicadores técnicos.

Indicadores implementados

- SMA

Indicadores futuros

- EMA
- RSI
- ATR
- MACD
- VWAP
- Bollinger Bands

---

## Strategy Engine

Responsável por analisar o mercado.

Recebe candles.

Calcula indicadores.

Produz sinais.

Sinais possíveis

- BUY
- SELL
- HOLD

Publica

```
STRATEGY_SIGNAL_GENERATED
```

---

## Risk Manager

Recebe sinais produzidos pela estratégia.

Responsável por validar:

- saldo
- posição aberta
- duplicidade
- preço
- quantidade

Publica

```
RISK_OPERATION_APPROVED
```

ou

```
RISK_OPERATION_BLOCKED
```

---

## Execution Engine

Responsável por solicitar a execução de uma ordem.

Modo atual

Paper Trading

Publica

```
TRADE_REQUESTED
```

---

## Portfolio Engine

Autoridade final da execução.

Responsável por:

- atualizar saldo
- atualizar posições
- validar execução
- atualizar patrimônio

Publica

```
TRADE_EXECUTED
```

```
TRADE_REJECTED
```

```
PORTFOLIO_UPDATED
```

---

## Performance Engine

Responsável pelos indicadores financeiros.

Calcula:

- Equity
- PnL
- ROI
- Valor da Carteira

Publica

```
PERFORMANCE_UPDATED
```

---

# Eventos da Plataforma

Fluxo completo

```
MARKET_CANDLES_RECEIVED

↓

STRATEGY_SIGNAL_GENERATED

↓

RISK_OPERATION_APPROVED

↓

TRADE_REQUESTED

↓

TRADE_EXECUTED

↓

PORTFOLIO_UPDATED

↓

PERFORMANCE_UPDATED
```

---

# Funcionalidades Implementadas

## Infraestrutura

- EventBus
- Configuração centralizada
- Banner
- Settings

## Banco

- SQLite

## Mercado

- Binance Client

## Indicadores

- SMA

## Estratégia

- Strategy Engine

## Risco

- Risk Manager

## Execução

- Execution Engine

## Carteira

- Portfolio Engine

## Performance

- Performance Engine

## Trading

- Paper Trading

---

# Testes

Atualmente existem testes automatizados para

- Compra válida
- Compra sem saldo
- Compra duplicada
- Venda encerrando posição

Resultado atual

```
Ran 4 tests

OK
```

---

# Decisões Arquiteturais

## A Strategy nunca executa operações.

## O Risk nunca altera patrimônio.

## O Execution nunca decide.

## O Portfolio possui a autoridade da execução.

## Toda comunicação acontece através do EventBus.

---

# Próximas Versões

## v0.7.1

- Atualizar RiskManager para registrar apenas operações executadas.

---

## v0.8

Position Manager

---

## v0.9

Order Manager

---

## v1.0

Backtesting Engine

---

## v1.1

Multi Asset

---

## v1.2

WebSocket Binance

---

## v1.3

Trailing Stop

---

## v1.4

Take Profit

---

## v1.5

Stop Loss

---

## v2.0

Live Trading Binance

---

## v3.0

Machine Learning

---

## v4.0

Multi Broker

---

## v5.0

AEGIS AI

---

# Estado Atual

A arquitetura v0.7 representa a primeira versão estável da plataforma.

A Execution Architecture foi concluída com sucesso.

O fluxo completo entre Market, Strategy, Risk, Execution, Portfolio e Performance encontra-se funcional.

Os testes automatizados foram executados com sucesso e validam os principais cenários da arquitetura.

A plataforma está pronta para iniciar a evolução do gerenciamento de posições e da camada de ordens.

---

# Histórico de Marcos

| Versão | Marco |
|---------|-------|
| v0.1 | Estrutura inicial do projeto |
| v0.2 | Banco SQLite |
| v0.3 | Integração com Binance |
| v0.4 | Estratégias e indicadores |
| v0.5 | EventBus |
| v0.6 | Risk Manager |
| **v0.7** | **Execution Architecture** |

---

# Observação

Este documento representa o estado oficial da arquitetura da AEGIS.

Toda mudança estrutural relevante deve ser refletida neste arquivo antes da criação de uma nova versão e do respectivo commit no Git.