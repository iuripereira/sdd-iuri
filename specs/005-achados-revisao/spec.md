# Δ 005 — achados-revisao
Estado: proposta · Data: 2026-07-19 · Branch: fix/005-achados-revisao

## Contexto (≤3 linhas)
A revisão do backfill Δ000 (2026-07-19, STATE.md "Decisões em aberto") deixou 3 achados
aprovados pelo usuário: o `adapters.md` não declara fallback para o review estágio 1
(fura o RNF2) e duas imprecisões de redação no TRUTH.md (R13 cenário 2, RNF3 vs R2).

## Mudanças
### R1 — MUDA R13 (Δ004): valor de negócio duplicado entre arquivos é governado por manifesto e validado por script
> Bloco integral; só o cenário 2 muda ("só o TRUTH.md consolidado está no escopo" → o que a
> varredura de fato faz); cenários 1 e 3 repetidos como vigem.

R13 — valor de negócio duplicado entre arquivos é governado por manifesto e validado por script.
- DADO um repo com `deps.toml` QUANDO `validate_integrity.py` roda ENTÃO verifica espelhos em
  sincronia (C1), materialização fora dos sancionados (C2) e links relativos vivos (C3),
  saindo 1 em qualquer violação
- DADO uma delta ainda aberta propondo valor novo QUANDO o validador roda ENTÃO ela não é
  acusada — as deltas abertas (`specs/NNN-*/`) ficam fora dos `scan_globs`; dentro de `specs/`,
  só o `TRUTH.md` consolidado (e `truth/`) entra na varredura
- DADO o `templates/deps.toml` da skill QUANDO um `exclude_globs` mira conteúdo de diretório
  ENTÃO o glob termina em `**/*.md` (nunca em `**` solto), com comentário no template
  explicando o porquê — `pathlib` ≤ 3.12 casa só diretórios num `**` final e o exclude
  viraria no-op

## Requisitos não funcionais
### RNF1 — MUDA RNF2 (Δ000): o ciclo degrada com aviso em vez de abortar
> Métrica mantida; a Verificação passa a exigir o fallback por linha da tabela — é o que
> torna o furo do review estágio 1 detectável. A implementação declara o fallback que falta.

RNF2 — o ciclo degrada com aviso em vez de abortar.
- Métrica: toda fase com motor de terceiro tem fallback nativo declarado
- Verificação: tabela de contrato em `adapters.md` — uma linha por fase, com o ponto sensível a
  breaking change **e uma seção de fallback correspondente para cada motor da linha**

### RNF2 — MUDA RNF3 (Δ000): idempotência defensiva: nada é sobrescrito nem migrado sem pedido
> Métrica reescrita: "no-op" conflitava com o R2 (re-run com `CLAUDE.md` presente grava
> `CLAUDE.generated.md` + diff). Verificação mantida.

RNF3 — idempotência defensiva: nada é sobrescrito nem migrado sem pedido.
- Métrica: 2ª execução de `/sdd-iuri:projeto-init` e `/sdd-iuri:projeto-infra` não altera nenhum
  arquivo versionado e relata o que pulou; artefato de comparação efêmero
  (`CLAUDE.generated.md` + diff, conforme R2) é permitido
- Verificação: rodar duas vezes em repo já inicializado e conferir o relatório

## Fora de escopo
- Mudar o comportamento do `projeto-init` (ex.: só gravar `CLAUDE.generated.md` quando houver
  diff) — o comportamento documentado está correto; o que estava errado era a métrica.
- Fallbacks novos para clarify/plan/implement/estágio 2 — já declarados no `adapters.md`.
- A notação alternativa ao símbolo `Δ` — proposta separada, escopo de outra delta.

## Dependências e riscos
- Os três achados e suas direções de correção foram aprovados pelo usuário em 2026-07-19
  (registro na seção "Decisões em aberto" do STATE.md, removida no archive desta delta).

## Clarify — relatório de ambiguidade (grill-me, modo spec)
<!-- gate do clarify; achados pré-aprovados pelo usuário, direções fixadas na revisão -->
```
Goals:        0.0   ✓ três edições concretas, alvo e texto definidos
Acceptance:   0.0   ✓ cada bloco verificável por leitura/grep
Boundaries:   0.0   ✓ fora de escopo explícito (comportamento do init, notação Δ)
Alternatives: 0.25  ✓ mudar o comportamento do init considerado e rejeitado com porquê
Assumptions:  0.0   ✓ tudo verificado no repo durante a própria revisão
──────────────────────────────
Aggregate:    0.05  ✓ abaixo do limiar (0.2 spec)
```
