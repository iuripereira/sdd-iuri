# Δ 003 — split-pr-delta
Estado: arquivada · Data: 2026-07-19 · Branch: feat/003-split-pr-delta

## Contexto (≤3 linhas)
2 de 2 deltas estouraram o limiar de PR por causa dos artefatos efêmeros do ciclo (plan.md).
Decisão do usuário (2026-07-19): manter a régua e mudar o processo — split do PR **somente
quando o limiar for excedido**; a régua continua com dono único na regra canônica.

## Mudanças
### R1 — ADICIONA: split condicional do PR da delta
- DADO uma delta com analyze LIBERADO cujo diff acumulado de `specs/NNN-nome/` contra a main
  excede o limiar de PR da regra canônica QUANDO o ciclo segue para o implement ENTÃO os
  artefatos são mergeados antes, num PR próprio de documentação, e a implementação segue em
  PR separado
- DADO uma delta cujos artefatos ficam dentro do limiar QUANDO o ciclo abre o PR ENTÃO um
  único PR carrega artefatos e implementação (comportamento vigente, inalterado)
- DADO o texto do ciclo que descreve o split QUANDO cita o limiar ENTÃO referencia a regra
  canônica dona sem materializar o valor (fonte canônica única; C2 do `deps.toml` vigia)

## Fora de escopo
- Mudar o valor do limiar ou excluir `specs/` da contagem — alternativa renunciada pelo usuário.
- Split da implementação em si — já coberto pela regra vigente "fim de etapa = commit + PR".
- Mecanizar a medição como check novo do `check_cycle.py` — vira pendência em riscos.

## Dependências e riscos
- Depende do limiar de PR governado pelo `deps.toml` (PR #9): dono `canonical-rules.md`.
- Regra manual até ser mecanizada — pode falhar por diligência; mitigação: medição objetiva
  de um comando, no momento fixo do ciclo (fim do analyze).
- [x] Mecanizar a medição do split como check do `check_cycle.py` (com selftest e MUDA no R12
  do TRUTH) quando/se a regra manual falhar numa delta real. <!-- roteada: STATE.md, Decisões em aberto -->
