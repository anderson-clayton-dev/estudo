# Formato e manutenção de `fluxo.md`

Leia esta referência ao retomar, criar ou navegar cards, ou quando for preciso corrigir o histórico de um curso.

## Fonte da navegação

Cada curso tem seu próprio `fluxo.md`. Ele é a fonte de verdade para os IDs, assuntos, relações pai/filho, opções e card ativo. O conteúdo completo das explicações fica na conversa; o fluxo guarda a estrutura de navegação.

Use registros Markdown desta forma:

```markdown
# FLUXO DE APRENDIZADO

## CARD 1

- Assunto: Linux
- Pai: INÍCIO
- Opção de origem: ---
- Filhos: CARD 2

### Opções

1. Dispositivos
2. MAIS
3. IR PARA

## CARD 2

- Assunto: Dispositivos
- Pai: CARD 1
- Opção de origem: Dispositivos
- Filhos: ---

### Opções

1. Discos
2. MAIS
3. IR PARA
4. VOLTAR

## Estado da navegação

- CARD atual: CARD 2
```

## Regras de integridade

- Dê a cada card um ID único no formato `CARD N`. Não renumere nem reutilize IDs existentes.
- Registre assunto, pai, opção de origem, filhos e a lista exata de opções numeradas apresentada ao aluno.
- Em cards novos, inclua `MAIS` e `IR PARA`; inclua `VOLTAR` quando houver um pai.
- Registre o card ativo numa seção única `## Estado da navegação`. Cursos antigos sem esse estado podem ser retomados se o card atual estiver inequívoco na conversa; passe esse ID com `--card`. Depois da próxima atualização, grave o estado no arquivo.
- Uma opção de assunto cria um novo filho. `MAIS`, `VOLTAR` e `IR PARA` não criam filhos.
- Ao criar um filho, atualize primeiro o pai e depois registre o card filho, suas opções e o estado ativo antes de responder.
- Ao voltar ou saltar, atualize o estado ativo. `VOLTAR` usa o pai registrado do card atual. `IR PARA` mantém intactas todas as relações da árvore.
- Preserve os ramos já visitados. Não reconstrua relações ou opções que não estejam no histórico ou na conversa observável.
- Em fluxos antigos, a lista registrada no card atual governa a interpretação dos números. Não altere históricos antigos apenas para acrescentar uma opção nova durante a navegação.

## Ordem de atualização

```text
ESCOLHA DE ASSUNTO
  identificar CARD atual e opção escolhida
  criar ID novo
  atualizar Filhos do pai
  gravar o CARD filho, as opções e o estado atual
  só então apresentar o CARD filho

VOLTAR ou IR PARA
  localizar o destino já registrado
  atualizar Estado da navegação
  só então apresentar o CARD de destino
```

## Resolução mecânica de escolhas

Antes de executar uma escolha numérica, rode o resolvedor em modo somente leitura:

```bash
python3 /absolute/path/to/tutor-estudos/scripts/resolve_option.py /path/to/course/fluxo.md --choice 5
```

O script obtém o card ativo de `## Estado da navegação`, lê as opções daquele card e imprime JSON com a opção e a ação exatas. Se um fluxo legado não tiver card ativo, forneça o ID somente quando a conversa deixar o estado inequívoco:

```bash
python3 /absolute/path/to/tutor-estudos/scripts/resolve_option.py /path/to/course/fluxo.md --choice 5 --card 'CARD 4'
```

Para validar um salto solicitado diretamente:

```bash
python3 /absolute/path/to/tutor-estudos/scripts/resolve_option.py /path/to/course/fluxo.md --goto 'CARD 5'
```

Interprete apenas uma resposta com `ok: true`. Em caso de erro, não adivinhe nem execute a escolha: corrija o estado ou peça a informação que falta.
