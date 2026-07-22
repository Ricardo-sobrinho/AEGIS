# 1. Contexto

Desde as primeiras versões da AEGIS, a arquitetura foi desenvolvida com foco em
modularidade, baixo acoplamento e separação clara de responsabilidades. Cada
RFC aprovada introduziu novos componentes especializados, permitindo que o
projeto evoluísse de forma incremental sem comprometer funcionalidades já
estáveis.

As RFCs anteriores estabeleceram os principais pilares da plataforma:

- RFC-004 consolidou o gerenciamento financeiro por meio do BankrollEngine,
  definindo uma única autoridade responsável pelo controle de saldo,
  movimentações financeiras, reservas e liquidações.

- RFC-005 introduziu o domínio de Contratos de Tempo Fixo, estabelecendo um
  modelo próprio para representar operações CALL e PUT, seu ciclo de vida e
  seus estados, sem reutilizar conceitos tradicionais de compra e venda de
  ativos.

- RFC-006 implementou o TradeLifecycleCoordinator, responsável por orquestrar
  todas as etapas do ciclo operacional através de eventos, mantendo os
  componentes desacoplados e preservando a arquitetura orientada a eventos da
  AEGIS.

Com esses componentes concluídos, a arquitetura passa a possuir todos os
elementos necessários para iniciar a validação de risco das operações.

Entretanto, o projeto ainda depende de um componente de risco originalmente
desenvolvido para um domínio diferente do atual.

O componente localizado em:

```text
src/services/risk_manager.py
```

foi criado para avaliar operações tradicionais de trading baseadas em posições,
utilizando conceitos como BUY, SELL, abertura de posição, redução de posição e
encerramento de posição.

Esse modelo não representa corretamente o funcionamento dos Contratos de Tempo
Fixo.

Em operações Fixed-Time não existe posição aberta aguardando encerramento.
Cada contrato nasce completo, possui um valor previamente definido, um tempo de
expiração conhecido e um resultado único ao final de seu ciclo de vida.

Consequentemente, os riscos associados também são diferentes.

Enquanto o modelo tradicional concentra sua avaliação na gestão contínua de uma
posição aberta, o domínio de Contratos de Tempo Fixo exige validações
específicas antes mesmo da criação do contrato, tais como:

- valor da stake;
- percentual máximo de exposição da banca;
- payout mínimo aceitável;
- quantidade máxima de contratos simultâneos;
- disponibilidade financeira para abertura da operação.

Essas regras pertencem exclusivamente ao domínio de Contratos de Tempo Fixo e
não devem ser incorporadas ao RiskManager legado, pois isso aumentaria o
acoplamento entre dois modelos de negócio distintos e reduziria a capacidade de
manutenção da arquitetura.

Por esse motivo, esta RFC propõe a criação de um novo componente denominado
FixedTimeRiskManager.

Esse componente será responsável exclusivamente pela avaliação de risco das
operações Fixed-Time, preservando o RiskManager existente para o domínio legado
e mantendo a independência entre os dois modelos de operação.

Essa decisão está alinhada aos princípios arquiteturais já adotados pela AEGIS,
especialmente:

- responsabilidade única (Single Responsibility Principle);
- baixo acoplamento;
- alta coesão;
- evolução incremental da arquitetura;
- compatibilidade retroativa;
- separação entre domínios de negócio.

Ao final desta RFC, a AEGIS passará a possuir uma camada de avaliação de risco
dedicada ao domínio de Contratos de Tempo Fixo, preparada para suportar as
próximas etapas do projeto, incluindo integração com corretoras, execução em
conta demo e futuras operações em ambiente real.

# 2. Problema

Com a conclusão da RFC-006, a arquitetura da AEGIS passou a possuir um fluxo
operacional completo para o processamento de eventos relacionados aos
Contratos de Tempo Fixo. Entretanto, ainda não existe um componente de risco
capaz de avaliar esse domínio de forma nativa.

O único mecanismo de avaliação de risco disponível atualmente é o componente:

```text
src/services/risk_manager.py
```

Esse componente foi desenvolvido para um modelo tradicional de trading baseado
em posições abertas, onde uma operação pode ser iniciada, ampliada, reduzida ou
encerrada ao longo do tempo.

Esse modelo parte das seguintes premissas:

- existência de posições abertas;
- operações BUY e SELL;
- acompanhamento contínuo da posição;
- encerramento manual ou estratégico da operação;
- gerenciamento do risco durante toda a vida útil da posição.

Essas premissas não são compatíveis com o domínio de Contratos de Tempo Fixo.

Nesse modelo operacional, cada contrato representa uma operação independente,
com início e fim previamente definidos. O contrato nasce completo, possui uma
stake fixa, um payout conhecido no momento da abertura e uma expiração
determinada, sendo encerrado automaticamente ao final do período contratado.

Consequentemente, o processo de avaliação de risco também é diferente.

Ao invés de acompanhar continuamente uma posição aberta, o sistema deve decidir,
antes da criação do contrato, se aquela operação atende às políticas de risco
estabelecidas para a banca.

Entre as principais validações exigidas por esse domínio destacam-se:

- valor mínimo e máximo da stake;
- percentual máximo da banca permitido por operação;
- payout mínimo aceitável;
- saldo disponível para abertura do contrato;
- exposição financeira máxima da banca;
- quantidade máxima de contratos simultaneamente ativos.

Essas regras não pertencem ao domínio do RiskManager legado e sua incorporação
ao componente existente produziria um aumento significativo do acoplamento entre
dois modelos de negócio distintos.

Além disso, adaptar o componente legado introduziria diversos problemas
arquiteturais, incluindo:

- mistura de conceitos de BUY/SELL com CALL/PUT;
- coexistência de regras incompatíveis dentro do mesmo componente;
- aumento da complexidade de manutenção;
- crescimento da quantidade de condicionais específicas por domínio;
- maior probabilidade de regressões em funcionalidades já estabilizadas;
- redução da clareza das responsabilidades do componente.

Essa abordagem violaria princípios arquiteturais adotados desde o início do
projeto, especialmente:

- Single Responsibility Principle;
- Separation of Concerns;
- baixo acoplamento;
- alta coesão.

Outro aspecto importante é a evolução futura da plataforma.

A arquitetura da AEGIS foi planejada para permitir a coexistência de múltiplos
domínios de operação. No futuro, o projeto poderá suportar simultaneamente
operações de Contratos de Tempo Fixo, mercados tradicionais, criptomoedas,
Forex e outros ativos financeiros.

Caso todas essas regras fossem concentradas em um único mecanismo de risco, o
componente se tornaria progressivamente mais complexo, dificultando sua
evolução, testes e manutenção.

Dessa forma, o problema identificado por esta RFC não consiste apenas na
ausência de determinadas validações, mas na inexistência de um mecanismo de
avaliação de risco especializado para o domínio de Contratos de Tempo Fixo.

A solução adotada deverá preservar integralmente o componente legado e
introduzir um novo motor de risco dedicado exclusivamente ao novo domínio,
permitindo que ambos evoluam de maneira independente e sem interferências
arquiteturais.

# 3. Decisão Arquitetural

Após a análise apresentada nas seções anteriores, conclui-se que a solução mais
adequada para o domínio de Contratos de Tempo Fixo consiste na criação de um
novo mecanismo de avaliação de risco, independente do componente atualmente
utilizado pelo fluxo legado.

A arquitetura aprovada por esta RFC estabelece a criação do componente:

```text
src/risk/fixed_time_risk_manager.py
```

cuja implementação será representada pela classe:

```python
FixedTimeRiskManager
```

Esse componente será responsável exclusivamente pela avaliação das regras de
risco aplicáveis ao domínio de Contratos de Tempo Fixo.

Nenhuma responsabilidade adicional será incorporada ao motor de risco.

Entre suas atribuições estão:

- validar a consistência da requisição de risco;
- validar a política de risco utilizada;
- avaliar todas as regras definidas para abertura de um contrato;
- retornar uma decisão determinística de aprovação ou rejeição.

O componente não deverá:

- criar contratos;
- reservar saldo;
- alterar a banca;
- executar ordens;
- publicar eventos;
- acessar banco de dados;
- acessar APIs externas;
- modificar qualquer estado interno da aplicação.

Todas essas responsabilidades permanecerão distribuídas entre os componentes já
existentes na arquitetura.

A separação das responsabilidades será a seguinte:

```text
TradeLifecycleCoordinator
        │
        ▼
RiskHandler
        │
        ▼
FixedTimeRiskManager
        │
        ▼
FixedTimeRiskDecision
```

Nesse fluxo:

- o TradeLifecycleCoordinator continuará responsável pela orquestração do ciclo
  operacional;

- o RiskHandler continuará responsável pela integração entre os eventos e o
  mecanismo de avaliação de risco;

- o FixedTimeRiskManager será responsável apenas pela aplicação das regras de
  negócio relacionadas ao risco;

- o FixedTimeRiskDecision representará o resultado imutável da avaliação.

Essa separação preserva o princípio da responsabilidade única e reduz o
acoplamento entre os componentes da arquitetura.

## Preservação do componente legado

O componente localizado em:

```text
src/services/risk_manager.py
```

não sofrerá qualquer alteração durante a implementação desta RFC.

Ele continuará disponível para atender fluxos que dependam do modelo
tradicional de trading baseado em posições.

Essa decisão possui os seguintes benefícios:

- elimina riscos de regressão;
- preserva compatibilidade com implementações existentes;
- permite evolução independente dos dois domínios;
- reduz o impacto das alterações sobre componentes já estabilizados.

## Avaliação das alternativas

Durante a definição desta RFC foram consideradas três possibilidades.

### Alternativa 1 — Adaptar o RiskManager existente

Descrição:

Adicionar ao componente legado todas as regras específicas de Contratos de Tempo
Fixo.

Resultado da análise:

Rejeitada.

Motivos:

- mistura dois domínios distintos;
- aumenta o acoplamento;
- dificulta manutenção;
- aumenta o número de condicionais;
- reduz a clareza das responsabilidades.

---

### Alternativa 2 — Criar um único RiskManager genérico

Descrição:

Construir um componente único capaz de atender qualquer domínio através de
configurações.

Resultado da análise:

Rejeitada.

Motivos:

- abstração prematura;
- complexidade desnecessária;
- regras específicas continuariam coexistindo;
- maior dificuldade de testes.

---

### Alternativa 3 — Criar um FixedTimeRiskManager dedicado

Descrição:

Criar um componente especializado apenas para o domínio de Contratos de Tempo
Fixo.

Resultado da análise:

Aprovada.

Motivos:

- responsabilidade única;
- baixo acoplamento;
- maior coesão;
- testes mais simples;
- evolução independente;
- maior clareza arquitetural.

## Princípios adotados

A implementação deverá respeitar os seguintes princípios:

- Single Responsibility Principle;
- Open/Closed Principle;
- Separation of Concerns;
- Clean Architecture;
- Domain-Driven Design;
- Event Driven Architecture.

## Decisão final

Fica oficialmente aprovada a criação de um novo componente denominado
FixedTimeRiskManager como mecanismo exclusivo de avaliação de risco para
Contratos de Tempo Fixo.

Esse componente será completamente independente do RiskManager legado e será
integrado à arquitetura exclusivamente através do RiskHandler, preservando o
baixo acoplamento entre os domínios da aplicação.

Essa decisão passa a fazer parte da arquitetura oficial da AEGIS e deverá ser
observada em todas as implementações futuras relacionadas ao domínio de
Contratos de Tempo Fixo.

# 4. Objetivo

O objetivo desta RFC é introduzir um mecanismo de avaliação de risco dedicado ao
domínio de Contratos de Tempo Fixo, preservando a separação de responsabilidades
estabelecida pela arquitetura da AEGIS e garantindo que todas as operações
sejam submetidas a uma validação consistente antes da criação do contrato.

Para atingir esse objetivo será implementado o componente
`FixedTimeRiskManager`, responsável exclusivamente pela avaliação das políticas
de risco aplicáveis a uma solicitação de abertura de contrato.

O componente deverá receber uma requisição contendo todas as informações
necessárias para a análise e produzir uma única decisão determinística,
indicando se a operação pode ou não prosseguir.

Essa decisão deverá ser baseada exclusivamente nos dados fornecidos na
requisição e na política de risco vigente, sem depender de estado interno,
componentes externos ou efeitos colaterais.

O resultado da avaliação será representado por um objeto imutável denominado
`FixedTimeRiskDecision`, que conterá todas as informações necessárias para que
os demais componentes da arquitetura deem continuidade ao fluxo operacional.

## Responsabilidades

O FixedTimeRiskManager será responsável por:

- validar a integridade da requisição de risco;
- validar a política de risco utilizada;
- verificar se a stake atende aos limites definidos;
- verificar se o payout atende aos requisitos mínimos;
- validar a disponibilidade financeira da operação;
- validar os limites de exposição da banca;
- validar a quantidade máxima de contratos simultaneamente ativos;
- produzir uma decisão única, determinística e auditável.

Toda decisão produzida deverá representar o resultado final da avaliação,
cabendo aos componentes consumidores decidir quais ações executar a partir
dessa resposta.

## Limites de responsabilidade

O FixedTimeRiskManager não deverá assumir responsabilidades pertencentes a
outros componentes da arquitetura.

Portanto, este componente não poderá:

- criar contratos;
- alterar o estado de um contrato;
- reservar saldo da banca;
- liberar saldo reservado;
- registrar transações financeiras;
- atualizar indicadores de desempenho;
- publicar eventos;
- acessar banco de dados;
- acessar APIs de corretoras;
- executar operações no mercado;
- modificar qualquer estado global da aplicação.

Essas responsabilidades permanecem distribuídas entre os componentes já
existentes, especialmente o BankrollEngine, o TradeLifecycleCoordinator e os
respectivos handlers.

## Características obrigatórias

A implementação deverá possuir as seguintes características:

- determinística;
- stateless;
- imutável sempre que aplicável;
- independente de infraestrutura;
- orientada ao domínio;
- completamente testável em isolamento.

Para uma mesma requisição e uma mesma política de risco, o resultado produzido
deverá ser sempre o mesmo.

O componente não poderá depender de:

- horário atual;
- variáveis globais;
- estado previamente armazenado;
- acesso à rede;
- banco de dados;
- números aleatórios;
- qualquer fonte externa de informação.

## Resultado esperado

Ao término desta RFC, a arquitetura da AEGIS deverá possuir um mecanismo de
avaliação de risco específico para Contratos de Tempo Fixo, integrado ao fluxo
operacional por meio do RiskHandler e totalmente desacoplado do RiskManager
legado.

Essa implementação estabelecerá a primeira camada de proteção da banca,
garantindo que apenas operações compatíveis com as políticas de risco sejam
encaminhadas para as etapas seguintes do ciclo operacional.

# 5. Escopo

Esta RFC contempla exclusivamente a implementação do mecanismo de avaliação de
risco para o domínio de Contratos de Tempo Fixo.

Seu objetivo é fornecer uma camada especializada responsável por validar todas
as regras de risco antes da criação de um contrato, preservando a separação de
responsabilidades entre os componentes da arquitetura da AEGIS.

O escopo desta RFC compreende a modelagem do domínio, a implementação do novo
motor de risco, sua integração ao fluxo operacional existente e a validação
completa através de testes automatizados.

## Componentes do domínio

Serão implementados os seguintes modelos de domínio:

### FixedTimeRiskPolicy

Representa a política de risco aplicada durante a avaliação das operações.

Será responsável por definir os limites utilizados pelo mecanismo de risco,
incluindo valores mínimos, máximos e percentuais aceitos pela estratégia de
proteção da banca.

### FixedTimeRiskRequest

Representa uma solicitação de avaliação de risco.

Esse objeto conterá todas as informações necessárias para que o motor possa
avaliar uma operação sem depender de qualquer estado interno ou componente
externo.

### FixedTimeRiskDecision

Representa o resultado da avaliação de risco.

O objeto deverá conter informações suficientes para que os componentes
consumidores decidam pela continuidade ou rejeição da operação.

Todos os modelos deverão ser imutáveis e orientados ao domínio.

---

## Serviço de domínio

Será implementado o componente:

```text
FixedTimeRiskManager
```

Esse serviço será responsável exclusivamente pela aplicação das regras de risco
definidas para Contratos de Tempo Fixo.

Sua única responsabilidade será transformar uma requisição de risco em uma
decisão de aprovação ou rejeição.

---

## Integração com a arquitetura

A RFC contempla a integração do novo mecanismo de risco ao fluxo operacional já
existente.

A integração ocorrerá exclusivamente através do:

```text
RiskHandler
```

O TradeLifecycleCoordinator permanecerá responsável apenas pela orquestração do
fluxo de eventos.

Nenhum outro componente deverá depender diretamente do FixedTimeRiskManager.

---

## Estrutura de arquivos

Ao final da implementação deverão existir os seguintes arquivos:

```text
src/
└── risk/
    ├── __init__.py
    ├── exceptions.py
    ├── fixed_time_risk_policy.py
    ├── fixed_time_risk_request.py
    ├── fixed_time_risk_decision.py
    └── fixed_time_risk_manager.py
```

A suíte de testes deverá conter:

```text
tests/
└── risk/
    ├── __init__.py
    ├── test_fixed_time_risk_policy.py
    ├── test_fixed_time_risk_request.py
    ├── test_fixed_time_risk_decision.py
    └── test_fixed_time_risk_manager.py
```

---

## Testes

Esta RFC contempla a implementação de testes automatizados para todos os
componentes desenvolvidos.

Os testes deverão validar:

- criação dos modelos;
- validação das invariantes;
- regras de negócio;
- decisões aprovadas;
- decisões rejeitadas;
- cenários de erro;
- comportamento determinístico;
- integração com o RiskHandler.

Todos os testes existentes na AEGIS deverão permanecer aprovados após a
implementação desta RFC.

---

## Documentação

Ao término da implementação deverão ser atualizados:

- CHANGELOG.md;
- PROJECT_CHECKPOINT.md;
- ROADMAP.md.

A documentação deverá refletir todas as alterações arquiteturais introduzidas
pela RFC-007.

---

## Entregáveis

Ao final desta RFC deverão estar concluídos os seguintes entregáveis:

✓ Modelagem completa do domínio de risco.

✓ Implementação do FixedTimeRiskManager.

✓ Implementação dos modelos FixedTimeRiskPolicy,
FixedTimeRiskRequest e FixedTimeRiskDecision.

✓ Implementação das exceções específicas do domínio.

✓ Integração do RiskHandler com o novo motor de risco.

✓ Cobertura completa por testes automatizados.

✓ Atualização da documentação oficial da AEGIS.

Todos esses itens fazem parte do escopo obrigatório da RFC-007 e deverão estar
concluídos antes da criação da tag correspondente à versão
v0.9.0-alpha.7.

# 6. Fora do Escopo

Esta RFC está restrita à implementação do mecanismo de avaliação de risco para
Contratos de Tempo Fixo.

Qualquer funcionalidade que não esteja diretamente relacionada à análise e à
decisão de risco não faz parte desta entrega e deverá ser tratada em RFCs
específicas.

A exclusão desses itens tem como objetivo preservar a responsabilidade única do
FixedTimeRiskManager e evitar o aumento indevido de complexidade durante sua
implementação.

## Gestão financeira

Esta RFC não contempla alterações no funcionamento do BankrollEngine.

Permanecem fora do escopo:

- reserva de saldo;
- liberação de saldo;
- registro de transações;
- atualização do saldo disponível;
- atualização do patrimônio da banca;
- cálculo financeiro da operação.

Todas essas responsabilidades continuam pertencendo exclusivamente ao
BankrollEngine.

---

## Ciclo de vida dos contratos

Esta RFC não altera o funcionamento do ciclo de vida dos Contratos de Tempo
Fixo.

Não fazem parte desta RFC:

- criação de contratos;
- alteração de estado;
- cancelamento;
- encerramento;
- liquidação;
- publicação de eventos do ciclo de vida.

Essas responsabilidades permanecem sob controle do
TradeLifecycleCoordinator e do FixedTimeContract.

---

## Estratégias operacionais

Esta RFC não implementa qualquer estratégia de negociação.

Permanecem fora do escopo:

- geração de sinais;
- análise técnica;
- indicadores;
- inteligência artificial;
- machine learning;
- seleção de ativos;
- definição de direção CALL/PUT;
- definição automática da stake.

Essas funcionalidades pertencem ao domínio das estratégias de operação e serão
tratadas em RFCs específicas.

---

## Gestão avançada de risco

Esta RFC implementa apenas a política padrão de risco definida para a versão
v0.9.0-alpha.7.

Não fazem parte desta entrega:

- múltiplos perfis de risco;
- políticas dinâmicas;
- políticas configuráveis pelo usuário;
- políticas dependentes da estratégia;
- políticas adaptativas;
- aprendizado automático das regras de risco.

Esses recursos poderão ser incorporados em versões futuras sem necessidade de
alteração da arquitetura estabelecida nesta RFC.

---

## Integrações externas

Esta RFC não contempla integração com componentes externos.

Permanecem fora do escopo:

- APIs de corretoras;
- bancos de dados;
- cache distribuído;
- filas de mensagens;
- serviços em nuvem;
- armazenamento persistente;
- serviços de monitoramento.

O FixedTimeRiskManager deverá permanecer totalmente independente de
infraestrutura.

---

## Interface do usuário

Esta RFC não contempla:

- telas;
- dashboards;
- APIs REST;
- interfaces administrativas;
- configuração manual de políticas;
- visualização de decisões de risco.

Toda interação ocorrerá exclusivamente através dos componentes internos da
arquitetura.

---

## Monitoramento e auditoria

Embora todas as decisões produzidas devam ser determinísticas e auditáveis, esta
RFC não implementa:

- trilhas completas de auditoria;
- histórico persistente de decisões;
- métricas de desempenho;
- telemetria;
- logs estruturados;
- observabilidade.

Esses recursos poderão ser adicionados posteriormente sem modificar o domínio
de risco.

---

## Evoluções futuras

Os seguintes temas ficam oficialmente reservados para RFCs futuras:

- perfis múltiplos de risco;
- gerenciamento dinâmico de exposição;
- políticas por estratégia;
- políticas por corretora;
- limites por ativo;
- limites por horário;
- limites por volatilidade;
- integração com inteligência artificial;
- gerenciamento avançado de capital;
- otimização automática de parâmetros.

Essas funcionalidades não deverão ser incorporadas durante a implementação da
RFC-007.

## Conclusão

Ao limitar explicitamente o escopo desta RFC, garante-se que o
FixedTimeRiskManager permaneça um componente pequeno, previsível, especializado
e totalmente aderente aos princípios da Clean Architecture e do Domain-Driven
Design.

Qualquer expansão funcional deverá ser proposta, discutida e aprovada por meio
de uma nova RFC antes de sua implementação.

# 7. Fluxo Arquitetural

Esta seção descreve o fluxo completo da avaliação de risco dentro da arquitetura
da AEGIS, desde o recebimento da solicitação de abertura de um Contrato de Tempo
Fixo até a devolução da decisão de risco ao coordenador do ciclo de vida.

O objetivo deste fluxo é garantir que nenhuma operação prossiga para as etapas
seguintes sem que todas as regras de risco tenham sido avaliadas pelo
FixedTimeRiskManager.

Todo o processo deverá permanecer determinístico, desacoplado e sem efeitos
colaterais.

---

## Visão Geral

O fluxo arquitetural será composto pelos seguintes componentes:

```text
TradeLifecycleCoordinator
            │
            ▼
      RiskHandler
            │
            ▼
 FixedTimeRiskManager
            │
            ▼
 FixedTimeRiskDecision
            │
            ▼
TradeLifecycleCoordinator
```

O FixedTimeRiskManager permanece isolado do restante da arquitetura,
interagindo apenas através do RiskHandler.

---

## Fluxo detalhado

### Etapa 1 — Recebimento da solicitação

O TradeLifecycleCoordinator inicia o processo de abertura de um Contrato de
Tempo Fixo.

Nesse momento já estarão disponíveis todas as informações necessárias para a
avaliação de risco, incluindo:

- ativo;
- direção (CALL ou PUT);
- valor da stake;
- payout;
- expiração;
- informações da banca;
- quantidade de contratos ativos;
- demais parâmetros necessários.

Essas informações serão encapsuladas em um objeto
FixedTimeRiskRequest.

---

### Etapa 2 — Encaminhamento ao RiskHandler

O TradeLifecycleCoordinator encaminha a requisição ao RiskHandler.

O RiskHandler atua exclusivamente como camada de integração entre o fluxo
operacional e o domínio de risco.

Suas responsabilidades incluem:

- receber a requisição;
- encaminhá-la ao FixedTimeRiskManager;
- devolver a decisão produzida.

O RiskHandler não implementa regras de negócio.

---

### Etapa 3 — Avaliação de risco

O FixedTimeRiskManager recebe:

- FixedTimeRiskRequest;
- FixedTimeRiskPolicy.

Durante essa etapa serão avaliadas todas as regras previstas na política de
risco.

Entre elas:

- valor mínimo da stake;
- valor máximo da stake;
- percentual máximo da banca;
- payout mínimo;
- exposição máxima;
- quantidade máxima de contratos simultâneos.

A ordem das validações deverá ser determinística e reproduzível.

---

### Etapa 4 — Produção da decisão

Concluída a avaliação, o FixedTimeRiskManager produzirá um único objeto
FixedTimeRiskDecision.

A decisão poderá representar:

- operação aprovada;
- operação rejeitada.

Em caso de rejeição, deverão estar disponíveis informações suficientes para que
os componentes consumidores compreendam o motivo da decisão.

O FixedTimeRiskManager encerra sua participação neste ponto.

---

### Etapa 5 — Continuação do fluxo

O TradeLifecycleCoordinator recebe a decisão através do RiskHandler.

A partir desse momento:

- decisões aprovadas permitem a continuidade do fluxo;
- decisões rejeitadas interrompem imediatamente a abertura do contrato.

O coordenador permanece responsável por todas as etapas posteriores da operação.

---

## Diagrama completo

```text
                 ┌─────────────────────────────┐
                 │ TradeLifecycleCoordinator   │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │      RiskHandler            │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │ FixedTimeRiskManager        │
                 ├─────────────────────────────┤
                 │ • valida request            │
                 │ • aplica política           │
                 │ • avalia exposição          │
                 │ • avalia stake              │
                 │ • avalia payout             │
                 │ • produz decisão            │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │ FixedTimeRiskDecision       │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │ TradeLifecycleCoordinator   │
                 └─────────────────────────────┘
```

---

## Garantias arquiteturais

Durante todo o fluxo deverão ser preservadas as seguintes garantias:

- nenhuma alteração financeira será realizada;
- nenhuma operação será enviada à corretora;
- nenhum evento será publicado;
- nenhum estado será modificado;
- nenhuma dependência externa será utilizada;
- nenhuma persistência será executada.

O fluxo representa exclusivamente uma avaliação de risco.

---

## Dependências

O fluxo depende apenas dos seguintes componentes:

- FixedTimeRiskRequest;
- FixedTimeRiskPolicy;
- FixedTimeRiskDecision;
- FixedTimeRiskManager;
- RiskHandler;
- TradeLifecycleCoordinator.

Nenhuma outra dependência arquitetural será introduzida por esta RFC.

---

## Resultado esperado

Ao final do fluxo, toda solicitação de abertura de Contrato de Tempo Fixo terá
passado obrigatoriamente pelo mecanismo especializado de avaliação de risco.

Essa arquitetura garante que apenas operações compatíveis com as políticas
definidas possam prosseguir para as etapas seguintes do ciclo operacional,
mantendo a separação de responsabilidades e a integridade do domínio.

# 8. Princípios Arquiteturais

A implementação do mecanismo de avaliação de risco deverá seguir os princípios
arquiteturais adotados em toda a plataforma AEGIS.

Esses princípios garantem consistência entre os componentes, reduzem o
acoplamento entre módulos e permitem que a arquitetura evolua de forma segura e
previsível ao longo do tempo.

Todas as decisões de implementação desta RFC deverão respeitar os princípios
descritos nesta seção.

---

## Single Responsibility Principle (SRP)

Cada componente deverá possuir uma única responsabilidade claramente definida.

O FixedTimeRiskManager será responsável exclusivamente pela avaliação das regras
de risco.

Todas as demais responsabilidades permanecerão distribuídas entre os
componentes específicos da arquitetura.

Esse princípio reduz o acoplamento e facilita a manutenção do sistema.

---

## Open/Closed Principle (OCP)

O mecanismo de risco deverá permitir evolução por extensão, evitando alterações
na lógica existente sempre que novas políticas ou regras forem introduzidas.

A arquitetura deverá favorecer a inclusão de novos comportamentos sem modificar
o comportamento já validado.

---

## Dependency Inversion Principle (DIP)

Os componentes deverão depender de abstrações do domínio e não de detalhes de
infraestrutura.

O domínio de risco não poderá conhecer:

- APIs externas;
- banco de dados;
- serviços de mensageria;
- componentes de interface;
- bibliotecas específicas de integração.

Essa separação preserva a independência do domínio.

---

## Clean Architecture

A implementação deverá manter a separação entre:

- domínio;
- aplicação;
- infraestrutura.

O domínio de risco deverá permanecer completamente independente das camadas
externas.

As dependências deverão apontar sempre em direção ao domínio.

---

## Domain-Driven Design (DDD)

O domínio de risco será modelado utilizando conceitos próprios do negócio.

Objetos como:

- FixedTimeRiskPolicy;
- FixedTimeRiskRequest;
- FixedTimeRiskDecision;

representam modelos do domínio e deverão refletir a linguagem utilizada pela
arquitetura da AEGIS.

As regras de negócio deverão permanecer concentradas nesses modelos e serviços
de domínio.

---

## Imutabilidade

Sempre que aplicável, os objetos do domínio deverão ser imutáveis.

Após sua criação, não deverão sofrer alterações de estado.

Esse princípio reduz efeitos colaterais, facilita testes e melhora a segurança
da implementação.

---

## Determinismo

Para uma mesma entrada e uma mesma política de risco, o resultado produzido
deverá ser sempre o mesmo.

A avaliação não poderá depender de:

- horário atual;
- números aleatórios;
- variáveis globais;
- estado previamente armazenado;
- serviços externos.

O comportamento deverá ser totalmente previsível e reproduzível.

---

## Alta Coesão

Cada componente deverá concentrar apenas funcionalidades pertencentes ao seu
próprio domínio.

Toda lógica de avaliação de risco deverá permanecer dentro do
FixedTimeRiskManager.

---

## Baixo Acoplamento

O domínio de risco deverá conhecer apenas os elementos estritamente necessários
para executar sua responsabilidade.

Novas funcionalidades deverão ser incorporadas por meio de novos componentes,
evitando dependências cruzadas entre módulos.

---

## Independência de Infraestrutura

O mecanismo de risco deverá funcionar integralmente sem depender de qualquer
tecnologia específica.

Não deverá existir dependência direta de:

- banco de dados;
- cache;
- corretoras;
- APIs REST;
- filas;
- serviços em nuvem.

Isso permitirá que o domínio seja executado em qualquer ambiente sem alterações
na lógica de negócio.

---

## Testabilidade

Todos os componentes deverão ser facilmente testáveis em isolamento.

A implementação deverá permitir:

- testes unitários;
- testes determinísticos;
- testes reproduzíveis;
- validação completa das regras de negócio.

Nenhum teste deverá depender de infraestrutura externa.

---

## Evolução Controlada

Qualquer expansão das responsabilidades do domínio de risco deverá ocorrer por
meio de novas RFCs.

Alterações arquiteturais significativas não deverão ser incorporadas diretamente
durante a implementação desta RFC.

Essa abordagem preserva a rastreabilidade das decisões arquiteturais e mantém a
governança técnica do projeto.

---

## Resultado esperado

Ao seguir esses princípios, o mecanismo de avaliação de risco permanecerá
coeso, desacoplado, previsível e alinhado aos padrões arquiteturais adotados
pela AEGIS, servindo como referência para futuras evoluções do domínio de risco.

# 9. Modelagem

Esta seção descreve a modelagem dos componentes que compõem o domínio de risco
para Contratos de Tempo Fixo.

Todos os modelos apresentados nesta RFC representam conceitos do domínio e
deverão permanecer independentes de infraestrutura, banco de dados,
corretoras, APIs externas e interfaces de usuário.

A modelagem apresentada nesta seção servirá como especificação oficial para a
implementação da versão v0.9.0-alpha.7.

---

# 9.1 FixedTimeRiskPolicy

## Finalidade

Representar a política de risco utilizada durante a avaliação das operações.

Este modelo concentra todos os limites e parâmetros que definem o comportamento
do mecanismo de avaliação de risco.

## Responsabilidades

O FixedTimeRiskPolicy será responsável por definir:

- stake mínima;
- stake máxima;
- percentual máximo da banca;
- payout mínimo;
- exposição máxima permitida;
- quantidade máxima de contratos ativos.

## Características

- Imutável.
- Sem comportamento financeiro.
- Sem dependência de infraestrutura.
- Compartilhável entre múltiplas avaliações.

## Invariantes

Após sua criação:

- nenhum valor poderá ser alterado;
- todos os limites deverão permanecer válidos;
- nenhum campo poderá assumir valores inconsistentes.

---

# 9.2 FixedTimeRiskRequest

## Finalidade

Representar uma solicitação completa de avaliação de risco.

Todos os dados necessários para a análise deverão estar presentes neste objeto.

## Responsabilidades

Conter todas as informações necessárias para que o FixedTimeRiskManager realize
a avaliação sem consultar qualquer outro componente.

## Informações previstas

- ativo;
- direção (CALL ou PUT);
- stake;
- payout;
- saldo disponível;
- patrimônio da banca;
- exposição atual;
- contratos ativos;
- expiração;
- demais informações relevantes.

## Características

- Imutável.
- Autossuficiente.
- Independente de infraestrutura.
- Sem regras de negócio.

---

# 9.3 FixedTimeRiskDecision

## Finalidade

Representar o resultado da avaliação de risco.

Este objeto será o único retorno produzido pelo FixedTimeRiskManager.

## Responsabilidades

Informar de forma objetiva:

- se a operação foi aprovada;
- se foi rejeitada;
- qual o motivo da decisão;
- informações auxiliares para o fluxo operacional.

## Características

- Imutável.
- Determinístico.
- Auditável.
- Independente de infraestrutura.

---

# 9.4 FixedTimeRiskManager

## Finalidade

Executar todas as validações de risco previstas para Contratos de Tempo Fixo.

## Responsabilidades

Receber:

- FixedTimeRiskRequest;
- FixedTimeRiskPolicy.

Produzir:

- FixedTimeRiskDecision.

## Regras

O serviço deverá:

- validar a requisição;
- validar a política;
- aplicar todas as regras de risco;
- produzir uma única decisão.

Não poderá:

- alterar saldo;
- criar contratos;
- publicar eventos;
- acessar banco de dados;
- acessar corretoras;
- modificar estado global.

## Características

- Stateless.
- Determinístico.
- Altamente coeso.
- Baixo acoplamento.
- Totalmente testável.

---

# Relacionamento entre os modelos

```text
FixedTimeRiskRequest
            │
            ▼
FixedTimeRiskManager
            │
            ▼
FixedTimeRiskDecision
            ▲
            │
FixedTimeRiskPolicy
```

A política define os limites.

A requisição fornece os dados da operação.

O gerente de risco aplica as regras.

A decisão representa o resultado da avaliação.

---

# Contratos do domínio

Cada componente deverá possuir um contrato único e bem definido.

| Componente | Entrada | Saída |
|------------|----------|-------|
| FixedTimeRiskPolicy | Configuração | Limites de risco |
| FixedTimeRiskRequest | Dados da operação | Solicitação de avaliação |
| FixedTimeRiskManager | Request + Policy | Decision |
| FixedTimeRiskDecision | Resultado da avaliação | Aprovação ou rejeição |

---

# Invariantes do domínio

Durante toda a execução deverão permanecer verdadeiras as seguintes condições:

- a política não poderá ser modificada;
- a requisição não poderá ser alterada;
- a decisão será imutável;
- o gerente de risco permanecerá stateless;
- nenhuma infraestrutura será acessada;
- nenhuma alteração financeira ocorrerá;
- nenhuma operação será enviada ao mercado.

Essas invariantes representam garantias arquiteturais obrigatórias da RFC-007.

---

# Resultado esperado

Ao final da implementação, o domínio de risco deverá estar completamente
modelado por objetos especializados, coesos e independentes, permitindo que a
lógica de avaliação seja implementada de forma previsível, testável e aderente
aos princípios definidos nesta RFC.

# 10. Implementação

Esta seção define o plano oficial de implementação da RFC-007.

O objetivo é estabelecer uma sequência de desenvolvimento previsível, na qual
cada componente seja implementado somente após a conclusão de todas as suas
dependências diretas.

Essa estratégia reduz o risco de retrabalho, facilita a revisão técnica e
permite validações incrementais durante todo o processo de desenvolvimento.

---

## Estratégia de implementação

A implementação será realizada de forma incremental.

Cada etapa deverá ser concluída, revisada e validada antes do início da etapa
seguinte.

Nenhum componente poderá depender de funcionalidades ainda não implementadas.

---

## Ordem de implementação

A implementação seguirá obrigatoriamente a seguinte sequência:

### Etapa 1 — Estrutura do módulo

Criação da estrutura do novo pacote:

```text
src/
└── risk/
    ├── __init__.py
    ├── exceptions.py
    ├── fixed_time_risk_policy.py
    ├── fixed_time_risk_request.py
    ├── fixed_time_risk_decision.py
    └── fixed_time_risk_manager.py
```

Objetivo:

- estabelecer a organização do domínio;
- preparar a estrutura para os componentes seguintes.

---

### Etapa 2 — Modelos do domínio

Implementação de:

- FixedTimeRiskPolicy;
- FixedTimeRiskRequest;
- FixedTimeRiskDecision.

Cada modelo deverá ser implementado de forma independente, respeitando as
invariantes definidas na Seção 9.

Nenhum modelo poderá depender do FixedTimeRiskManager.

---

### Etapa 3 — Exceções do domínio

Implementação das exceções específicas do mecanismo de risco.

Essas exceções representarão erros de validação e situações inválidas do domínio,
permitindo tratamento consistente pelos componentes consumidores.

---

### Etapa 4 — Serviço de domínio

Implementação do:

```text
FixedTimeRiskManager
```

O serviço deverá utilizar exclusivamente os modelos definidos nesta RFC e aplicar
as regras de risco previstas na política.

Nenhuma dependência de infraestrutura poderá ser introduzida.

---

### Etapa 5 — Integração

Integração do FixedTimeRiskManager ao fluxo operacional por meio do:

```text
RiskHandler
```

O TradeLifecycleCoordinator permanecerá inalterado em sua responsabilidade de
orquestração, recebendo apenas o resultado da avaliação de risco.

---

### Etapa 6 — Validação

Execução da suíte completa de testes automatizados.

Deverão ser executados:

- testes unitários do novo módulo;
- testes de integração;
- regressão da suíte existente.

Nenhuma regressão poderá ser introduzida.

---

### Etapa 7 — Documentação

Atualização dos seguintes documentos:

- CHANGELOG.md;
- PROJECT_CHECKPOINT.md;
- ROADMAP.md.

Toda alteração arquitetural introduzida pela RFC deverá ser registrada.

---

## Dependências entre componentes

A sequência de dependências será:

```text
FixedTimeRiskPolicy
            │
            ▼
FixedTimeRiskRequest
            │
            ▼
FixedTimeRiskDecision
            │
            ▼
FixedTimeRiskManager
            │
            ▼
RiskHandler
            │
            ▼
TradeLifecycleCoordinator
```

Essa ordem evita dependências circulares e mantém a arquitetura desacoplada.

---

## Critérios de revisão

Ao final de cada etapa deverão ser verificados:

- aderência à RFC-007;
- respeito aos princípios arquiteturais;
- ausência de dependências indevidas;
- conformidade com SOLID;
- conformidade com Clean Architecture;
- manutenção da imutabilidade quando aplicável;
- preservação do comportamento determinístico.

Nenhuma etapa será considerada concluída sem revisão técnica.

---

## Compatibilidade durante a implementação

A implementação deverá preservar integralmente os componentes existentes.

Em especial:

- BankrollEngine;
- TradeLifecycleCoordinator;
- FixedTimeContract;
- PortfolioEngine;
- EventBus.

Alterações nesses componentes somente poderão ocorrer quando estritamente
necessárias para integração e sem modificar suas responsabilidades.

---

## Resultado esperado

Ao término desta implementação, a arquitetura da AEGIS deverá possuir um módulo
de risco especializado para Contratos de Tempo Fixo, integrado ao fluxo
operacional, completamente coberto por testes automatizados e compatível com os
componentes já existentes, mantendo os princípios arquiteturais definidos nesta
RFC.

# 11. Testes

Esta seção define a estratégia oficial de validação da RFC-007.

Todos os componentes implementados deverão possuir cobertura por testes
automatizados, garantindo que as regras de negócio, os contratos do domínio e
as decisões arquiteturais permaneçam corretos ao longo da evolução da AEGIS.

A estratégia de testes deverá priorizar previsibilidade, reprodutibilidade e
isolamento.

---

## Objetivos

Os testes desta RFC deverão garantir que:

- todas as regras de risco sejam corretamente avaliadas;
- os modelos do domínio respeitem suas invariantes;
- o comportamento permaneça determinístico;
- nenhuma regressão seja introduzida;
- a integração com a arquitetura existente permaneça compatível.

---

## Testes Unitários

Cada componente deverá possuir uma suíte própria de testes unitários.

Serão implementados testes para:

### FixedTimeRiskPolicy

Validação de:

- criação da política;
- valores mínimos;
- valores máximos;
- percentuais permitidos;
- invariantes;
- imutabilidade.

---

### FixedTimeRiskRequest

Validação de:

- criação da requisição;
- obrigatoriedade dos campos;
- consistência dos dados;
- invariantes;
- imutabilidade.

---

### FixedTimeRiskDecision

Validação de:

- aprovação;
- rejeição;
- motivos da decisão;
- consistência dos resultados;
- imutabilidade.

---

### FixedTimeRiskManager

Validação de:

- stake válida;
- stake mínima;
- stake máxima;
- payout mínimo;
- exposição máxima;
- contratos simultâneos;
- aprovação da operação;
- rejeição da operação;
- comportamento determinístico.

---

## Testes de Contrato

Além dos testes unitários, deverão ser implementados testes de contrato para os
modelos do domínio.

Esses testes verificarão:

- imutabilidade dos objetos;
- contratos públicos das classes;
- tipos de retorno;
- invariantes;
- estabilidade das interfaces.

Alterações futuras que violem esses contratos deverão provocar falha imediata na
suíte de testes.

---

## Testes de Integração

A integração entre os componentes deverá ser validada.

Serão testados:

- comunicação entre RiskHandler e FixedTimeRiskManager;
- propagação da FixedTimeRiskDecision;
- continuidade do fluxo quando aprovado;
- interrupção do fluxo quando rejeitado.

---

## Testes de Regressão

Após a implementação deverão ser executados todos os testes existentes da
plataforma.

A RFC-007 não poderá introduzir regressões.

A suíte atualmente aprovada contém:

- 275 testes automatizados.

Todos deverão continuar aprovados.

---

## Critérios de Qualidade

Todos os testes deverão ser:

- independentes;
- reproduzíveis;
- determinísticos;
- rápidos;
- executáveis em isolamento.

Nenhum teste poderá depender de:

- banco de dados;
- corretoras;
- APIs externas;
- acesso à internet;
- horário atual;
- números aleatórios.

---

## Organização da suíte

A estrutura de testes deverá seguir:

```text
tests/
└── risk/
    ├── __init__.py
    ├── test_fixed_time_risk_policy.py
    ├── test_fixed_time_risk_request.py
    ├── test_fixed_time_risk_decision.py
    └── test_fixed_time_risk_manager.py
```

A organização deverá refletir a estrutura do módulo de produção.

---

## Critérios de Aprovação

A implementação desta RFC somente será considerada concluída quando:

- todos os testes unitários forem aprovados;
- todos os testes de contrato forem aprovados;
- todos os testes de integração forem aprovados;
- toda a suíte existente permanecer aprovada;
- nenhuma regressão for identificada.

---

## Resultado esperado

Ao final da implementação, o domínio de risco deverá possuir uma suíte completa
de testes automatizados capaz de validar regras de negócio, contratos,
integrações e compatibilidade com a arquitetura existente.

Essa suíte passará a representar a principal garantia de estabilidade para as
próximas evoluções do módulo de risco da AEGIS.

# 12. Compatibilidade

Esta seção estabelece os requisitos de compatibilidade da RFC-007 com a
arquitetura existente da AEGIS.

A introdução do módulo de avaliação de risco para Contratos de Tempo Fixo deverá
ocorrer de forma incremental, preservando o funcionamento dos componentes já
implementados e evitando regressões comportamentais.

A implementação desta RFC não deverá alterar responsabilidades previamente
definidas em RFCs anteriores.

---

## Compatibilidade Arquitetural

O novo módulo deverá ser totalmente compatível com a arquitetura atualmente
adotada pela AEGIS.

Deverão ser preservados os princípios de:

- Clean Architecture;
- SOLID;
- Domain-Driven Design;
- Event-Driven Architecture;
- baixo acoplamento;
- alta coesão.

Nenhuma dependência arquitetural existente deverá ser violada.

---

## Compatibilidade com Componentes Existentes

Os seguintes componentes deverão permanecer compatíveis e funcionais após a
implementação da RFC-007:

- EventBus;
- PortfolioEngine;
- BankrollEngine;
- FixedTimeContract;
- TradeLifecycleCoordinator;
- RiskHandler.

O novo mecanismo de risco deverá integrar-se a esses componentes sem alterar
suas responsabilidades originais.

---

## Compatibilidade Funcional

A RFC-007 não deverá modificar:

- regras financeiras do BankrollEngine;
- ciclo de vida dos contratos;
- fluxo de publicação de eventos;
- gerenciamento de portfólio;
- regras de execução de operações;
- lógica de estratégias.

Esses domínios permanecem sob responsabilidade de seus respectivos componentes.

---

## Compatibilidade de Interfaces

As interfaces públicas dos componentes existentes deverão permanecer estáveis.

Sempre que possível, novas funcionalidades deverão ser incorporadas por meio de
novos objetos e novos serviços, evitando alterações incompatíveis nas APIs
internas da plataforma.

Quando uma adaptação for necessária para integração, ela deverá preservar o
comportamento esperado pelos componentes consumidores.

---

## Compatibilidade com Testes

A implementação da RFC-007 deverá manter a aprovação de toda a suíte de testes
existente.

Além disso:

- os novos testes deverão ser adicionados sem substituir os atuais;
- nenhuma cobertura existente poderá ser reduzida;
- regressões deverão ser tratadas antes da conclusão da RFC.

A aprovação dos testes representa a principal evidência de compatibilidade da
implementação.

---

## Compatibilidade Evolutiva

A arquitetura introduzida por esta RFC deverá permitir futuras evoluções sem a
necessidade de reestruturação do domínio de risco.

Entre as evoluções previstas estão:

- múltiplas políticas de risco;
- perfis configuráveis;
- limites específicos por ativo;
- limites específicos por estratégia;
- regras adaptativas;
- novos critérios de avaliação.

Essas funcionalidades deverão ser incorporadas por extensão, preservando a
compatibilidade com a implementação inicial.

---

## Restrições

A RFC-007 não autoriza:

- substituição do BankrollEngine;
- substituição do TradeLifecycleCoordinator;
- alteração das responsabilidades do FixedTimeContract;
- dependência direta de infraestrutura no domínio de risco;
- quebra de contratos públicos existentes.

Qualquer necessidade de alteração estrutural nesses componentes deverá ser
tratada em uma nova RFC.

---

## Resultado esperado

Ao término da implementação, o novo módulo de risco deverá estar plenamente
integrado à arquitetura da AEGIS, preservando a estabilidade dos componentes
existentes e permitindo a evolução futura do domínio sem comprometer a
compatibilidade entre versões.

# 13. Critérios de Aceitação

Esta seção estabelece os critérios objetivos que deverão ser atendidos para que
a RFC-007 seja considerada implementada e concluída.

Nenhuma etapa poderá ser considerada finalizada apenas pela conclusão do código.
Todos os critérios definidos nesta seção deverão ser atendidos e validados.

---

## Critérios Arquiteturais

Deverão estar concluídos:

- implementação completa do módulo `src/risk`;
- aderência integral à modelagem definida nesta RFC;
- preservação dos princípios arquiteturais da AEGIS;
- ausência de dependências indevidas entre domínio e infraestrutura;
- manutenção do baixo acoplamento e da alta coesão.

---

## Critérios Funcionais

O FixedTimeRiskManager deverá ser capaz de:

- receber uma FixedTimeRiskRequest válida;
- aplicar uma FixedTimeRiskPolicy;
- avaliar todas as regras previstas;
- produzir uma FixedTimeRiskDecision determinística;
- rejeitar operações inválidas;
- aprovar operações compatíveis com a política.

Todas as regras previstas nesta RFC deverão estar implementadas.

---

## Critérios Técnicos

Todos os componentes implementados deverão:

- utilizar type hints;
- seguir PEP 8;
- utilizar Decimal para valores financeiros;
- evitar efeitos colaterais;
- permanecer stateless quando aplicável;
- preservar a imutabilidade dos modelos do domínio.

---

## Critérios de Integração

A integração deverá garantir que:

- o RiskHandler utilize o FixedTimeRiskManager;
- o TradeLifecycleCoordinator continue responsável apenas pela orquestração;
- o fluxo operacional permaneça consistente;
- nenhuma responsabilidade seja transferida indevidamente entre componentes.

---

## Critérios de Qualidade

Todos os componentes deverão possuir:

- testes unitários;
- testes de contrato;
- testes de integração;
- validação das invariantes;
- validação do comportamento determinístico.

Não poderão existir falhas conhecidas nos testes implementados.

---

## Critérios de Compatibilidade

Ao término da implementação:

- todos os testes existentes deverão permanecer aprovados;
- nenhuma regressão funcional poderá ser identificada;
- os componentes existentes deverão manter suas responsabilidades originais;
- os contratos públicos existentes deverão permanecer compatíveis.

---

## Critérios de Documentação

Deverão estar atualizados:

- CHANGELOG.md;
- PROJECT_CHECKPOINT.md;
- ROADMAP.md.

Toda decisão arquitetural introduzida nesta RFC deverá estar documentada.

---

## Critérios de Versionamento

Antes da criação da nova tag deverão estar concluídos:

- revisão técnica;
- revisão arquitetural;
- aprovação da suíte de testes;
- atualização da documentação;
- validação final da implementação.

Somente após essas etapas poderá ser criada a versão:

v0.9.0-alpha.7

---

## Checklist de Aceitação

A RFC será considerada concluída somente quando todos os itens abaixo estiverem
marcados como concluídos.

Arquitetura

- [ ] Modelagem implementada
- [ ] Responsabilidades preservadas
- [ ] Princípios arquiteturais respeitados

Implementação

- [ ] FixedTimeRiskPolicy
- [ ] FixedTimeRiskRequest
- [ ] FixedTimeRiskDecision
- [ ] FixedTimeRiskManager
- [ ] Exceptions

Integração

- [ ] RiskHandler integrado
- [ ] Fluxo operacional validado

Qualidade

- [ ] Testes unitários aprovados
- [ ] Testes de contrato aprovados
- [ ] Testes de integração aprovados
- [ ] Testes de regressão aprovados

Documentação

- [ ] CHANGELOG atualizado
- [ ] PROJECT_CHECKPOINT atualizado
- [ ] ROADMAP atualizado

Versionamento

- [ ] Revisão arquitetural concluída
- [ ] Aprovação final da RFC
- [ ] Tag v0.9.0-alpha.7 criada

---

## Resultado esperado

A RFC-007 somente será considerada oficialmente concluída quando todos os
critérios descritos nesta seção forem atendidos, garantindo que a implementação
esteja tecnicamente correta, arquiteturalmente consistente, completamente
testada, documentada e preparada para evolução nas próximas versões da AEGIS.

# 14. Riscos

Esta seção identifica os principais riscos relacionados à implementação da
RFC-007 e define as estratégias adotadas para mitigá-los.

O objetivo é preservar a estabilidade da arquitetura da AEGIS durante a
introdução do novo mecanismo de avaliação de risco.

Todos os riscos aqui descritos deverão ser considerados durante a implementação,
revisão técnica e evolução futura do módulo.

---

## Risco 1 — Acúmulo de responsabilidades

### Descrição

Existe o risco de que o FixedTimeRiskManager passe a concentrar
responsabilidades pertencentes a outros componentes da arquitetura.

Exemplos:

- reserva de saldo;
- criação de contratos;
- publicação de eventos;
- comunicação com corretoras.

### Impacto

- violação do SRP;
- aumento do acoplamento;
- redução da testabilidade;
- crescimento da complexidade.

### Mitigação

Toda nova responsabilidade deverá ser comparada com a Seção 4 (Objetivo) e a
Seção 6 (Fora do Escopo).

Caso não pertença ao domínio de risco, deverá ser implementada em outro
componente ou proposta em uma nova RFC.

---

## Risco 2 — Dependência de infraestrutura

### Descrição

O domínio de risco poderá evoluir incorporando dependências de banco de dados,
APIs externas ou outros serviços.

### Impacto

- quebra da Clean Architecture;
- perda de isolamento;
- testes mais lentos;
- maior dificuldade de manutenção.

### Mitigação

O FixedTimeRiskManager deverá permanecer completamente independente de
infraestrutura.

Toda integração deverá ocorrer por meio das camadas apropriadas da arquitetura.

---

## Risco 3 — Regressões

### Descrição

A introdução do novo módulo poderá provocar regressões em funcionalidades já
existentes.

### Impacto

- falhas em componentes consolidados;
- quebra de comportamento esperado;
- aumento do custo de manutenção.

### Mitigação

Executar integralmente:

- testes unitários;
- testes de integração;
- testes de contrato;
- suíte completa de regressão.

Nenhuma regressão será aceita antes da conclusão da RFC.

---

## Risco 4 — Crescimento descontrolado do escopo

### Descrição

Durante a implementação poderá surgir a tentativa de incluir funcionalidades
não previstas nesta RFC.

Exemplos:

- múltiplas políticas de risco;
- machine learning;
- regras adaptativas;
- configuração dinâmica.

### Impacto

- aumento da complexidade;
- atraso na entrega;
- perda de foco da RFC.

### Mitigação

Toda funcionalidade fora do escopo deverá ser registrada para uma RFC futura.

---

## Risco 5 — Quebra de contratos do domínio

### Descrição

Alterações futuras poderão modificar o comportamento esperado dos modelos do
domínio.

### Impacto

- incompatibilidade entre componentes;
- regressões silenciosas;
- quebra de integrações.

### Mitigação

Manter:

- testes de contrato;
- objetos imutáveis;
- interfaces públicas estáveis.

---

## Risco 6 — Violação do determinismo

### Descrição

O mecanismo de risco poderá passar a depender de informações externas, tornando
o resultado imprevisível.

### Impacto

- decisões inconsistentes;
- dificuldade de reprodução de cenários;
- perda de confiabilidade.

### Mitigação

A avaliação deverá depender exclusivamente de:

- FixedTimeRiskRequest;
- FixedTimeRiskPolicy.

Para uma mesma entrada, o resultado deverá ser sempre o mesmo.

---

## Matriz de Riscos

| Risco | Probabilidade | Impacto | Prioridade |
|--------|---------------|----------|------------|
| Acúmulo de responsabilidades | Média | Alto | Alta |
| Dependência de infraestrutura | Baixa | Alto | Alta |
| Regressões | Média | Alto | Alta |
| Crescimento do escopo | Alta | Médio | Alta |
| Quebra de contratos | Baixa | Alto | Média |
| Violação do determinismo | Baixa | Alto | Alta |

---

## Monitoramento

Durante toda a implementação deverão ser monitorados:

- aderência à arquitetura;
- preservação das responsabilidades;
- estabilidade da suíte de testes;
- compatibilidade entre componentes;
- conformidade com esta RFC.

Sempre que um risco for identificado, a implementação deverá ser interrompida
até que a estratégia de mitigação seja definida.

---

## Resultado esperado

Ao identificar previamente os principais riscos e suas estratégias de
mitigação, a RFC-007 reduz a probabilidade de desvios arquiteturais durante a
implementação e estabelece um processo de evolução mais seguro, previsível e
alinhado aos princípios de engenharia adotados pela AEGIS.

# 15. Decisões Definitivas

Esta seção consolida todas as decisões arquiteturais aprovadas durante a
elaboração da RFC-007.

As decisões aqui registradas passam a fazer parte da arquitetura oficial da
AEGIS e deverão ser consideradas referência durante a implementação, revisão de
código e futuras evoluções do domínio de risco.

Qualquer alteração em uma das decisões abaixo deverá ser proposta e aprovada por
meio de uma nova RFC.

---

## DD-001 — Módulo de risco dedicado

Fica aprovada a criação de um módulo específico para o domínio de risco dos
Contratos de Tempo Fixo.

Estrutura oficial:

```text
src/
└── risk/
    ├── __init__.py
    ├── exceptions.py
    ├── fixed_time_risk_policy.py
    ├── fixed_time_risk_request.py
    ├── fixed_time_risk_decision.py
    └── fixed_time_risk_manager.py
```

O domínio de risco passa a possuir identidade própria dentro da arquitetura da
AEGIS.

---

## DD-002 — Preservação do RiskManager legado

O RiskManager existente não será adaptado para suportar Contratos de Tempo
Fixo.

Ele permanecerá responsável exclusivamente pelo domínio para o qual foi
projetado originalmente.

Essa decisão evita aumento de acoplamento e preserva o princípio da
responsabilidade única.

---

## DD-003 — FixedTimeRiskManager como serviço de domínio

O FixedTimeRiskManager será o único componente responsável pela avaliação das
regras de risco dos Contratos de Tempo Fixo.

Suas responsabilidades incluem:

- validar a requisição;
- aplicar a política de risco;
- produzir uma decisão.

Não será permitido assumir responsabilidades financeiras, operacionais ou de
infraestrutura.

---

## DD-004 — Modelos imutáveis

Os modelos:

- FixedTimeRiskPolicy;
- FixedTimeRiskRequest;
- FixedTimeRiskDecision;

serão implementados como objetos imutáveis.

Após sua criação, não poderão sofrer alteração de estado.

---

## DD-005 — Determinismo obrigatório

Para uma mesma requisição e uma mesma política de risco, o resultado produzido
pelo FixedTimeRiskManager deverá ser sempre idêntico.

Nenhuma dependência externa poderá influenciar a decisão.

---

## DD-006 — Independência de infraestrutura

O domínio de risco permanecerá completamente independente de:

- banco de dados;
- APIs externas;
- corretoras;
- filas;
- cache;
- serviços em nuvem.

Toda integração ocorrerá nas camadas apropriadas da arquitetura.

---

## DD-007 — Integração por meio do RiskHandler

O FixedTimeRiskManager será integrado ao fluxo operacional exclusivamente por
meio do RiskHandler.

Nenhum outro componente deverá depender diretamente do mecanismo de risco.

---

## DD-008 — Evolução por extensão

Novas funcionalidades relacionadas ao domínio de risco deverão ser adicionadas
por extensão, preservando a implementação existente sempre que possível.

Alterações estruturais significativas deverão ser formalizadas em novas RFCs.

---

## DD-009 — Validação obrigatória por testes

Toda implementação deverá ser acompanhada por:

- testes unitários;
- testes de contrato;
- testes de integração;
- testes de regressão.

A aprovação da suíte de testes será requisito obrigatório para conclusão da RFC.

---

## DD-010 — Governança arquitetural

A RFC-007 passa a ser a referência oficial para qualquer evolução do domínio de
risco dos Contratos de Tempo Fixo.

Decisões conflitantes somente poderão ser adotadas após revisão arquitetural e
aprovação formal em uma nova RFC.

---

## Resultado esperado

Com estas decisões formalmente registradas, a arquitetura da AEGIS passa a
dispor de um conjunto estável de diretrizes para o domínio de risco,
assegurando consistência entre implementação, documentação e futuras evoluções
do projeto.

# 16. Próximo Marco

Com a aprovação da RFC-007, o domínio de risco para Contratos de Tempo Fixo
passa a possuir uma especificação arquitetural completa e pronta para
implementação.

O próximo marco do projeto consiste na implementação integral da versão
v0.9.0-alpha.7, seguindo rigorosamente as definições estabelecidas nesta RFC.

---

## Objetivo do próximo marco

Implementar o novo módulo de risco especializado para Contratos de Tempo Fixo,
garantindo aderência total às decisões arquiteturais aprovadas.

O desenvolvimento deverá ocorrer de forma incremental, validando cada etapa
antes do avanço para a seguinte.

---

## Sequência de implementação

A implementação seguirá a seguinte ordem:

### Etapa 1

Estrutura do módulo:

```text
src/risk/
```

---

### Etapa 2

Implementação de:

- FixedTimeRiskPolicy
- FixedTimeRiskRequest
- FixedTimeRiskDecision

---

### Etapa 3

Implementação de:

- exceptions.py

---

### Etapa 4

Implementação de:

- FixedTimeRiskManager

---

### Etapa 5

Integração com:

- RiskHandler

---

### Etapa 6

Implementação dos testes:

- unitários;
- contrato;
- integração;
- regressão.

---

### Etapa 7

Atualização da documentação oficial:

- CHANGELOG.md
- PROJECT_CHECKPOINT.md
- ROADMAP.md

---

### Etapa 8

Execução da suíte completa de testes da plataforma.

Todos os testes existentes deverão permanecer aprovados.

---

### Etapa 9

Revisão arquitetural final.

Será verificado:

- aderência à RFC;
- conformidade com SOLID;
- conformidade com Clean Architecture;
- preservação do baixo acoplamento;
- preservação da alta coesão;
- compatibilidade entre componentes.

---

### Etapa 10

Criação da tag oficial:

```text
v0.9.0-alpha.7
```

Esse marco representa a conclusão oficial da implementação prevista nesta RFC.

---

## Entregáveis do marco

Ao final deste ciclo deverão estar concluídos:

- módulo src/risk;
- modelos do domínio;
- mecanismo de avaliação de risco;
- integração arquitetural;
- suíte completa de testes;
- documentação atualizada;
- versionamento oficial.

---

## Critério para início da próxima RFC

Após a conclusão da v0.9.0-alpha.7, a próxima RFC deverá tratar exclusivamente
de uma nova capacidade arquitetural, preservando integralmente o módulo de risco
implementado nesta versão.

Qualquer evolução deverá ocorrer por extensão e respeitar as decisões
arquiteturais estabelecidas na RFC-007.

---

## Resultado esperado

Ao concluir este marco, a AEGIS passará a possuir um mecanismo de avaliação de
risco especializado, modular, determinístico e totalmente integrado ao fluxo de
Contratos de Tempo Fixo, estabelecendo uma base sólida para futuras evoluções
do domínio de risco.

# 17. Status Final

## Situação da RFC

Após a conclusão das etapas de análise, modelagem e definição arquitetural, a
RFC-007 encontra-se oficialmente aprovada para implementação.

Todas as decisões arquiteturais previstas neste documento foram analisadas,
discutidas e consolidadas antes do início da codificação, reduzindo riscos de
retrabalho e garantindo uma base consistente para a evolução do domínio de
risco da AEGIS.

---

## Escopo aprovado

A RFC-007 aprova oficialmente a implementação de:

- módulo `src/risk`;
- `FixedTimeRiskPolicy`;
- `FixedTimeRiskRequest`;
- `FixedTimeRiskDecision`;
- `FixedTimeRiskManager`;
- exceções específicas do domínio;
- integração com o `RiskHandler`;
- suíte completa de testes automatizados;
- atualização da documentação oficial.

Nenhuma funcionalidade adicional faz parte desta entrega.

---

## Estado arquitetural

Ao término desta RFC, ficam oficialmente estabelecidos os seguintes princípios
para o domínio de risco dos Contratos de Tempo Fixo:

- separação clara de responsabilidades;
- domínio independente de infraestrutura;
- modelos imutáveis;
- comportamento determinístico;
- baixo acoplamento;
- alta coesão;
- evolução por extensão;
- validação obrigatória por testes automatizados.

Esses princípios passam a integrar a arquitetura oficial da AEGIS.

---

## Autorização para implementação

A implementação da versão:

```text
v0.9.0-alpha.7
```

está autorizada, devendo seguir integralmente as definições desta RFC.

Qualquer divergência identificada durante o desenvolvimento deverá ser analisada
e, quando representar alteração arquitetural, formalizada por meio de uma nova
RFC antes da implementação.

---

## Critério de encerramento

A RFC-007 será considerada definitivamente encerrada quando forem concluídos:

- implementação de todos os componentes previstos;
- aprovação da suíte completa de testes;
- atualização da documentação;
- revisão arquitetural final;
- criação da tag `v0.9.0-alpha.7`.

Até esse momento, este documento permanece como a referência oficial para todas
as decisões relacionadas ao domínio de risco.

---

## Registro histórico

A RFC-007 passa a integrar o histórico arquitetural da AEGIS como a RFC
responsável pela introdução do mecanismo especializado de avaliação de risco
para Contratos de Tempo Fixo.

As decisões aqui registradas servirão como base para futuras RFCs que evoluam o
domínio de risco, preservando a rastreabilidade das escolhas arquiteturais ao
longo do ciclo de vida do projeto.

---

## Status

```text
RFC ID:
RFC-007

Título:
Fixed-Time Risk Engine

Versão:
v0.9.0-alpha.7

Situação:
APROVADA

Implementação:
AUTORIZADA

Governança:
ATIVA

Próxima etapa:
Implementação da RFC-007
```

---

## Aprovação Final

Com a conclusão desta RFC, a AEGIS passa a possuir uma especificação completa
para o domínio de risco dos Contratos de Tempo Fixo.

Toda a implementação deverá respeitar as definições arquiteturais, estruturais e
funcionais estabelecidas neste documento, garantindo consistência entre código,
testes, documentação e evolução futura da plataforma.

Esta RFC entra em vigor a partir de sua aprovação e permanecerá como referência
oficial até que uma nova RFC altere explicitamente qualquer uma de suas
decisões.