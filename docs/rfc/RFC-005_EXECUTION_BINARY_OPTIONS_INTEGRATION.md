# RFC-005 — Fixed-Time Trade Lifecycle Integration

**Projeto:** AEGIS — Adaptive Evolutionary Global Intelligence System  
**Versão-alvo:** v0.10.0  
**Status:** Proposta para aprovação  
**Data:** Julho de 2026  
**Responsável técnico:** Arquiteto Principal da AEGIS  

---

## 1. Resumo

Esta RFC define a arquitetura responsável por integrar o ciclo completo
de uma operação de contrato de tempo fixo na AEGIS.

O fluxo contemplará:

1. recebimento de um sinal operacional;
2. criação da intenção de operação;
3. validação de risco;
4. criação do contrato;
5. reserva da stake;
6. envio para execução;
7. confirmação ou rejeição pela plataforma;
8. espera da expiração;
9. recebimento do resultado;
10. liquidação financeira;
11. atualização das métricas de desempenho;
12. encerramento auditável do ciclo de vida.

O componente responsável por coordenar esse fluxo será chamado
`TradeLifecycleCoordinator`.

O coordenador não será autoridade sobre nenhuma regra de domínio.
Ele apenas garantirá que os componentes especializados sejam chamados
na ordem correta e que nenhuma transição inválida seja permitida.

---

## 2. Motivação

A AEGIS possui atualmente componentes independentes para:

- dados de mercado;
- indicadores;
- estratégias;
- gerenciamento de risco;
- execução;
- gestão de banca;
- desempenho;
- portfolio de mercados tradicionais;
- comunicação orientada a eventos.

A RFC-004 concluiu o `BankrollEngine`, responsável pelos saldos
disponível e reservado, pelas transações financeiras e pelo ledger
imutável.

O próximo passo é integrar esses componentes para que uma operação de
tempo fixo percorra todo o seu ciclo de vida de maneira segura,
rastreável e testável.

A AEGIS deverá impedir situações como:

- execução sem aprovação de risco;
- execução sem stake reservada;
- liquidação duplicada;
- resultado recebido para contrato inexistente;
- liberação incorreta de reservas;
- envio duplicado para a corretora;
- alteração direta do saldo por componentes externos;
- transições de estado fora de ordem;
- fallback silencioso de execução real para paper.

---

## 3. Decisão arquitetural principal

Será criado o componente:

```text
TradeLifecycleCoordinator
```

Sua responsabilidade será coordenar o caso de uso completo de uma
operação de tempo fixo.

O coordenador poderá solicitar ações aos seguintes componentes:

```text
RiskManager
FixedTimeContractFactory
FixedTimeContractRepository
BankrollEngine
ExecutionEngine
BrokerAdapter
PerformanceEngine
EventBus
```

O coordenador não poderá:

- calcular indicadores;
- gerar sinais;
- definir regras de estratégia;
- aprovar risco diretamente;
- alterar saldo diretamente;
- criar transações financeiras manualmente;
- modificar o ledger;
- executar chamadas específicas de uma corretora;
- calcular resultados fora do domínio do contrato;
- atualizar posições do `PortfolioEngine`.

---

## 4. Separação entre Bankroll e Portfolio

### 4.1 BankrollEngine

O `BankrollEngine` será a autoridade financeira das operações de tempo
fixo.

Somente ele poderá:

- alterar o saldo disponível;
- alterar o saldo reservado;
- reservar uma stake;
- liberar uma stake;
- liquidar WIN;
- liquidar LOSS;
- liquidar DRAW;
- registrar transações no ledger;
- informar reservas vinculadas a contratos.

### 4.2 PortfolioEngine

O `PortfolioEngine` continuará responsável exclusivamente por posições
de mercados tradicionais, como:

- compra e venda spot;
- preço médio;
- quantidade do ativo;
- lucro realizado;
- lucro não realizado;
- valor de mercado das posições.

Contratos de tempo fixo não geram posição aberta tradicional.

Por isso, o fluxo definido nesta RFC não atualizará o
`PortfolioEngine`.

### 4.3 PerformanceEngine

O `PerformanceEngine` poderá receber os resultados liquidados dos
contratos para calcular métricas como:

- quantidade de operações;
- wins;
- losses;
- draws;
- taxa de acerto;
- lucro líquido;
- payout médio;
- retorno sobre a banca;
- sequência de resultados;
- drawdown;
- resultado por ativo;
- resultado por estratégia;
- resultado por período.

O `PerformanceEngine` não poderá alterar a banca.

---

## 5. Escopo

Esta RFC contempla:

- modelo de intenção de operação;
- modelo de contrato de tempo fixo;
- estados do ciclo de vida;
- direção CALL e PUT;
- stake;
- duração;
- horário de expiração;
- payout;
- preço de entrada;
- preço de expiração;
- WIN, LOSS e DRAW;
- coordenação entre risco, banca e execução;
- contrato abstrato de integração com corretoras;
- adaptador paper para testes;
- eventos de domínio;
- prevenção de processamento duplicado;
- tratamento de rejeições;
- estratégia de testes.

---

## 6. Fora do escopo

Não fazem parte desta RFC:

- integração com uma corretora real específica;
- operação com dinheiro real;
- autenticação em plataforma externa;
- armazenamento de credenciais;
- Machine Learning;
- Reinforcement Learning;
- martingale;
- soros;
- gerenciamento automático de estratégias;
- dashboard gráfico;
- execução distribuída;
- múltiplas corretoras simultâneas;
- recuperação automática após queda do processo;
- persistência em banco de dados de produção.

Esses recursos deverão ser tratados em RFCs posteriores.

---

## 7. Terminologia

### 7.1 Trade Intent

Representa a intenção de realizar uma operação antes da aprovação de
risco.

Deverá conter, no mínimo:

- `intent_id`;
- `symbol`;
- `direction`;
- `stake`;
- `duration`;
- `requested_payout`;
- `strategy_id`;
- `signal_id`;
- `created_at`;
- metadados opcionais.

### 7.2 Fixed-Time Contract

Representa uma operação de tempo fixo criada após a aprovação de risco.

Deverá conter, no mínimo:

- `contract_id`;
- `intent_id`;
- `symbol`;
- `direction`;
- `stake`;
- `payout`;
- `duration`;
- `created_at`;
- `expiration_at`;
- `entry_price`;
- `expiration_price`;
- `status`;
- `result`;
- `broker_reference`;
- `execution_mode`;
- `strategy_id`;
- `signal_id`;
- timestamps relevantes.

### 7.3 Stake

Valor financeiro comprometido na operação.

A stake deverá ser representada por `Decimal`.

### 7.4 Payout

Percentual de lucro oferecido para uma operação vencedora.

Exemplo:

```text
Stake: 100.00
Payout: 0.80
Lucro líquido em WIN: 80.00
Retorno total: 180.00
```

O payout deverá ser representado como taxa decimal:

```text
0.80 = 80%
```

### 7.5 Resultado

Resultados mínimos suportados:

```text
WIN
LOSS
DRAW
```

Resultados adicionais poderão existir no domínio do contrato:

```text
CANCELLED
UNKNOWN
```

`CANCELLED` e `UNKNOWN` não poderão ser liquidados como WIN, LOSS ou
DRAW sem uma decisão explícita do domínio.

---

## 8. Direção operacional

Será criado o enum:

```text
FixedTimeDirection
```

Valores:

```text
CALL
PUT
```

Regras:

- `CALL` vence quando o preço de expiração for maior que o preço de
  entrada;
- `PUT` vence quando o preço de expiração for menor que o preço de
  entrada;
- preços iguais resultam em `DRAW`, salvo regra explícita e documentada
  da plataforma;
- o adaptador da corretora deverá informar diferenças de regra quando
  existirem;
- nenhuma regra específica de corretora poderá contaminar o domínio
  central.

---

## 9. Estados do contrato

Será criado o enum:

```text
FixedTimeContractStatus
```

Estados propostos:

```text
CREATED
RISK_APPROVED
STAKE_RESERVED
SUBMITTED
ACCEPTED
ACTIVE
EXPIRED
SETTLED
REJECTED
CANCELLED
FAILED
```

---

## 10. Resultados do contrato

Será criado o enum:

```text
FixedTimeContractResult
```

Valores:

```text
PENDING
WIN
LOSS
DRAW
CANCELLED
UNKNOWN
```

Enquanto o contrato não estiver encerrado, seu resultado deverá ser
`PENDING`.

---

## 11. Modos de execução

Será criado o enum:

```text
ExecutionMode
```

Valores iniciais:

```text
PAPER
DEMO
REAL
```

Regras:

- `PAPER` executa inteiramente dentro da AEGIS;
- `DEMO` utiliza uma conta demonstrativa oficial da plataforma;
- `REAL` utiliza uma conta financeira real;
- nenhum modo poderá ser trocado silenciosamente durante uma operação;
- falha no modo `REAL` nunca poderá provocar execução automática em
  `PAPER`;
- o modo deverá ser registrado no contrato e nos eventos;
- a RFC-005 implementará obrigatoriamente o modo `PAPER`;
- `DEMO` e `REAL` serão preparados arquiteturalmente, mas não integrados
  a uma plataforma nesta RFC.

---

## 12. Máquina de estados

As transições válidas serão controladas explicitamente.

### 12.1 Fluxo bem-sucedido

```text
CREATED
   ↓
RISK_APPROVED
   ↓
STAKE_RESERVED
   ↓
SUBMITTED
   ↓
ACCEPTED
   ↓
ACTIVE
   ↓
EXPIRED
   ↓
SETTLED
```

### 12.2 Rejeição de risco

```text
CREATED
   ↓
REJECTED
```

Nenhuma stake será reservada.

### 12.3 Falha na reserva

```text
RISK_APPROVED
   ↓
FAILED
```

Nenhuma ordem será enviada.

### 12.4 Rejeição pela plataforma

```text
STAKE_RESERVED
   ↓
SUBMITTED
   ↓
REJECTED
```

A stake deverá ser liberada integralmente.

### 12.5 Cancelamento aceito pela plataforma

```text
ACCEPTED ou ACTIVE
   ↓
CANCELLED
```

O tratamento financeiro dependerá da confirmação retornada pelo
adaptador.

Nenhuma liberação será presumida sem resposta explícita.

### 12.6 Falha técnica após envio

Quando houver falha após o envio e antes de saber se a plataforma
aceitou a ordem:

```text
SUBMITTED
   ↓
FAILED
```

A stake não poderá ser liberada automaticamente enquanto a situação
externa estiver incerta.

Esse contrato deverá permanecer pendente de reconciliação.

---

## 13. Transições proibidas

Exemplos de transições inválidas:

```text
CREATED → ACTIVE
CREATED → SETTLED
RISK_APPROVED → SETTLED
STAKE_RESERVED → EXPIRED
REJECTED → ACTIVE
SETTLED → ACTIVE
SETTLED → SETTLED
CANCELLED → SETTLED
```

Toda tentativa inválida deverá gerar uma exceção de domínio sem alterar
o estado anterior.

---

## 14. TradeLifecycleCoordinator

### 14.1 Responsabilidade

O `TradeLifecycleCoordinator` será o caso de uso responsável por:

- receber a intenção;
- solicitar a decisão de risco;
- criar o contrato;
- reservar a stake;
- solicitar a execução;
- registrar respostas;
- coordenar a expiração;
- solicitar a liquidação;
- publicar eventos;
- impedir repetição de etapas;
- preservar consistência entre contrato e banca.

### 14.2 Dependências

O coordenador dependerá de abstrações sempre que houver comunicação com
infraestrutura.

Dependências previstas:

```text
RiskEvaluator
FixedTimeContractRepository
BankrollEngine
ExecutionGateway
PerformanceRecorder
EventPublisher
Clock
```

### 14.3 Restrições

O coordenador não deverá:

- conhecer detalhes HTTP ou WebSocket;
- conhecer endpoints de uma corretora;
- armazenar credenciais;
- calcular saldos;
- modificar estruturas internas do Bankroll;
- substituir regras do contrato;
- substituir regras de risco;
- manter um ledger paralelo;
- atualizar o PortfolioEngine.

---

## 15. Contrato do Broker Adapter

Será definida uma abstração semelhante a:

```text
FixedTimeBrokerAdapter
```

Responsabilidades:

- enviar contrato;
- retornar aceitação ou rejeição;
- retornar referência externa;
- consultar estado da operação quando suportado;
- consultar resultado quando suportado;
- informar preço de entrada confirmado;
- informar horário de expiração confirmado;
- informar payout confirmado;
- cancelar quando a plataforma permitir;
- diferenciar erros definitivos de estados incertos.

O domínio não deverá depender de SDK, HTTP, WebSocket ou formato
proprietário da corretora.

---

## 16. Resposta de submissão

O adaptador deverá retornar um objeto imutável com informações como:

```text
submission_id
contract_id
accepted
broker_reference
confirmed_entry_price
confirmed_payout
confirmed_expiration_at
rejection_reason
submitted_at
```

Regras:

- uma resposta aceita deverá possuir `broker_reference`;
- uma resposta rejeitada deverá possuir motivo;
- respostas inválidas deverão ser rejeitadas antes de alterar o
  contrato;
- o payout confirmado pela plataforma prevalecerá sobre o payout
  solicitado;
- alterações relevantes deverão ser registradas em evento.

---

## 17. Resultado de execução

O resultado recebido da plataforma deverá conter:

```text
contract_id
broker_reference
result
entry_price
expiration_price
stake
payout
gross_return
net_profit
expired_at
received_at
```

O domínio deverá validar a coerência desses dados antes da liquidação.

---

## 18. Regras financeiras

### 18.1 Reserva

Antes do envio ao adaptador:

```text
available_balance -= stake
reserved_balance += stake
```

A reserva deverá estar vinculada ao `contract_id`.

### 18.2 WIN

Para:

```text
stake = 100.00
payout = 0.80
```

O lucro líquido será:

```text
net_profit = stake × payout
net_profit = 80.00
```

O retorno bruto será:

```text
gross_return = stake + net_profit
gross_return = 180.00
```

Após a liquidação:

```text
reserved_balance -= 100.00
available_balance += 180.00
```

### 18.3 LOSS

Após a liquidação:

```text
reserved_balance -= stake
```

Nenhum valor será devolvido ao saldo disponível.

### 18.4 DRAW

Após a liquidação:

```text
reserved_balance -= stake
available_balance += stake
```

### 18.5 Rejeição antes da aceitação

Quando a plataforma rejeitar a operação de forma definitiva:

```text
reserved_balance -= stake
available_balance += stake
```

A reserva será liberada.

### 18.6 Falha de estado desconhecido

Quando não for possível determinar se a plataforma aceitou a operação:

- a reserva permanecerá bloqueada;
- o contrato será marcado para reconciliação;
- nenhuma liquidação será presumida;
- um evento crítico deverá ser publicado.

---

## 19. Idempotência

Todas as ações críticas deverão ser idempotentes.

A AEGIS deverá impedir:

- duas reservas para a mesma etapa;
- dois envios externos do mesmo contrato;
- dois processamentos da mesma resposta;
- duas liquidações;
- duas liberações da mesma reserva;
- reaplicação do mesmo resultado.

Identificadores previstos:

```text
intent_id
contract_id
transaction_id
submission_id
broker_reference
event_id
```

O mesmo evento poderá ser recebido mais de uma vez sem provocar alteração
financeira duplicada.

---

## 20. Atomicidade

Sempre que possível, cada operação deverá seguir o padrão:

1. validar os dados;
2. calcular o próximo estado;
3. validar o próximo estado;
4. confirmar a alteração;
5. publicar o evento correspondente.

Nenhum evento de sucesso poderá ser publicado antes da confirmação da
mudança de estado.

Falhas não poderão deixar estados parcialmente alterados.

---

## 21. Eventos de domínio

Os eventos deverão ser imutáveis e possuir pelo menos:

```text
event_id
occurred_at
correlation_id
contract_id
```

Eventos previstos:

```text
TRADE_INTENT_CREATED
TRADE_RISK_APPROVED
TRADE_RISK_REJECTED
FIXED_TIME_CONTRACT_CREATED
BANKROLL_STAKE_RESERVED
BANKROLL_STAKE_RESERVATION_FAILED
FIXED_TIME_CONTRACT_SUBMITTED
FIXED_TIME_CONTRACT_ACCEPTED
FIXED_TIME_CONTRACT_REJECTED
FIXED_TIME_CONTRACT_ACTIVATED
FIXED_TIME_CONTRACT_EXPIRED
FIXED_TIME_CONTRACT_RESULT_RECEIVED
FIXED_TIME_CONTRACT_SETTLED
FIXED_TIME_CONTRACT_CANCELLED
FIXED_TIME_CONTRACT_FAILED
BANKROLL_STAKE_RELEASED
BANKROLL_SETTLEMENT_COMPLETED
PERFORMANCE_UPDATED
TRADE_RECONCILIATION_REQUIRED
```

---

## 22. Correlação e rastreabilidade

Todos os eventos de uma mesma operação deverão compartilhar um
`correlation_id`.

Exemplo:

```text
signal_id
    ↓
intent_id
    ↓
contract_id
    ↓
submission_id
    ↓
broker_reference
    ↓
settlement transaction_id
```

Isso permitirá reconstruir todo o histórico da operação.

---

## 23. Repositório de contratos

Será criada uma abstração:

```text
FixedTimeContractRepository
```

Operações mínimas:

```text
add
get_by_id
exists
update
```

A implementação inicial poderá utilizar memória.

Regras:

- não aceitar dois contratos com o mesmo `contract_id`;
- não expor armazenamento interno mutável;
- retornar o contrato atual de maneira segura;
- não conter regras financeiras;
- não acessar diretamente o BankrollEngine.

---

## 24. Relógio abstrato

Será criada uma abstração de relógio:

```text
Clock
```

Objetivo:

- obter horário UTC;
- calcular expiração;
- facilitar testes determinísticos;
- evitar dependência direta e espalhada de `datetime.now()`.

Implementações previstas:

```text
SystemClock
FixedClock
```

`SystemClock` será usado em execução normal.

`FixedClock` será usado em testes.

---

## 25. Paper Broker Adapter

A primeira implementação será:

```text
PaperFixedTimeBrokerAdapter
```

Responsabilidades:

- aceitar contratos válidos;
- registrar preço de entrada;
- respeitar expiração;
- receber ou consultar preço de encerramento;
- calcular WIN, LOSS ou DRAW;
- retornar resultado padronizado;
- permitir testes determinísticos.

O adaptador paper não poderá acessar ou alterar o saldo diretamente.

Ele deverá apenas retornar respostas ao coordenador.

---

## 26. Integração com RiskManager

A RFC deverá adaptar ou envolver o `RiskManager` existente por meio de
um contrato apropriado ao domínio de tempo fixo.

A decisão de risco deverá conter:

```text
approved
reason
stake
symbol
direction
expiration_at
risk_policy_id
evaluated_at
```

Regras mínimas:

- stake maior que zero;
- saldo disponível suficiente;
- stake dentro do limite por operação;
- exposição simultânea dentro do limite;
- quantidade de contratos ativos dentro do limite;
- payout mínimo aceitável;
- duração permitida;
- ativo permitido;
- direção válida;
- horário válido;
- bloqueios de risco respeitados.

O `RiskManager` não reservará a stake.

A reserva continuará pertencendo exclusivamente ao `BankrollEngine`.

---

## 27. Tratamento de sinais HOLD

Sinais `HOLD` não deverão criar intenção de operação nem contrato.

O fluxo deverá terminar antes da avaliação financeira.

Para contratos de tempo fixo, sinais tradicionais deverão ser
normalizados da seguinte forma:

```text
BUY  → CALL
SELL → PUT
HOLD → nenhuma operação
```

A normalização deverá ocorrer em um componente explícito, sem modificar
silenciosamente o significado do sinal original.

---

## 28. Exceções de domínio

Exceções previstas:

```text
InvalidTradeIntentError
InvalidFixedTimeContractError
InvalidFixedTimeContractTransitionError
DuplicateFixedTimeContractError
FixedTimeContractNotFoundError
FixedTimeContractAlreadySettledError
FixedTimeContractSubmissionError
FixedTimeContractResultError
FixedTimeContractReconciliationRequiredError
StakeReservationError
RiskApprovalRequiredError
BrokerOperationRejectedError
```

As exceções deverão possuir mensagens claras e não expor segredos ou
credenciais.

---

## 29. Consistência entre contrato e Bankroll

Antes da execução:

```text
contract.status == STAKE_RESERVED
bankroll.reserved_for_contract(contract_id) == contract.stake
```

Antes da liquidação:

```text
contract.status == EXPIRED
contract.result in {WIN, LOSS, DRAW}
bankroll.reserved_for_contract(contract_id) == contract.stake
```

Após a liquidação:

```text
contract.status == SETTLED
bankroll.reserved_for_contract(contract_id) == 0
```

Qualquer divergência deverá interromper o processamento.

---

## 30. Segurança operacional

A RFC deverá respeitar estas regras:

- conta real não será habilitada por padrão;
- credenciais não serão colocadas no código;
- credenciais não serão armazenadas em eventos;
- dados sensíveis não aparecerão em logs;
- não haverá fallback silencioso;
- toda execução informará explicitamente seu modo;
- operações reais futuras exigirão configuração explícita;
- conta demo será obrigatória antes de operação real;
- martingale não será comportamento padrão;
- limites de risco não poderão ser ignorados pelo coordenador;
- erros de comunicação não serão interpretados como rejeição definitiva;
- estados incertos exigirão reconciliação.

---

## 31. Observabilidade

Cada etapa deverá permitir registro estruturado com:

```text
event_id
correlation_id
contract_id
symbol
direction
stake
status
execution_mode
broker_reference
occurred_at
```

Logs não serão a fonte de verdade financeira.

As fontes de verdade serão:

- estado do contrato;
- repositório de contratos;
- ledger do Bankroll;
- resposta confirmada do adaptador.

---

## 32. Estratégia de implementação

A implementação será dividida em etapas pequenas.

### Etapa 1 — Domínio básico

Criar:

```text
src/fixed_time/
    __init__.py
    enums.py
    exceptions.py
    trade_intent.py
    contract.py
```

Testes:

```text
tests/fixed_time/
    __init__.py
    test_enums.py
    test_trade_intent.py
    test_contract.py
```

### Etapa 2 — Factory e transições

Criar:

```text
src/fixed_time/
    contract_factory.py
    lifecycle.py
```

Testes:

```text
tests/fixed_time/
    test_contract_factory.py
    test_lifecycle.py
```

### Etapa 3 — Repositório

Criar:

```text
src/fixed_time/
    repository.py
```

Testes:

```text
tests/fixed_time/
    test_repository.py
```

### Etapa 4 — Contratos de execução

Criar:

```text
src/execution/
    fixed_time_gateway.py
    fixed_time_responses.py
```

Testes:

```text
tests/execution/
    test_fixed_time_responses.py
```

### Etapa 5 — Paper Adapter

Criar:

```text
src/infrastructure/brokers/
    paper_fixed_time_adapter.py
```

Testes:

```text
tests/infrastructure/brokers/
    test_paper_fixed_time_adapter.py
```

### Etapa 6 — Eventos

Criar ou atualizar:

```text
src/events/
    fixed_time_events.py
```

Testes:

```text
tests/events/
    test_fixed_time_events.py
```

### Etapa 7 — Coordenador

Criar:

```text
src/services/
    trade_lifecycle_coordinator.py
```

Testes:

```text
tests/services/
    test_trade_lifecycle_coordinator.py
```

### Etapa 8 — Integração

Criar testes de integração para:

```text
WIN
LOSS
DRAW
RISK_REJECTED
STAKE_RESERVATION_FAILED
BROKER_REJECTED
DUPLICATE_RESULT
UNKNOWN_SUBMISSION_STATE
```

---

## 33. Estratégia de testes

A RFC deverá possuir testes unitários e de integração.

### 33.1 Testes do domínio

Validar:

- criação de intenção válida;
- rejeição de intenção inválida;
- criação do contrato;
- valores de enum;
- imutabilidade;
- timestamps UTC;
- expiração;
- CALL;
- PUT;
- payout;
- stake;
- transições válidas;
- transições inválidas;
- proibição de liquidação duplicada.

### 33.2 Testes financeiros

Validar:

- reserva antes da execução;
- impossibilidade de executar sem reserva;
- WIN;
- LOSS;
- DRAW;
- liberação em rejeição;
- manutenção da reserva em estado incerto;
- ausência de saldo duplicado;
- atomicidade em falhas.

### 33.3 Testes do adaptador paper

Validar:

- aceitação;
- rejeição;
- preço de entrada;
- expiração;
- CALL WIN;
- CALL LOSS;
- PUT WIN;
- PUT LOSS;
- DRAW;
- resposta duplicada;
- contrato desconhecido.

### 33.4 Testes do coordenador

Validar:

- fluxo completo de WIN;
- fluxo completo de LOSS;
- fluxo completo de DRAW;
- risco rejeitado;
- saldo insuficiente;
- ordem rejeitada;
- erro antes do envio;
- erro depois do envio;
- processamento idempotente;
- eventos em ordem correta;
- inexistência de atualização do PortfolioEngine.

### 33.5 Teste da suíte completa

Ao final de cada etapa:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Critério obrigatório:

```text
0 failures
0 errors
```

---

## 34. Critérios de aceite

A RFC-005 será considerada concluída somente quando:

- o domínio de contrato de tempo fixo estiver implementado;
- CALL e PUT estiverem implementados;
- WIN, LOSS e DRAW estiverem implementados;
- estados e transições estiverem protegidos;
- a stake for reservada antes da execução;
- a operação rejeitada liberar a stake corretamente;
- estados incertos mantiverem a reserva;
- a liquidação for idempotente;
- o adaptador paper estiver funcional;
- o coordenador estiver funcional;
- os eventos estiverem implementados;
- os testes unitários estiverem aprovados;
- os testes de integração estiverem aprovados;
- a suíte completa permanecer verde;
- o `PortfolioEngine` não for usado no fluxo de tempo fixo;
- o `BankrollEngine` permanecer como única autoridade financeira;
- a documentação for atualizada;
- o checkpoint mestre for atualizado;
- o commit da RFC for realizado;
- a versão v0.10.0 for registrada.

---

## 35. Riscos conhecidos

### 35.1 Duplicidade de resultado

Uma plataforma poderá entregar o mesmo resultado mais de uma vez.

Mitigação:

- idempotência por contrato e referência externa;
- proibição de liquidação duplicada.

### 35.2 Falha após envio

A conexão poderá cair depois que a ordem for enviada.

Mitigação:

- não presumir rejeição;
- manter a reserva;
- marcar reconciliação obrigatória.

### 35.3 Divergência de payout

O payout poderá mudar entre a intenção e a aceitação.

Mitigação:

- armazenar payout solicitado e confirmado;
- validar novamente limites de risco quando necessário;
- registrar a alteração.

### 35.4 Divergência de horário

A corretora poderá confirmar horário de expiração diferente.

Mitigação:

- usar horário confirmado;
- registrar a diferença;
- rejeitar diferenças fora dos limites permitidos.

### 35.5 Acoplamento excessivo

O coordenador poderá crescer demais.

Mitigação:

- manter casos de uso pequenos;
- delegar regras para objetos de domínio;
- impedir regras financeiras dentro do coordenador;
- refatorar em serviços específicos quando necessário.

---

## 36. Dívidas técnicas aceitas

Durante esta RFC serão aceitas temporariamente:

- repositório em memória;
- EventBus síncrono;
- execução paper no mesmo processo;
- ausência de persistência transacional;
- ausência de reconciliação automática;
- ausência de broker real;
- ausência de dashboard.

Essas limitações deverão permanecer registradas e serão tratadas em
RFCs futuras.

---

## 37. Compatibilidade

Os componentes existentes de trading tradicional serão preservados.

O novo domínio deverá ser adicionado sem quebrar:

- `PortfolioEngine`;
- `Position`;
- fluxo spot já testado;
- eventos tradicionais existentes;
- `BankrollEngine`;
- `BankrollTransaction`;
- `BankrollTransactionFactory`;
- `BankrollStatistics`;
- testes atuais.

Qualquer mudança incompatível exigirá decisão explícita e documentação.

---

## 38. Versionamento

A versão-alvo desta RFC será:

```text
v0.10.0
```

Justificativa:

- introdução de um novo domínio operacional;
- novo ciclo completo de contratos;
- novo coordenador;
- novos estados;
- novos eventos;
- novo adaptador paper;
- integração financeira e operacional.

---

## 39. Próximas RFCs previstas

Após a conclusão desta RFC, poderão ser abertas:

```text
RFC-006 — Risk Policies for Fixed-Time Contracts
RFC-007 — Demo Broker Integration
RFC-008 — Reconciliation and Recovery
RFC-009 — Fixed-Time Performance Analytics
RFC-010 — Observability and Operational Dashboard
RFC-011 — Controlled Real-Money Execution
```

A integração real somente será considerada depois de:

- conta demo funcional;
- estabilidade comprovada;
- reconciliação;
- observabilidade;
- limites de risco;
- auditoria;
- aprovação técnica formal.

---

## 40. Decisão final proposta

A RFC-005 propõe oficialmente:

1. criar o domínio `fixed_time`;
2. adotar `TradeLifecycleCoordinator`;
3. manter `BankrollEngine` como única autoridade financeira;
4. não atualizar `PortfolioEngine` em contratos de tempo fixo;
5. utilizar adaptadores desacoplados para execução;
6. implementar primeiro um adaptador paper;
7. proteger o ciclo com máquina de estados;
8. exigir idempotência nas operações críticas;
9. manter reservas em situações externas incertas;
10. impedir fallback silencioso entre modos de execução;
11. usar eventos imutáveis e correlacionados;
12. entregar a funcionalidade em etapas pequenas e testadas.

---

## 41. Status de aprovação

```text
RFC: RFC-005
Título: Fixed-Time Trade Lifecycle Integration
Status atual: PROPOSTA
Versão-alvo: v0.10.0
Implementação autorizada: NÃO
```

A implementação será autorizada somente após a aprovação formal deste
documento.

---

**Fim da RFC-005**