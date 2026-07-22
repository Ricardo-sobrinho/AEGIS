# RFC-006 — Event-Driven Trade Lifecycle Coordinator

**RFC:** 006

**Título:** Event-Driven Trade Lifecycle Coordinator

**Status:** Approved

**Versão do Projeto:** v0.9.0-alpha.6

**Data:** 21/07/2026

---

# 1. Objetivo

Definir a arquitetura do componente responsável por orquestrar todo o ciclo de vida de uma operação de Contrato de Tempo Fixo (Fixed-Time Contract), utilizando uma abordagem totalmente orientada a eventos.

O objetivo é manter todos os módulos desacoplados, preservando a responsabilidade de cada domínio e utilizando o EventBus como único mecanismo de comunicação entre os componentes.

---

# 2. Motivação

Até a RFC-005 todos os módulos da AEGIS foram desenvolvidos de forma independente.

Já existem componentes responsáveis por:

- Estratégia
- Gerenciamento de risco
- Gestão de banca
- Contrato
- Liquidação
- Performance

Entretanto, ainda não existe um componente responsável por coordenar a interação entre esses módulos.

Esta RFC introduz esse componente.

---

# 3. Problema

Uma implementação baseada em chamadas diretas entre módulos produziria:

- alto acoplamento;
- dificuldade de manutenção;
- baixa escalabilidade;
- maior risco de regressões.

Além disso, dificultaria a futura evolução para processamento assíncrono e múltiplas corretoras.

---

# 4. Solução Proposta

Introduzir um componente denominado:

```
TradeLifecycleCoordinator
```

Este componente atuará como um **Application Service** responsável exclusivamente pela orquestração do fluxo.

O Coordinator não implementará regras de negócio.

Todas as regras permanecerão nos módulos de domínio.

---

# 5. Princípios Arquiteturais

A implementação deverá seguir:

- SOLID
- Clean Architecture
- Domain Driven Design
- Event Driven Architecture
- Baixo Acoplamento
- Alta Coesão
- Dependency Injection

---

# 6. Arquitetura

```
Strategy Engine
        │
        ▼
Signal Generated
        │
        ▼
EventBus
        │
        ▼
TradeLifecycleCoordinator
        │
        ▼
Handlers
        │
        ├────────► RiskHandler
        ├────────► BankrollHandler
        ├────────► ContractHandler
        ├────────► ExecutionHandler
        ├────────► SettlementHandler
        └────────► PerformanceHandler
```

---

# 7. Coordinator

Responsabilidades:

- iniciar o fluxo;
- registrar handlers;
- controlar a orquestração;
- publicar eventos;
- tratar falhas de orquestração.

Não deve:

- calcular risco;
- movimentar saldo;
- criar regras financeiras;
- calcular performance.

---

# 8. Handlers

Cada etapa será implementada em um Handler especializado.

Estrutura:

```
src/coordinator/handlers/
```

Componentes previstos:

- BaseHandler
- RiskHandler
- BankrollHandler
- ContractHandler
- ExecutionHandler
- SettlementHandler
- PerformanceHandler

Cada Handler deverá possuir apenas uma responsabilidade.

---

# 9. Fluxo Principal

```
Signal Generated
        │
        ▼
RiskHandler
        │
        ▼
Risk Approved
        │
        ▼
BankrollHandler
        │
        ▼
Stake Reserved
        │
        ▼
ContractHandler
        │
        ▼
Trade Created
        │
        ▼
ExecutionHandler
        │
        ▼
Trade Accepted
        │
        ▼
SettlementHandler
        │
        ▼
Trade Settled
        │
        ▼
PerformanceHandler
        │
        ▼
Performance Updated
```

---

# 10. Eventos

Eventos do Coordinator:

- TRADE_LIFECYCLE_STARTED
- TRADE_RISK_APPROVED
- TRADE_RISK_REJECTED
- TRADE_STAKE_RESERVED
- TRADE_STAKE_RELEASED
- TRADE_CREATED
- TRADE_SUBMITTED
- TRADE_ACCEPTED
- TRADE_REJECTED
- TRADE_ACTIVATED
- TRADE_EXPIRED
- TRADE_SETTLED
- TRADE_COMPLETED
- TRADE_CANCELLED
- TRADE_FAILED

---

# 11. Estrutura do Projeto

```
src/coordinator/
│
├── __init__.py
├── events.py
├── exceptions.py
├── trade_lifecycle_coordinator.py
│
└── handlers/
    ├── __init__.py
    ├── base_handler.py
    ├── risk_handler.py
    ├── bankroll_handler.py
    ├── contract_handler.py
    ├── execution_handler.py
    ├── settlement_handler.py
    └── performance_handler.py
```

---

# 12. Decisões Arquiteturais

## Coordinator

É um Application Service.

Não contém regras de negócio.

---

## EventBus

Continua sendo o único mecanismo oficial de comunicação entre módulos.

---

## Handlers

Cada Handler trata exatamente um conjunto de eventos.

---

## Estado

O Coordinator deverá permanecer preferencialmente stateless.

O estado das operações permanece nas entidades e agregados de domínio.

---

# 13. Benefícios

Esta arquitetura proporciona:

- baixo acoplamento;
- alta testabilidade;
- facilidade para adicionar novos módulos;
- preparação para execução assíncrona;
- facilidade para auditoria;
- suporte futuro a múltiplas corretoras;
- suporte futuro a múltiplos ativos.

---

# 14. Critérios de Aceite

A RFC será considerada concluída quando:

- o TradeLifecycleCoordinator estiver implementado;
- todos os Handlers estiverem implementados;
- o fluxo completo estiver operacional;
- todos os eventos forem publicados corretamente;
- testes unitários aprovados;
- testes de integração aprovados;
- documentação atualizada.

---

# 15. Fora do Escopo

Esta RFC não contempla:

- integração com corretoras reais;
- execução em conta demo;
- interface gráfica;
- Machine Learning;
- Reinforcement Learning;
- otimização automática de estratégias.

Esses itens serão tratados em RFCs futuras.

---

# 16. Próximas Etapas

1. Implementar infraestrutura dos Handlers.
2. Criar BaseHandler.
3. Implementar RiskHandler.
4. Implementar BankrollHandler.
5. Implementar ContractHandler.
6. Implementar ExecutionHandler.
7. Implementar SettlementHandler.
8. Implementar PerformanceHandler.
9. Atualizar TradeLifecycleCoordinator.
10. Criar testes unitários.
11. Criar testes de integração.
12. Atualizar documentação.
13. Encerrar RFC-006.