# CHANGELOG

Todas as mudanças relevantes da AEGIS (Adaptive Evolutionary Global Intelligence System) são registradas neste documento.

O projeto adota evolução incremental baseada em RFCs (Request for Comments), garantindo rastreabilidade das decisões arquiteturais, implementações e marcos de desenvolvimento.

---

# Informações do Projeto

| Item | Valor |
|------|--------|
| Projeto | AEGIS |
| Arquitetura | Clean Architecture + SOLID + Event Driven Architecture |
| Linguagem | Python 3.13 |
| Status | Em desenvolvimento |
| Versão atual | **v0.9.0-alpha.5** |
| Próxima RFC | RFC-006 – Trade Lifecycle Coordinator |

---

# Histórico de Versões

---

# v0.9.0-alpha.5

**Data:** Julho/2026

**Status:** RFC-005 Finalizada

## Objetivo

Implementar completamente o domínio responsável pelos contratos de tempo fixo (Fixed-Time Contracts), tornando a entidade `FixedTimeContract` a única autoridade sobre o ciclo de vida dos contratos.

---

## Adicionado

### Domínio Fixed-Time

- FixedTimeContract
- FixedTimeSettlementCalculator
- SettlementCalculation

---

### Ciclo de Vida

Implementadas todas as transições de estado protegidas:

- approve_risk()
- reserve_stake()
- submit()
- accept()
- activate()
- expire()
- settle()
- reject()
- cancel()
- fail()

---

### Estados

Implementados:

- CREATED
- RISK_APPROVED
- STAKE_RESERVED
- SUBMITTED
- ACCEPTED
- ACTIVE
- EXPIRED
- SETTLED
- REJECTED
- CANCELLED
- FAILED

---

### Validações

Implementadas validações completas para:

- símbolo
- stake
- payout
- duração
- direction
- strategy_id
- signal_id
- execution_mode
- broker_reference
- entry_price
- expiration_price

---

### Resultado Financeiro

Implementado:

- determine_result()

Suporte para:

- WIN
- LOSS
- DRAW

---

### Settlement

Implementado:

- cálculo financeiro do contrato
- retorno líquido
- lucro
- prejuízo
- draw

---

### Exceções

Criadas exceções específicas:

- InvalidFixedTimeContractError
- InvalidFixedTimeContractTransitionError
- FixedTimeContractAlreadySettledError
- InvalidStakeError
- InvalidPayoutError
- InvalidContractDirectionError
- InvalidContractPriceError

---

## Arquitetura

Removido definitivamente:

- FixedTimeContractStateMachine

A entidade `FixedTimeContract` passa a ser responsável por todo o ciclo de vida do contrato.

---

## Compatibilidade

Atualizado:

```
src/fixed_time/__init__.py
```

Mantidos aliases públicos para preservar compatibilidade.

---

## Testes

Nova suíte de testes para:

- ciclo completo
- transições válidas
- transições inválidas
- estados terminais
- dupla liquidação
- dupla ativação
- dupla aceitação
- dupla submissão
- cálculo de resultado

Resultado:

```text
Ran 267 tests

OK
```

---

## Próxima Etapa

RFC-006

Trade Lifecycle Coordinator

---

# v0.9.0

**Data:** Julho/2026

**Status:** RFC-004 Finalizada

## Objetivo

Implementar um módulo financeiro desacoplado responsável pelo gerenciamento completo da banca da AEGIS.

---

## Adicionado

### Bankroll

- BankrollEngine
- BankrollStatistics
- BankrollTransaction
- BankrollTransactionFactory

---

### Funcionalidades

- saldo disponível
- saldo reservado
- ledger financeiro
- reserva de stake
- liberação de stake
- liquidação WIN
- liquidação LOSS
- liquidação DRAW
- depósitos
- saques
- ajustes financeiros
- controle por Contract ID
- estatísticas

---

## Garantias

- Ledger imutável
- Operações atômicas
- Apenas BankrollEngine altera saldos
- Snapshot imutável

---

## Testes

```text
Ran 234 tests

OK
```

---

# v0.8.0

## RFC-002

Portfolio Engine

### Adicionado

- PortfolioEngine
- controle de posições
- preço médio
- lucro realizado
- lucro não realizado
- patrimônio
- compra
- venda parcial
- venda total
- atualização de preços

### Garantias

- PositionManager removido
- Apenas PortfolioEngine altera posições

---

# v0.7.0

## RFC-001

Execution Architecture

### Adicionado

- Execution Engine
- EventBus
- Eventos
- Integração entre módulos

---

# v0.6.0

Core Trading

### Adicionado

- Performance Engine
- Risk Manager
- Strategy Engine
- Paper Trading Engine
- Indicator Engine
- Candle Repository

---

# v0.5.0

### Adicionado

- Binance Client
- Market Data
- Candle Repository

---

# v0.4.0

### Adicionado

- Estrutura inicial do projeto
- Organização da arquitetura
- Primeiros testes

---

# Estatísticas Atuais

## Arquitetura

- Clean Architecture
- SOLID
- Event Driven Architecture
- Domain Driven Design (parcial)

---

## Componentes Implementados

- Event Bus
- Market Data
- Candle Repository
- Indicator Engine
- Strategy Engine
- Risk Manager (Legado)
- Portfolio Engine
- Performance Engine
- Paper Trading Engine
- Bankroll Engine
- Fixed-Time Contract Domain

---

## Testes

```text
267 testes
0 falhas
100% aprovados
```

---

# Próximo Marco

## RFC-006

Trade Lifecycle Coordinator

Objetivos:

- coordenar o ciclo completo da operação;
- integrar handlers especializados;
- desacoplar o fluxo de execução;
- preparar integração com o novo motor de risco.

---

Fim do documento.