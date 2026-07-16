# RFC-001 - Core Engine

## Objetivo

O Core Engine é o núcleo da plataforma AEGIS.

Ele é responsável por coordenar todos os módulos da aplicação sem conter regras específicas de negócio.

---

## Responsabilidades

- Inicializar a aplicação.
- Carregar configurações.
- Gerenciar ciclo de vida dos módulos.
- Publicar eventos.
- Encerrar a aplicação corretamente.

---

## Não é responsabilidade do Core Engine

- Fazer operações de mercado.
- Executar estratégias.
- Salvar dados.
- Fazer chamadas para APIs.

---

## Comunicação

Todos os módulos da AEGIS devem conversar através do Core Engine.

Nenhum módulo pode depender diretamente de outro.

---

## Objetivo futuro

O Core Engine será capaz de iniciar e gerenciar:

- Market Engine
- Memory Engine
- AI Engine
- Vision Engine
- Automation Engine
- Security Engine