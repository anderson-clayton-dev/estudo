# Modelo de aprendizagem

Este documento apresenta o sistema de estudo usado nesta pasta. As instruções operacionais ficam na skill [Tutor de Estudos](.agents/skills/tutor-estudos/SKILL.md), para manter uma fonte única de regras e carregar detalhes apenas quando forem necessários.

## Como funciona

- O ensino é organizado em **cards**: cada resposta de estudo apresenta um `ASSUNTO` e `OPÇÕES`.
- O aluno escolhe novos tópicos, aprofunda o card atual com `MAIS`, volta ao pai com `VOLTAR` ou abre um card já visitado com `IR PARA`.
- Cada curso mantém sua árvore e o card ativo em seu próprio `fluxo.md`.
- A opção numérica é resolvida por um script da skill contra as opções registradas para o card ativo; o agente não deve adivinhar o significado do número.

## Início de um curso

```text
Pedido de estudo
       │
       ├── assunto não informado ──► perguntar o que o aluno quer aprender
       │
       └── assunto informado
                │
                ├── pasta do curso informada ──► criar/usar essa pasta
                │
                └── pasta não informada ───────► perguntar o nome da pasta
                                                    │
                                                    ▼
                                         criar a pasta e o CARD 1
```

Um curso existente só é retomado quando o aluno pedir para continuá-lo ou a conversa atual deixar isso claro. A existência de um `fluxo.md` no diretório não significa, por si só, que o aluno quer retomar aquele curso.

## Navegação dos cards

```text
Escolha do aluno
       │
       ├── tópico ──► criar CARD filho ──► atualizar fluxo.md ──► apresentar card
       ├── MAIS ────► aprofundar o mesmo CARD
       ├── VOLTAR ─► abrir o CARD pai ──► atualizar card ativo
       └── IR PARA ─► abrir CARD existente ─► atualizar card ativo

Número informado ──► resolver_option.py ──► usar a opção registrada do CARD ativo
```

`IR PARA` é um salto na árvore, não um novo ramo. Os detalhes operacionais ficam na skill e em suas referências.

## Arquivos de referência

- [Skill de estudo](.agents/skills/tutor-estudos/SKILL.md): ponto de entrada e regras essenciais do tutor.
- [Protocolo dos cards](.agents/skills/tutor-estudos/references/card-protocol.md): formato das respostas, tom e ações de navegação.
- [Formato do fluxo](.agents/skills/tutor-estudos/references/flow-format.md): estrutura, integridade e atualização de cada `fluxo.md`.
- [Resolvedor de opções](.agents/skills/tutor-estudos/scripts/resolve_option.py): consulta determinística das opções e destinos registrados.
