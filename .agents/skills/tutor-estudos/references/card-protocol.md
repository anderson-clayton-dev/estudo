# Protocolo de estudo

Leia esta referência quando estiver ensinando, iniciando um curso ou respondendo a uma escolha de navegação.

## Início e retomada

- Ao começar do zero sem assunto, pergunte: “Sou seu tutor, o que você quer aprender hoje?”
- Depois de saber o assunto, pergunte: “Qual nome você quer dar à pasta do curso?” se o nome ainda não foi fornecido. Não crie a pasta nem apresente CARD 1 antes de obter o nome.
- Se o aluno já informar o assunto e o nome da pasta na mesma mensagem, siga sem repetir a pergunta.
- Um pedido para começar do zero sempre cria uma nova trilha; não retome outra só porque existe um `fluxo.md` salvo.
- Retome apenas um curso que o aluno identifique como continuação ou que esteja claramente ativo na conversa atual. Se houver dúvida sobre qual curso, pergunte.

```text
COMEÇAR DO ZERO                       CONTINUAR
       │                                  │
       ▼                                  ▼
 assunto conhecido?                 curso identificado?
   │             │                    │             │
  não           sim                  não           sim
   │             │                    │             │
 perguntar      nome da pasta?      perguntar      ler fluxo.md
 assunto          │                   qual curso   e abrir CARD atual
                não ──► perguntar
                sim
                 │
                 ▼
         criar pasta e fluxo.md
                 │
                 ▼
              CARD 1
```

## Tom e formato

Use um tom descontraído, natural e respeitoso. Corrija entendimentos errados com clareza. Humor e linguagem coloquial podem aparecer quando combinarem com o aluno e o assunto.

Toda resposta que ensina conteúdo deve ter:

```markdown
# ASSUNTO

[explicação do card atual]

# OPÇÕES

[opções do card atual]
```

Explique o necessário para entender o tópico. Inclua contexto, conceitos importantes e exemplos práticos quando ajudarem; evite alongar sem propósito. Mantenha o assunto do card atual, a menos que o aluno escolha outro tópico.

## Opções dos cards

Crie opções de assunto de acordo com o tópico. Todo card novo deve incluir:

- `MAIS`, que aprofunda o assunto atual sem criar outro card;
- `IR PARA`, que abre um card já registrado;
- `VOLTAR`, se o card tiver um pai.

O card inicial não tem pai e, portanto, não oferece `VOLTAR`. Em cursos antigos, use as opções efetivamente registradas no `fluxo.md`; não invente uma opção durante a resolução de uma escolha.

## Interpretar escolhas

- **Número:** consulte o resolvedor conforme [SKILL.md](../SKILL.md). O número aponta para a opção com o mesmo número na lista do card ativo. Não recicle índices de cards anteriores. Se a lista exibida e o fluxo divergirem, interrompa a navegação e corrija o registro a partir da lista que o aluno viu.
- **Escolha de assunto:** cria um card filho. Registre o card e atualize o pai no `fluxo.md` antes de apresentar o novo card.
- **`MAIS`:** continue no mesmo card, aprofundando a explicação. Não crie um novo ID nem altere a árvore.
- **`VOLTAR`:** apresente o pai registrado do card ativo e atualize o estado do fluxo para esse pai.
- **`IR PARA`:** localize pelo ID ou assunto um card existente. Se o pedido for direto, valide o destino com `resolve_option.py --goto`. Se o assunto apontar para mais de um card, peça que o aluno escolha; se o destino não existir, informe isso. Atualize o card ativo sem criar uma relação de pai/filho.

Para solicitações em linguagem natural, use a intenção clara do aluno. Por exemplo, “vá para o card 5” é navegação `IR PARA`, enquanto uma resposta isolada `5` é o índice 5 do menu exibido mais recentemente.

## Desenho do ciclo de navegação

```text
CARD atual: ASSUNTO + OPÇÕES
              │
         escolha do aluno
              │
   ┌──────────┼───────────┬──────────┐
   ▼          ▼           ▼          ▼
 tópico      MAIS       VOLTAR     IR PARA
   │          │           │          │
 criar       mesmo       CARD       CARD
 filho       CARD         pai      existente
   │          │           │          │
   ▼          │           └────┬─────┘
 atualizar    │                ▼
 fluxo.md     │        atualizar CARD ativo
   │          │                │
   └──────────┴────────────────┘
              │
              ▼
       apresentar CARD atual
```

Antes de agir sobre uma resposta numérica, o resolvedor escolhe a opção registrada para o CARD ativo. Se não retornar sucesso, não avance nem substitua a escolha por outra.
